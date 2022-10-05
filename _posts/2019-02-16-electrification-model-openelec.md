---
layout: single
title: "A new open source electrification model: openelec"
date: '2019-02-16 12:29:00'
excerpt: "A better tool for planning electricity access."
image: /assets/images/2019/oe1.png
---

In my work in electricity access and related issues, an issue that often comes up, and often frustrates me, is the lack of good open source tools. I've been part of discussions where various planners are obliged to choose proprietary systems that come with significant lock-in, simply because the alternatives aren't as capable, or they aren't aware of them. Apart from being expensive and closed source, these tools are typically incapable of being adapted to a team's existing processes and workflows.

{% include image.html url="/assets/images/2019/oe1.png" description="openelec.me in action for a national plan of Lesotho, showing the second of four time steps" %}

There are [existing open source tools](https://onlinelibrary.wiley.com/doi/full/10.1002/wene.305) (including [one](https://rdrn.me/lighting-the-world/) that I was extensively involved in) in this category, but none of them are open source in a meaningful way, and all have significant and non-trivial shortcomings. So building from [these](https://rdrn.me/flask-optimize-minigrid/) [two](https://rdrn.me/modelling-universal-electrification/) developments, I've started to make inroads on this issue by creating [openelec](https://github.com/carderne/openelec). In contrast to the other tools, it is truly open source, modular, and has an evolving but sensible API that allows it to be plugged into a variety of front-ends, such as Jupyter, QGIS or a web interface. It is built with proper network analysis and optimisation at its core, with the same components used for different scales (national, local) and objectives (private, public). It is easy to add data points as available and replace the decision calculus (currently CAPEX) with any other, such as LCOE or social goals. It can be made to run in multiple time steps of any granularity and with any prioritisation algorithm.

I discussed most of the model development in my other blog posts ([one](https://rdrn.me/flask-optimize-minigrid/) and [two](https://rdrn.me/modelling-universal-electrification/)). The next steps were mostly merging the two models, improving some functionality and working to improve the code and documentation and work towards a more flexible and user-friendly API. Currently, [openelec](https://github.com/carderne/openelec) provides a very straight-forward mechanism for the following main planning goals:
1. Create a national electricity roll-out plan for any country using open data such as [GHS](https://ghsl.jrc.ec.europa.eu/), [NTL](https://ngdc.noaa.gov/eog/viirs/download_dnb_composites.html), [GDP](https://preview.grid.unep.ch/index.php?preview=data&events=socec&evcat=1&lang=eng) among others.
2. Using the same sources to select the most suitable villages for private sector ventures, depending on input requirements.
3. Design of LV networks for villages and towns, whether for on- or off-grid application, using mostly [OpenStreetMap](https://www.openstreetmap.org/) data.

{% include image.html url="/assets/images/2019/oe2.png" description="openelec.me in local planning mode with some sample output" %}

## From model to tool
For advanced users and modifying/adding functionality, it is probably easiest to use openelec via Jupyter notebooks or direct scripting. I provided simple instructions on the GitHub repository to `pip install` or `git clone` the openelec code. The base [data requirements](https://github.com/carderne/openelec/tree/master/test_data) are also provided in the repository.

For more general users, a web interface poses the lowest barrier to entry and no installation requirements. To this end, I created a very simple Flask app (basically just an HTTP layer over the openelec API) and got it up and running on [AWS Lambda](https://aws.amazon.com/lambda/) using [serverless](https://serverless.com/). This means I pay nothing for hosting costs while no one is using the app, but it scales seamlessly when suddenly loads of people are running my pretty resource intensive optimisation algorithms. I put this to the test during the [EMP-A workshop](http://www.energymodellingplatform.org/emp-a-2019.html) in Cape Town in January, where suddenly 30 demanding users were simultaneously running the model.

The front end provides a simple interface to the model (coded in JavaScript) that exposes most of the functionality, but obviously doesn't allow any extensions or modifications. To play with this interface (the easiest way to understand what openelec is for), please visit [openelec.me](https://openelec.me/). You can also watch the video below with a quick overview of the main model features.

<video width="100%" height="500" controls>
    <source src="/assets/videos/openelec.mp4" type="video/mp4">
    Your browser does not support the video tag.
    </source>
</video>

For more routine use, and in internet constrained environments, a QGIS Plugin is probably most useful - I'm working on it now!

## Get involved
I'm still working on getting the code as developer-friendly as possible, but code contributions, suggestions and ideas are very welcome! It's all completely open source and I have no intention of trying to monetise it. Please also get in touch if you'd like to use openelec in whatever capacity and need help doing so.
