---
layout: single
title: Using NASA night time lights to guess where the grid is
date: '2019-01-02 15:31:00'
excerpt: "A lot of the work I do relates to finding the cost-optimal of bringing electricity to more people and businesses. Implicit in this is the assumption that we know where the people are who already have electricity access. Often we don't."
tags:
- inside
---

A lot of the work I do relates to finding the cost-optimal of bringing electricity to more people and businesses. Implicit in this is the assumption that we know where the people are who already have electricity access. Often we don't.

One method for guessing (dare I call it a heuristic?) is using NASA's [Night Time Lights](https://www.nasa.gov/feature/goddard/2017/new-night-lights-maps-open-up-possible-real-time-applications) satellite imagery - processed satellite photographs taken at 2 a.m. around the world. The hypothesis is that locations that show up at night (once filtered of reflections and fires), are places that have electricity access. And places that have electricity access (by and large) get it from electrical grid infrastructure. As you can imagine, it takes a bit of light to be visible from space, so a few small lamps and phone chargers powered by off-grid PV are unlikely to show up and break our assumption.

The steps to get from this assumption to a made-up map of medium voltage grid lines is as follows. (As always, skip over to the GitHub repo if you prefer: [https://github.com/carderne/gridfinder](https://github.com/carderne/gridfinder).)

## From satellite imagery to a target and costs

Firstly, we combine a range of monthly satellite images to average out any aberrations. I took a year's worth, but you could easily do more. By taking the *x*th percentile for each pixel, we ensure that only those places that are lit up that percentage of the time are included. So a fire that burned for two months is excluded from the final product. We should also filter for things like water features, which can have reflections of the moon, but it seems like NASA has already done a decent job of cleaning up this stuff. The result of that process is the image below (for Uganda).

![Merged NTL](/assets/images/2019/gf1.png)

Then we want to boil this down to a binary image: 1 for yes-has-electricity, 0 for no-it-doesn't. We do this by convolving and subtracting 2D filter, that basically concentrates sites with evidence of night time lights and zeros out the faded areas around them, resulting in the image below.

![Filtered NTL](/assets/images/2019/gf2.png)

Then we need to connect these together, with our hypothetical grid lines. A minimum spanning tree is the natural starting point, with difference: instead of following the shortest line between points, we apply a cost function based on existing road networks, going on the assumption that grid lines are more likely to follow (or be followed by) these existing networks. So we extract the full Ugandan road network from OpenStreetMap (thanks to [geofabrik](https://download.geofabrik.de/africa.html)) and assign a 'cost' based on this: lower cost for bigger roads, full cost in places with no road.

So now we have the two inputs needed to algorithmically 'create' a Ugandan grid network. A set of 'target' pixels that need to be connected, and a 'cost' array which can guide an algorithm in finding the cheapest way between them.

## So many algorithms to choose from

Minimum spanning trees have had a lot of interest over the years as a problem in network theory, with many different solutions proposed, each with its own uses and drawbacks in speed and complexity. For this I used Djikstra's, because it's one of the simplest to implement. Basically, it goes as follows:

1) Start at a connected point.  
2) Branch outward (typically along network edges, but in this case between raster cells) keeping track of the cost as the total distance to a known connected location, adding each cell to the queue as we go.  
3) If another connected target cell is found, record it, and all the points leading to it are assigned a distance of zero and re-added to the queue for analysis.  
4) If we find a shorter route to an already connected cell, this replaces the former.  
5) Continue until all cells have been visited!

In graphic form, this looks like this:

<video width="100%" height="500" controls>
    <source src="/assets/videos/gridfinder.mp4" type="video/mp4">
    Your browser does not support the video tag.
    </source>
</video>

## Final results

The results of this algorithm look as follows, where red is the algorithm's guess and green is actual grid data for Uganda. Where they overlap in a murky brown colour is where the model was correct - quite a lot of it! 

- Points identified as grid that are actual grid: 85%
- Actual grid that was identified: 64%

![Filtered NTL](/assets/images/2019/gf3.png)