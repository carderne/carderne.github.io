---
layout: single
title: Leaflet maps with data from Google Sheets
date: '2018-10-19 17:51:19'
excerpt: "I love working with Python, but as soon as you want to put something online, JavaScript's ability to process in the browser is a clear winner. In this post I'm going to go through making a web map in JavaScript that pulls data from Google Sheets – where non-coders can easily make updates."
tags:
- inside
---

*I wrote another [post here](https://rdrn.me/python-mapping-automatic-updating/), outlining how this can be achieved without stepping out of a Python environment.*

I love working with Python, but as soon as you want to put something online, JavaScript's ability to process in the browser is a clear winner. For one, you can have statically served HTML files performing complex tasks, whereas with Python you'd need a cloud instance running and a system for communicating between front- and back-end.

In this post I'm going to go through making a web map in JavaScript that pulls data from Google Sheets – where non-coders can easily make updates. This seems to be a common request and something that is not well covered by the various GUI solutions available. There is a [Data Visualization for All](https://www.datavizforall.org/leaflet/with-google-sheets/) guide, but it didn't seem to work well (potentially due to changes in Google's API) and is overly complex.

*Skip the first two sections if you just want the juicy stuff, or go straight to [the repo](https://github.com/carderne/leaflet-gsheets).*

## Client-side programming
JavaScript is unique in being used on both the client- and server-sides of a web application. This means it can run directly in a user's browser without anything happening on the server, but can also be used on the back-end (via [Node.js](https://nodejs.org/) for moving data around and doing the heavy lifting. For this example, I'm basically taking advantage of the user's computer to do the processing, so that I don't have to pay [Amazon](https://aws.amazon.com/) and friends to do it for me on a cloud instance. This dual nature of JavaScript is one of the reasons for its booming popularity in web development.

## Mapping libraries available in JavaScript
Another reason for JavaScript's ubiquity is the endless variety of libraries available, and the ease with which these can be used, thanks, in part, to  [Atwood's Law](https://blog.codinghorror.com/the-principle-of-least-power/):
> any application that can  be written in JavaScript, will  eventually be written in JavaScript

As for web mapping, there are a few obvious choices:

 * [OpenLayers](https://openlayers.org/) – the most mature and powerful option, but also heavy and quite complex to use
 * [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/tutorial) – limited basemap options and it's closed source (noting the irony that this post is all about Google Sheets)
 * [Mapbox GL JS](https://www.mapbox.com/mapbox-gl-js/api/) (or the older [Mapbox.js](https://www.mapbox.com/help/define-mapbox-js/)) – great for integrating with [Mapbox Studio](https://www.mapbox.com/mapbox-studio/) (designing basemaps) and their [geocoding](https://www.mapbox.com/geocoding/)     service
 * [Leaflet](https://leafletjs.com/) – light-weight, well-documented and easy to use for simple projects – goldilocks!

You can read a more complete [overview here](http://ledeprogram.com/2015/absolutely-everything-you-need-to-know-about-mapping-tools/); it's a bit out of date, but includes comparisons with non JavaScript solutions such as [Carto](https://carto.com/) (not cheap, unfortunately). 

## Pulling data from Google Sheets
*In all the code excerpts, I'm stripping it to the bare essentials for readability. The full code is available at the [repo](https://github.com/carderne/leaflet-gsheets).*

To make maps from Google Sheets, we first need to get data from Google Sheets. This is made exceedingly easy by [Tabletop.js](https://github.com/jsoma/tabletop), a simple library for pulling in entire sheets as JSON objects. This is done in a few lines of code:

```
function init() {
    Tabletop.init({
        key: sheetsUrl,
        callback: myFunction,
        simpleSheet: true
    })
}

window.addEventListener('DOMContentLoaded', init)

function myFunction(data, tabletop) {
    console.log(data);
}
```

You just need to get the public sharing link from your Sheet (follow the instructions at the Tabletop.js repo) and assign it to `sheetsUrl` and you're done! 

The data I pulled in for this web map was two separate tables, which you can preview [here](https://docs.google.com/spreadsheets/d/1WyZNokrgj5NmbyYrRIOQDa2mZ0_SEdbjBohR2RmKXp8/edit?usp=sharing) and [here](https://docs.google.com/spreadsheets/d/1p9pdXDgaLLVFj1agny5m1Y5gHSeRYJP-K0hrENLkfJo/edit?usp=sharing). The first has simple `lat` and `long` coordinates for a few points, while the second has a more complicated `geometry` column with polygon representations of each US state. In addition they each have extra columns with more information.

## Putting it together for an easy web map
My objective for this web map was to show these point and polygon items on a map of the US, with pop-ups for each element showing additional information. With a few more steps, it's easy to style each element based on other columns in the data.

Firstly, let's create a basic HTML file to hold our map. The example below provides the bare minimum of importing Tabletop.js, Leaflet.js and the Leaflet CSS styling. It then creates a `div` with `id="map"`, which is where our map will go, and then imports `leaflet-example.js`, which is where our new JavaScript code goes.

```
<!DOCTYPE html>
<html>
<head>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/tabletop.js/1.5.1/tabletop.min.js'></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.3.4/dist/leaflet.js"></script>
</head>
<body>
    <div id="map"></div>
    <script type="text/javascript" src="leaflet-example.js"></script>
</body>
</html>
```

With that set up, let's create a Leaflet map and insert it into our `div`, and add a beautiful basemap (basically a background map). A number of basemap options are demoed here [http://leaflet-extras.github.io/leaflet-providers/preview/] – just copy the provided URL into `baseMapURL` in the code below (and add the suggested attributions).

```
var map = L.map('map-div').setView([startLat, startLong], startZoom);
var basemap = L.tileLayer(baseMapURL, {
	attribution: attributionText
});
basemap.addTo(map);
```

Next we need to add things to the map! The points are easier, and we can add them by simply looping through each item in the JSON and adding a Leaflet `marker`. This function is called by the init()  function from further up, once the data has been retrieved from Google Sheets.

```
function addPoints(data, tabletop) {
    for (var row in data) {
    	var marker = L.marker([
            data[row].lat,
            data[row].long
        ]).addTo(map);
      	marker.bindPopup(data[row].category);
    }
}
```

The polygons are slightly more complicated, as Leaflet needs a GeoJSON  object to represent them. So in a new function like the previous one (also called by the `init()` function), we have the following code to create a single GeoJSON containing all of our polygons.

```
function addPolygons(data, tabletop) {
    // the empty GeoJSON waiting to be populated with features
    var polygons = {
        "type": "FeatureCollection",
        "features": []
    }

    for (var row in data) {
        // JSON.parse converts the geometry strings into JSON objects
        var coords = JSON.parse(data[row].geometry);

        polygons.features.push({
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": coords
            },
            "properties": {
                "name": data[row].name,
            }
        });
    }
}
```

This sets up an empty GeoJSON and then loops through each element in `data` and inserts the coordinates and names as `Feature` elements within the GeoJSON. With this set up, it's just a few lines to add this new object to our Leaflet map. The lines below can be added at the bottom of the `addPolygon` function for simplicity.

```
polygonMarkers = L.geoJSON(polygons, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup(feature.properties.name);
    },
}).addTo(map);
```

As for the points further up, this includes the code to add a popup, but nothing on styling. That's probably a post for another day, but you can have a look at the [repo](https://github.com/carderne/leaflet-gsheets) if you want to see what I used for this example.

And we're done! The result (with styling) is shown below, or click [here](https://rdrn.me/leaflet-gsheets/leaflet-gsheets.html) to see it full screen. Every time a user loads this map in their browser, it will automatically hop over to the specified Google Sheets and pull the latest data to display it.

<iframe src="/assets/html/leaflet-gsheets-nosidebar.html" style="width: 100%; height: 600px" name="internal" frameborder="0"></iframe>