---
layout: single
title: Modelling hydrological networks at massive scale
date: '2017-04-15 13:26:00'
excerpt: "Ironically, a large part of my work at KTH's Division of Energy Systems Analysis was modelling complex hydrological systems. I set out to create a model that would conduct massive scale hydrological modelling."
tags:
- inside
---

Ironically, a large part of my work at KTH's Division of [Energy Systems Analysis](https://www.kth.se/en/itm/inst/energiteknik/forskning/desa/welcome-to-the-unit-of-energy-systems-analysis-kth-desa-1.197296) was modelling complex hydrological systems. Often, this was while modelling the 'nexus' between different systems, such as energy, water and climate – as opposed to treating these as separate fields of study.

A lot of this was done in [WEAP](https://www.weap21.org/index.asp?NewLang=EN), a hydrological modelling package courtesy of the [Stockholm Environmental Institute](https://www.sei.org/).  This provided an easy user interface, and access to a variety of complex models and systems for things such as rainwater run-off and crop requirements. However, it isn't easily scriptable, and is mostly suited to very localised systems.

So when my colleagues and I wanted to conduct a continent-scale assessment of mini-hydropower potential, we had to turn elsewhere. For the first version of this, I created a simple script to run down every river in a given network and calculate the elevation drop (head) between points to estimate hydropower potential. We applied this to the whole of Sub-Saharan Africa, using river networks from [HydroSHEDS](http://www.hydrosheds.org/) and run-off data from the EU's [Joint Research Centre](https://data.jrc.ec.europa.eu/collection/water).

Update: The paper we wrote on this has recently been published with the journal Energies: [A Geospatial Assessment of Small-Scale Hydropower Potential in Sub-Saharan Africa](https://www.mdpi.com/1996-1073/11/11/3100).

Later on, I decided to improve and generalise this simple model and came with an unwieldy bit of code called [hydro-networks](https://github.com/carderne/hydro-networks). Instead of just creating points all over the show, I set out to create a model that would:

 * Conduct massive scale hydrological modelling
 * Calculate run-off and stream-flow using precipitation and land-use data
 * Model rivers in a network-aware manner
 * Allow point sources/drains such as farms and dams to be added procedurally

At a rough estimate, I achieved about 3/4 of this, and realised run-off modelling is damn hard. What I did manage was still pretty fun, so I'm going to go over an example below, in the hopes that one day I'll pick this up again and complete it.

## Create direction-aware river networks
The model uses the wonderful [GeoPandas](http://geopandas.org/) library to read in the river network data from [HydroSHEDS](http://www.hydrosheds.org/). It is very happy crunching the data for the whole African continent, but to make this easier, I've clipped out a small river called Dieprivier  just outside Cape Town(yes, they exist).

![Dieprivier][hydro1]

If we zoom into a small section, we see the the model-generated layer (purple)matches pretty well with the painstakingly traced data (light blue) fromOpenStreetMap.

![Section][hydro2]

The model then goes through a couple of steps to convert this GIS data into something we can use for modelling.

 1. Go through every river segment in the input data, and create for it a separate arc, which altogether form the network data structure.
 2. As it does this, create another data structure called nodes that contains all of these points where arcs meet or terminate.
 3. Then tell every arc  which two nodes it is connected to, and tell each node which arcs it is connected to. This means if we know a node location, we know which arcs connect to it, and therefore which other nodes are connected, and so on.

A small section of the resulting layers is shown below, with the nodes at the intersections of river arcs. The large green node knows which arcs are connected to it (also in green) and they in turn know about it.

![Nodes][hydro3]

## Giving the network some order
This is all very well, but it's still just a bunch of lines and dots. To make this network a lot easier to use, we must assign [stream order](https://en.wikipedia.org/wiki/Stream_order) to the arcs – essentially indicating how many upstream branches they have. This is a useful proxy for how 'big' any part of a river is relative to the network, but also allows the model to easily orientate itself to what is up- and down-stream of any node.

There are two main approaches to this, the [Strahler number](https://en.wikipedia.org/wiki/Strahler_number) and the Shreve number. For the Strahler number, the smallest tributaries are assigned an order of 1. These are then followed down, and when two 1's join, they form a 2. If two streams with a different number join, it gets the higher of the two, i.e. 1+2=2. The Shreve number is similar, except the numbers always add, so 1+2=3! For this model, I used the Shreve number, as it ensures that a downstream section always has a higher number that the sections upstream of it.

To achieve this, I adapted the algorithm from [this paper](https://doi.org/10.1111/j.1752-1688.2004.tb01057.x) (Gleyzer, et al., 2007), a beautiful but not very intuitive recursive function. Basically, it starts at the mouth of a given river (identified by a separate bit of code) and then follows recursively up the network until it reaches the mountain-top tributaries. Then it trickles back down to the mouth, adding up the stream orders as it goes.

```
def shreve(arc_index, direction_node_id, network, nodes):
    up_stream_orders = []
    if len(nodes[direction_node_id]) == 5:
        network[arc_index][7] = 1
    else:
        for index, arc in enumerate(nodes[direction_node_id]):
            if index >= 4:
                if network[arc][0] != arc_index:
                    if network[arc][5] != direction_node_id:
                        up_stream_orders.append(shreve(arc,
                            network[arc][5], network, nodes))
                    else:
                        up_stream_orders.append(shreve(arc,
                            network[arc][6], network, nodes))
        max_orders = heapq.nlargest(2, up_stream_orders)
        if len(max_orders) == 2:
            order = 0 + max_orders[0] + max_orders[1]
        else:
            order = 0 + max(up_stream_orders)

        network[arc_index][7] = order
    return network[arc_index][7]
```

Applied to the entire river network, it looks something like this.

![Stream order][hydro4]

## Adding data layers and doing things
Now that we have the network set up and ordered, it's time to do something with it! In addition to the run-off data mentioned further up, there are a few other important layers:

 * Digital elevation model (DEM), normally from NASA's [SRTM ](https://www2.jpl.nasa.gov/srtm/)
 * Flow accumulation, which is derived from the DEM and also available at [HydroSHEDS](http://www.hydrosheds.org/)
 * Land cover, used for modelling run-off and available [from the FAO](http://www.fao.org/land-water/land/land-governance/land-resources-planning-toolbox/category/details/en/c/1036355/)
 * ETo, the reference evapo-transpiration for an area, also available from the FAO
 * Precipitation, from many sources, hopefully monthly, never easy to use

For example, here's our same river overlaid with the DEM elevation data.

![DEM][hydro5]

Previously I used the laborious and buggy [ArcPy](http://pro.arcgis.com/en/pro-app/arcpy/get-started/what-is-arcpy-.htm)  t oextract all of this information in the network and nodes data structures, but now [rasterio](https://github.com/mapbox/rasterio) makes this a walk in the park. It's a straightforward library for reading raster GIS data and sampling and manipulating it, and takes only a few lines to load all of this new data.

## Calculating hydropower potential
One thing that we can do with all of this data is replicate the hydropower estimates, from the paper we wrote, except now just for Dieprivier in Cape Town.Note that this is exclusively for [run-of-river](https://en.wikipedia.org/wiki/Run-of-the-river_hydroelectricity) mini-hydropower. To estimate power output, we use the hydropower formula as follows:

 * P = ηρgQH

where P  is the power output, η  is the efficiency, ρ  is the density of water,and g is acceleration due to gravity. Q is the flow-rate, and H is the head, or height difference available. These last two must be calculated for each point using the data described above.

The head is simple: we get the height for our chosen point, and then look a set distance up-stream and get the height there – the difference between these is the head. The flow-rate is more complicated. The global run-off data we have is provided in m/s, where we need m3/s. So we do the following:

 * Q = runoff × catchment-area

where catchment-area is the total area upstream of the selected point.Multiplying these together calculates the theoretical amount of water that should flow past this point.

Applying this to Dieprivier, the model creates a point every 500 metres and calculates the head over the preceding 500 metres. By filtering to only include those with at least 10 metres of head and more than 100 kW output, we get the following suggested point of 162 kW, with 12 metres of head and flow rate of 2.75 m3/s.

![Hydropower][hydro6]

Note that this is an unchecked, un-calibrated example result, I'm not at all suggesting someone should build a mini-hydropower site there.

## Going further with rainfall run-off and discharge
The result above was calculated using the GSCD, which provides only a single value, with no monthly or yearly variations. This doesn't provide much information about seasonal changes, nor allow for any calibrations with stream gauges, which will likely be on a daily or monthly basis.

To improve this, I extended the model to work with precipitation as an input instead, which is often available as monthly (or even daily data). For each node then, the model takes local precipitation, land cover and evapo-transpiration data and uses the [Simplified Coefficeint Method](http://www.weap21.org/webhelp/hydrology.htm) to calculate local rainfall run-off. This is then carried downstream in the model, and when stream join,their flows are combined. At the same time, there are certain losses on each stream due to various causes.

Then every river section has a (potentially) more accurate discharge associated with it, which is now able to vary by month and day. So in the example above, we could specify not only the mean power output, but also show which months we expect to have lower and higher output.

The code for this is all with the model in the [GitHub rep](https://github.com/carderne/hydro-networks), but be aware – it takes a lot of fiddling and calibration to get useful numbers out, and precipitation and stream-gauge data often require a lot more data wrangling to make ready for the model.I was on the verge of setting up the model to calibrate against some measurements automatically, but that'll have to be a project for another day.

## Towards a generalised model
From there, it's not a huge step to add other point withdrawals (such as city water requirements or a farm) and use the model to make predictions about the system. For example, by including projected precipitation changes and increased population (and hence increased withdrawals) we could model whether there would be a water shortfall, and in which months this would be most severe.

As I said, the model isn't quite there, but hopefully I'll come back to it at some point.

[hydro1]: /assets/images/2017/hydro1.jpg
[hydro2]: /assets/images/2017/hydro2.jpg
[hydro3]: /assets/images/2017/hydro3.jpg
[hydro4]: /assets/images/2017/hydro4.jpg
[hydro5]: /assets/images/2017/hydro5.jpg
[hydro6]: /assets/images/2017/hydro6.jpg