---
layout: single
title: A Flask app for mini-grid planning with a cost-optimised spanning tree
date: '2018-03-18 13:20:00'
tags:
- inside
---

As part of ongoing work on energy access in Tanzania, we (the [IFC](https://www.ifc.org), together with Tanzania's Rural Energy Agency) have mapped over 4 million buildings in rural parts of the country. This gives loads of new possibilities to those looking to work in these areas, and not only in the energy sector. One of these is the ability to conduct detailed site assessments,including sensible estimates of household populations and potential demand,along with wiring requirements to connect a village.

Apart from  the potential for use in state planning for new grid extensions,this data is valuable to private developers looking to sell off-grid services such as stand-alone solar systems (such as those sold by [M-Kopa](https://www.bloomberg.com/features/2015-mkopa-solar-in-africa/) as well as more capital intensive mini-grid systems (with a power source and grid connecting households, but no connection to the national grid), which [some suggest](https://www.greentechmedia.com/articles/read/minigrids-are-the-cheapest-way-to-electrify-100-million-africans-today)  are a key to tackling energy access issues.

In this post I'm focusing on mini-grids, mostly because it's a more interesting problem to analyse. However, I also provide some cost comparisons with national grid connections. This post is split into two main sections:

 1. Using a minimum spanning tree and cost-optimisation algorithm to find the ideal network layout for a given village and parameters
 2. Serving this as a GIS web app with Flask, where users can customise inputs, run the model, and visualise results

So if you just want an example of a basic Flask app, go ahead and skip to the second section. Or just check out the [GitHub repo](https://github.com/carderne/minigrid-optimiser)  for the code for both sections.

## Optimising mini-grids in rural villages
As I've covered [elsewhere](https://rdrn.me/open-data-access-tanzania/), data is one of the key barriers to ramping up off-grid development and investment.Machine learning and ML-supported manual mapping in OpenStreetMap (a strategy we applied in Tanzania) are starting to make inroads into this problem, at least for assessing demand.

As a test case, I've chosen the village of Sipungu  in the Tabora region ofTanzania. To start off with, let's see how this village looks in OpenStreetMap compared to Google Maps. Each of the 444 little shapes on the left is a building, accurately traced by the [HOT team](https://www.hotosm.org/where-we-work/tanzania/) team in Dar es Salaam as part of the IFC project. Some are homes, some are stores, some are schools. As you can see, there's no information in Google Maps about this village – not even the road in.

![Compare][mg1]

To find the optimum way of connecting all these buildings to a mini-grid system,we turn to network theory, and in particular, the [minimum spanning tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree). This is the set of lines that connects a group of points with the minimum total distance (or other cost function). For the village of Sipungu, this looks as follows, where each blue dot is a building (very small ones filtered) and the green point a randomly chosen location for the solar PV installation. I haven't yet extensive testing on speed with larger datasets, but my solution for now is a combination of a [k-neighbors graph](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.kneighbors_graph.html) and scipy's built-in [minimum_spanning_tree](https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.sparse.csgraph.minimum_spanning_tree.html) function.

![MST][mg2]

Our goal then is to determine, based on some criteria, which of these connections to maintain. The first step is to direct the network from the PV installation outwards, so that the model knows where to start in looking for connections to drop or keep. We don't want to accidentally disconnect the PV system itself! This is a process not dissimilar to the stream ordering used in my [hydrological modelling](https://rdrn.me/modelling-hydrological-networks/). Conceptually they fall in with a broad range of physical, mathematical and [social](https://rdrn.me/visualizing-book-club-ai/) problems where [network theory]([https://en.wikipedia.org/wiki/Network_theory) is applied.

There are a number of different ways to cost-optimise this network; I chose a brute force approach to find the configuration with the highest [net present value](https://en.wikipedia.org/wiki/Net_present_value), i.e. the most money for the developer, taking into account the future income streams and costs. This sounds like a ruthless way of thinking, but for more mini-grids to get built and more people to get access to electricity, they need to be sustainable. The hope is that once the system is running, demand will increase and more households will become profitable to connect.

The algorithm starts with the complete network, and considers which single deletion of a line a connecting two households provide the biggest boost to profitability. For example, a very small household far away from any others -lots of wire, but not much demand or electricity sold. It then repeats this process over and over again until there are no more profitable configurations to be found and that is the optimum network!

I contrived the following main parameters for the village of Sipungu, along with some heuristics for determining the number of people based on building size.

 * Minimum building size: 30 m2
 * Wire cost: 25 USD/m
 * Connection cost: 150 USD/household
 * Tariff: 0.25 USD/kWh
 * Demand: 6 kWh/person/month
 * Generator cost: 7,000 USD/kW

The resultant optimised network is shown below, where about 80% of the buildings are connected by the algorithm. The remaining little clusters are deemed to not be worth connecting, based on the capital outlay required and expected returns based on the demand and tariff above. So with this new data and this model, we already have an estimate of the costs involved and how the mini-grid might end up looking (noting, of course that the real network will follow real-world constraints like the existing road).

<iframe src="/assets/html/map-sipungu.html" style="width: 100%; height: 400px" name="internal" frameborder="0"></iframe>

Note that I mentioned the model optimises for NPV. With these parameters, the NPV of this development was calculated to be USD -815,000 – in the optimum case!So either the developer needs to cut costs, or charge higher tariffs, or hope for higher demand. This leads me to another extremely useful feature of this type of model: easy scaling. It's as easy to model Sipungu village as it is to model hundreds of villages.

So I did. To explore the relationship between village density and economics, and to understand tariffs needed for project profitability, I modelled 100 Tanzanian villages, considering for each one different combinations of costs, demand and village coverage (percentage of households electrified). In the chart below,each point represents a model run, with demand on the horizontal axis (6 kWh,from the example above, is marked by a vertical red line) and the required tariff for a 6-year payback on the vertical.

As you can see, there are not many villages that can sustain a mini-grid at that demand level and tariff. Even at extremely high demand levels, around 0.24USD/kWh is still needed for projects to be feasible. However, grid electricity in Tanzania is below 0.10 USD/kWh, so this is unlikely to be possible for poor rural villages. One possible solution: subsidies.

![Tariffs][mg3]

## Creating a simple GIS web app with Flask
A web app interface to the model would make it a lot more accessibly to non-coders. So I set out to create a basic app that would allow a user to select a village and the desired input parameters, and get an interactive map and summary results in-browser.

[Flask](https://github.com/pallets/flask) is a Python web framework – it transforms data and code into web pages and APIs. I selected it for this project because it is lightweight and easy. A basic Flask app looks as follows. The `'/'` in `@app.route()`  tells Flask that this method should be run when someone accesses the base URL of the website, and the `'Hello World!'`  returned is what will be displayed in the user's browser.

```
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'
```

Most of the time you want your result to look better than that, so you use anHTML template, into which Flask inserts results as follows using the module render_template. I set up a template with buttons and selectors for the model parameters, and a big window where the mapped results can be displayed. When the user first arrives, they are greeted with an overview map of Tanzania and a selector list on the left. Once they've chosen a village, selected the generator site, and inserts the other parameters, they are shown the mapped results – as in the example below for Nakiu.

<a href="https://gfycat.com/CarefreeRemarkableAardwolf"><img src="https://thumbs.gfycat.com/FirstWiltedGreyhounddog-size_restricted.gif" alt="Web App demo"></a>

Or below for the slightly larger village of Uwemba.

![Uwemba][mg4]

The front-end is set up with JavaScript to make AJAX calls to the server when necessary. So, for example, when the user clicks 'Run (and be patient)' the client sends a request with all the necessary data to the server app, which uses this data in whatever way, and then responds with a JSON representation of its output. The front-end then uses this data to update the user interface in some way – in this case by displaying results and updating the map.

```
from flask import jsonify

@app.route('/run_model')
def run_model():
    args=request.args
    # model code here
    # or calls to external module
    results = ...
    return jsonify(result=results)
```

This approach means that the entire web page rarely or never has to reload,which makes the user experience much faster and more dynamic.

Then there's only one thing left to do: push it to a server where it can run without keeping my laptop hot. I used a simple git set up to push the latest model and app to a Google cloud instance, and use `supervisor` to keep the Flask app up and running. I won't post all of the code here, but it's available at my [GitHub repo](https://github.com/carderne/minigrid-optimiser).

[mg1]: /assets/images/2018/mg1.png
[mg2]: /assets/images/2018/mg2.png
[mg3]: /assets/images/2018/mg3.png
[mg4]: /assets/images/2018/mg4.png