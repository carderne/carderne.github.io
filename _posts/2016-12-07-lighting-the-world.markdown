---
layout: single
title: "'Lighting the World' - A paper I worked on"
date: '2016-12-07 08:35:00'
excerpt: "This model is used to determine the best way to achieve universal electrification, by suggesting for each location in a country whether to extend the electrical grid, use a mini-grid system, or rather to rely on stand-alone household solar PV systems."
tags:
- inside
---

I did my Master's thesis at KTH University of Technology on [A climate, land-use, energy and water nexus assessment of Bolivia](http://urn.kb.se/resolve?urn=urn%3Anbn%3Ase%3Akth%3Adiva-189473). That is, I used various models and approaches to attempt to look holistically at Bolivia's land, energy and water use, taking into account the expected impacts of climate change. One of the models I used is called [OnSSET](http://www.onsset.org/) (EU-funding requires silly acronyms, apparently). This model (developed at KTH) is used to determine the best way to achieve universal electrification, by suggesting for each location in a country whether to extend the electrical grid, use a mini-grid system, or rather to rely on stand-alone household solar PV systems.

![Onsset Bolivia][onsset1]

Essentially the model takes in a variety of data on population distribution, energy infrastructure, solar intensity, night-time satellite imagery, as well as social and techno-economic factors. As a starting point, it uses this to estimate where the settlements are that already have electricity access. From there, the model spreads outwards from electrified locations, and for each new location, comparing the cost of connecting by the three different options. An exhaustive (-ing?) process.

I started overhauling this model while using it for my thesis, and as a result was talked into staying at the division as a Research Engineer. In essence, the model I inherited was a complicated mix of Excel macros, copy-pasting and difficult GIS instructions. During the course of my thesis I picked up Python and set to work replacing the model with a coherent Python library: [PyOnSSET](https://github.com/carderne/PyOnSSET).

This made modelling a country a few orders of magnitude faster, and much easier to batch process huge jobs. So we immediately put it to work modelling the whole of Sub-Saharan Africa! The modelling unit is 1 km2  (more on that later) so this involved modelling more than 20 million individual units (iteratively!). We published this in Environmental Research Letters: [Lighting the World: the first application of an open source, spatial electrification tool (OnSSET) on Sub-Saharan Africa](http://iopscience.iop.org/article/10.1088/1748-9326/aa7b29/meta).

![Onsset Africa][onsset2]

The model was also used in the International Energy Agency's [Special Report: Energy Access Outlook](https://webstore.iea.org/weo-2017-special-report-energy-access-outlook)  to show what is need to provide electricity to the millions in Africa currently without access (see the figure above, taken from the report.

Unfortunately, I left KTH and the Division for Energy Systems Analysis before getting the time to fix two of the model's biggest shortcomings:

1. Modelling 1 km2  grid cells, instead of representations of actual towns and villages. This means that a barren patch of land will get a solution, even if it's never inhabited. This is not only inefficient, computationally, but     logically unsound. In the same way, larger towns and cities (anything more than 1 km2) can get split up into multiple modelling units, which doesn't make a lot of sense.
2. It handles time in a very simplistic way, modelling only today  and 2030 (or another far-off year). This doesn't exactly give policy-makers and private sector developers a good vision of where they should be going tomorrow.

[onsset1]: /assets/images/2016/onsset1.jpg
[onsset2]: /assets/images/2016/onsset2.jpg