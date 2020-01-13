---
layout: single
title: A workflow for Python mapping with automatic updating
date: '2018-06-20 06:47:00'
excerpt: "A friend needed a map of the US displayed with points at specific locations with attached information, and overviews for certain states with summaries. And for this to be done (and updated) as easily as possible by people with no coding knowledge."
tags:
- inside
---

*This is intended as a workflow for a Python application focused on modelling and mapping. For a much simpler solution to produce dynamic maps from Google Sheets data using JavaScript, see my [other post here](https://rdrn.me/leaflet-maps-google-sheets/).*

A friend needed a map of the US displayed with points at specific locations with attached information, and overviews for certain states with summaries. And for this to be done (and updated) as easily as possible by people with no coding knowledge. Their solution was [Google My Maps](https://www.google.com/mymaps),which was probably more than adequate for what they're trying to achieve.

So (mostly for the fun of it) I decided to see if I could help out, using Folium and some simple tables. My first proposal ("just run this Jupyter notebook and embed the output") didn't go over well. So I decided to explore how to make it as simple as possible, and this is what I came up with.

{% include image.html url="/assets/images/2018/py1.png" description="I highly recommend draw.io for this type of stuff." %}

Firstly there are two Google Sheets with a simple format. The [first](https://docs.google.com/spreadsheets/d/1WyZNokrgj5NmbyYrRIOQDa2mZ0_SEdbjBohR2RmKXp8/edit?usp=sharing) contains specific point data with coordinates in decimal degrees, and the [second](https://docs.google.com/spreadsheets/d/15t8dZIab3cNoN3y3WVYVy4a-RITFhfvlPWIKSKAuV0Y/edit?usp=sharing) contains summary state-level data with polygon representations of each state.These are then shared with anyone who might need access to updating the map data.

Then the Python package [gspread](https://github.com/burnash/gspread) makes it extremely easy to pull this data using OAuth2. It has great instructions on how to set up a Google API key and access specific sheets. It's only a few lines of code to pull the data and convert into a [panda](https://pandas.pydata.org/) DataFrame.

```
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'google-api-key.json', scope)
gc = gspread.authorize(credentials)

wks = gc.open("sheet").sheet1  # sheet is the name of the Google Sheet
wks_vals = wks.get_all_values()
df = pd.DataFrame(wks_vals[1:], columns=wks_vals[0])
```

And then a few more to convert this into a [GeoPandas](http://geopandas.org/) GeoDataFrame, which extends pandas with a geometry  attribute and provides easy access to the geospatial packages [Shapely](http://toblerity.org/shapely/) and [Fiona](http://toblerity.org/fiona/). More importantly, they play nicely with Folium, my preferred shortcut to easy JavaScript web-maps.

```
import geopandas as gpd
from shapely.geometry import Point

df = df.astype({'X': int, 'Y':int})
geo = [Point(xy) for xy in zip(laws['Y'], laws['X'])]
gdf = gpd.GeoDataFrame(df, crs={'init':'epsg:4326'}, geometry=geo)
```

With a similar process for the other Sheet, it is a simple process to create a basic map based on this GeoDataFrame. Please have a look at my [repo here](https://github.com/carderne/web-mapping/tree/master/folium-gspread) for the complete code and output.

```
import folium

m = folium.Map([40, -100], zoom_start=5)
c = folium.GeoJson(gdf)     
c.add_to(m)  
m.save('map.html')
```

The final step is to make this all happen in a predictable way that doesn't force anyone to get their hands covered in code, who doesn't particularly want to. So we set this code up on a Google Compute instance and have it output theresults as an embeddable html file. To avoid dealing with servers and firewalls,I cloned into a new [GitHub repo](https://github.com/carderne/web-mapping/tree/master/folium-gspread) and set up a cron-job to run the following script every hour.

cron entry:

```
0 * * * * /home/username/update_map.sh
```

update_map.sh:

```
python enviro_map.py
git add .
git commit -m "Hourly map update"
git pull --no-edit
git push
```

This pushes the updated html file to the repo, where my so-called clients can easily [access it](https://github.com/carderne/leaflet-gsheets) to embed in their website. Then all they have to do to update their website is edit the Google Sheets and wait for the new results to appear embedded in their website.

<iframe src="/assets/html/leaflet-gsheets-nosidebar.html" style="width: 100%; height: 600px" name="internal" frameborder="0"></iframe>
