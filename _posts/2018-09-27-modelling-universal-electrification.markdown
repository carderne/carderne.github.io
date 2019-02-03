---
layout: single
title: Modelling the optimum way to achieve universal electrification
date: '2018-09-27 13:22:00'
excerpt: "Building on the algorithms I developed for mini-grids, I decided to move up a level of abstraction and look at the country- rather than village-level. What follows is the outline of a model that use population and other input data, and techno-economic parameters, to develop a nationally optimised pathway to achieving universal electrification per the UN’s Sustainable Development Goal 7."
tags:
- inside
---

Building on the algorithms I developed for [mini-grids](https://rdrn.me/flask-optimize-minigrid/), I decided to move up a level of abstraction and look at the country- rather than village-level. What follows is the outline of a model that use population and other input data, and techno-economic parameters, to develop a nationally optimised pathway to achieving universal electrification per the UN's [Sustainable Development Goal 7](https://sustainabledevelopment.un.org/sdg7).

If you're more interested in seeing the code, skip over to the [electrification-planner](https://github.com/carderne/electrification-planner) repository on GitHub.

## Clustering population into settlements
Most GIS data on human populations, such as the [GHSL](https://ghsl.jrc.ec.europa.eu/) that I'm using in this example, comes in raster format. For example, the population around Kampala, Uganda looks like this. Each pixel represents a grid cell of 250 x 250 metres, and I've shown inhere with darker = more people.

![Population][uni1]

This is extremely useful, and allows for many types of analysis, but isn't inherently useful for planning an electrical grid – the government of Uganda doesn't decide where to build infrastructure on a pixel-by-pixel basis.

Thus the first step of this model is to transform this population data into something more useful for our purposes, by combining nearby pixels into population 'clusters', which we hope will approximate settlements such as villages, towns and cities. For this process, I'm going to lean heavily on [rasterio](https://github.com/mapbox/rasterio) for raster processing, and [GeoPandas](http://geopandas.org/) for managing vectors.

So the first thing we do is read in the population layer and mask it to our area of interest. In this case, the GHSL data is global but we only want to focus on Uganda.

```
import rasterio
import geopandas as gpd
import json

pop = rasterio.open(pop_raster)

adm = gpd.read_file(admin_boundary)
adm = adm.to_crs(crs=pop.crs)
coords = [json.loads(adm.to_json())['features'][0]['geometry']]

pop_masked, pop_affine = mask(dataset=ghs, shapes=coords, crop=True)
```

Then we can use rasterio's shapes  module to convert the clipped rastero into aset of polygons. This just converts each pixel into a vector square.

```
pop_geoms = list(({'properties': {'raster_val': v}, 'geometry': s} 
              for i, (s, v)
              in enumerate(shapes(pop_masked, mask=None, transform=pop_affine))))

pop_poly = gpd.GeoDataFrame.from_features(pop_geoms)
pop_poly.crs = pop.crs.data
```

Then we filter out polygons that are more than fives times average, as these are probably artefacts, and remove all polygons with below a cut-off population, so that we focus on actual villages and towns. Finally, we buffer each polygon out by 150 metres so that neighbouring polygons will overlap.

```
pop_poly['area_m2'] = pop_poly.geometry.area
pop_poly = pop_poly[pop_poly['area_m2'] < pop_poly['area_m2'].mean() * 5]
pop_poly = pop_poly[pop_poly['raster_val'] > 50]

pop_poly['geometry'] = pop_poly.geometry.buffer(150)
```

Then we use the GeoPandas dissolve  and explode  modules to merge these touching polygons into single polygons. After all these steps, we get the following,where each separate polygon is assigned a random colour. As you can see, Kampala (turquoise) and Jinja (in pink, another large Ugandan town) have become sprawling, unwieldy polygons that aren't ideal for simple modelling. However,big cities are not really our goal here – hopefully in most cases they already have electricity connections.

![Clusters][uni2]

There is one final step to make these clusters a bit more useful. We want to know how many people are in each cluster, and how far they are from existing electricity grid infrastructure. For the grid distances, we need to read in our grid file, and convert it to a raster. In the section below, the red vectorl ines are transformed into the black raster data, with 250 x 250 metres grid cells as in our population data.

![Distance][uni3]

An important thing to remember at this point is that a raster is just a 2-dimensional array, plus geospatial information. Thus, we can use [SciPy](https://www.scipy.org/) and the [Euclidean distance transform](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.ndimage.morphology.distance_transform_edt.html) to calculate the distance from every point in a raster to preset points of interest, which in this case is the black electricity grid in the image above.These distances are shown above, with bluer cells meaning further distances.

With this done, we use a neat little library called [rasterstats](https://github.com/perrygeo/python-rasterstats), which creates summary statistics of rasters based on vector geometries. We use this to get the *minimum*  distance a cluster is from any grid infrastructure. We do the same for population, but take the *sum*, as we want to know the total population hiding under each cluster.

```
grid = gpd.read_file(grid_file)
grid = grid.to_crs(crs=pop_poly.crs)

grid_raster = rasterize(grid.geometry, out_shape=pop_masked[0].shape, fill=1, default_value=0, all_touched=True, transform=pop_affine)
dist_raster = ndimage.distance_transform_edt(grid_raster)

dists = zonal_stats(vectors=pop_poly, raster=dist_raster, affine=pop_affine, stats='min', nodata=1000)
pop_poly['grid_dist'] = [x['min'] for x in dists]

pop_sums = zonal_stats(pop_poly, pop, stats='sum')
pop_poly['pop'] = [x['sum'] for x in pop_sums]
```

Finally we get the following result, where all clusters within 1 km of the gridh ave been excluded. The remaining villages are coloured by population, with higher populations being more blue.

![Exclude][uni4]

## Choosing the optimum technology for each cluster
Now that we have a sensible representation of settlements, along with their populations and distance from infrastructure, we can start to look at how best to provide each settlement with electricity. In reality, there are a number of things we'd additionally need to do: estimate demand based on various economic factors, consider resource availability such as solar radiation, exclude areas that are too high/steep/sensitive for whatever technology to be used. For nowI'm simplifying things so we can focus on the core modelling process.

Similar to the [process I described for mini-grids](https://rdrn.me/flask-optimize-minigrid/), we take these grid lines and clusters and from them create a [network](https://en.wikipedia.org/wiki/Network_theory), where each line and each cluster is aware of who its neighbours are. The difference is that mini-grids are a greenfield with no existing grid lines, whereas Uganda already has several thousand km of grid lines. As above, we take these into account by specifying that every village within 1 km of grid lines is already electrified. However, as Uganda has an urban electricity access rate of [around 60%](https://data.worldbank.org/indicator/EG.ELC.ACCS.UR.ZS), only that portion of each cluster actually has electricity coming into their houses.

Then the primary question is this: for each cluster, is it more economical to connect with on-grid or off-grid technology. First we calculate for each cluster what it would cost to connect with off-grid technology. In reality this should consider a range of possibilities, including solar-home systems, solar mini-grids, diesel hybrids and others, to see which can most affordably serve a particular community.

For this proof-of-concept, I'm simply calculating the off-grid cost as follows:

 * *cost = demand × generator-cost + area × wiring-cost*

where demand is estimated simply estimated by the population, and the wiring cost is an estimate of how much electrical wire is needed depending on the size of the village. For this example, I've used a demand of 6 kWh/person/month(corresponding to Tier 2 from the World Bank's [Multi-Tier Framework](https://www.esmap.org/node/55526), 4000 USD/kW for generators and 2 USD/m2 for wiring.

With this done, we're ready to start looking into grid extensions, and each time the algorithm finds a potential candidate, it can compare to the already-calculate off-grid cost to see if grid is more suitable. I'm using50,000 USD/km for grid wiring and the same in-village costs as above for low-voltage wiring.

We start off with a [minimum spanning tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree) connecting all the electrified villages (those that already have electricity access) to all of the remaining villages with the least total amount of wire. However, it gets complicated: the spanning tree doesn't know about the existing grid lines, so it can create multiple paths to the same village.

Consider the image below, which was produced by the final output from the model.Already connected villages in green, new connections in blue and off-grid villages in red. The existing grid is dark grey, new grid lines purple, while the yellow dashed lines represent lines from the spanning tree that the model rejected. The two villages on the left circle in blue could have been connected by the yellow line, but the model found that the bottom one was more cheaply connected by its southern neighbour, while the top one was cheaply connected by its eastern neighbour.

The two red off-grid villages were locations where the population was too low, or the grid distance too far, for grid connection to be feasible. So these yellow lines should not be constructed, and some kind of solar solution should instead be used.

![Algo][uni5]

To achieve this heuristic of finding the best connections to keep and which to toss, the model begins as follows (in pseudo-code). This only enables those network arcs that don't connect already electrified villages – as they already have grid lines connecting them.

```
for village in unelectrified_villages:
    for arc in connected_arcs:
        arc ← enabled
```

Then we're ready to loop through all electrified villages, and look in their neighbourhood to see if there are any nearby un-electrified villages that they can extend grid lines to. Each time, it calls the connect_neighbours()  function (described below) and if the results are better than the mini-grid costs we calculated, it keeps them. Before making the changes permanent, it compares any duplicates and keeps the cheapest one – this is how the decision is made for the two circled villages in the image above.

```
while True:
    for village in electrified_villages:
        for arc in connected_arcs:
            if arc is enabled:
                new ← connect_neighbours(village, arc)
                
                if new.cost < mini_grid_cost:
                    connect ← new
                    
    if len(connect) > 0:
        if duplicates:
            keep lowest cost
            
        for village, arc in connect:
            village ← electrified
            arc ← electrified
    else:
        break
```

Finally, let's look at the most important part, the connect_neighbours()  function. This starts at the given village and branches outwards looking for the most affordable way to connect nearby villages. This type of tree search is best achieved with a [recursive function](https://en.wikipedia.org/wiki/Recursion_(computer_science)) – note the functions calls itself on the second-last line.

At any moment, the function is tracking two configurations that it has found: the current  one that it is looking at, and the best  one it has found so far. At any point if the current is cheaper than the best it has found, the best is replaced. It then takes advantage of a very useful property of recursive functions: the ability to pass some data in both directions, and some in only one direction. Note that both current  and best  are passed to the function call, while only best  is returned at the end. This means that the algorithm is free to explore side-paths to its heart's content, but if no better solution is found, the main search is not bothered by the current  solution found on that side tree. However, a new best  solution will be returned to the main branch.

```
def connect_neighbours(village, arc, best, current):
    if node not electrified:
        current.arcs ← current + arc
        current.villages ← current + village

        if current.cost() < best.cost():
            best ← current

        for arc in connected_arcs:
            if arc is enabled and arc not electrified:
                best ← conect_neighbours(village, arc, best, current)  
    return best
```

For this example, the while  loop from two blocks up ran eight times, and found a total of 2,686 new villages to connect, with a remaining 263 that were deemed cheaper to connect with off-grid technology. The final results are shown in the image below, following the same colour scheme as before.

 ![Result][uni6]

Let's do a quick sanity check of these results. The current population of Uganda is around 43 million, of whom [about 30%](https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS) have access to electricity, or 13 million people. According to my heuristic that any cluster within 1 km of the grid has electricity access, and of these 60% have electricity in their house, the number is 15 million people, so not too far from the official measurements. What about the remaining 40% of urban people that aren't considered by this model? Most likely the government should be focusing on [grid densification](https://endev.info/content/Grid_Densification_Challenge_Fund) – providing electricity to those already in sight of the grid.

There are 12 million people in the 2,686 new villages to connect, and hopefully more than 60% of these would get electricity access if the grid arrives. There are a further 230,000 people in the 263 off-grid villages, where a mini-grid solar PV system is probably best. According to the model, the combined cost to connect these people to the grid USD 4.5 billion – but note that this is based on extremely rough guesses of infrastructure costs.

Finally, what about the people that were left out when we created the clusters? That process ignored 4 million people (about 9%) from the least densely populated parts of Uganda, who are potentially the most in need of public support. It's difficult to model how best to include this group if they are very rural, dispersed populations, it's probably to safe to say that the quickest and cheapest would be to for them to use solar-home systems, such as solar lanterns and individual roof-mounted solar panels.

You can view a static version of the entire Python notebook [here](http://nbviewer.jupyter.org/github/carderne/electrification-planner/blob/master/electrify.ipynb), or visit the [GitHub repo](https://github.com/carderne/electrification-planner) to see the entire package.

[uni1]: /assets/images/2018/uni1.png
[uni2]: /assets/images/2018/uni2.png
[uni3]: /assets/images/2018/uni3.png
[uni4]: /assets/images/2018/uni4.png
[uni5]: /assets/images/2018/uni5.png
[uni6]: /assets/images/2018/uni6.png