---
layout: single
title: "Fun with gov.uk car data"
date: "2023-04-19"
excerpt: "I shouldn't have had to do this"
---
<script src="https://cdn.jsdelivr.net/npm/vega@5.22.1"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5.7.1"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6.21.3"></script>

An embarrassing amount of my identity is built around the fact that I don't, and never have, owned a car. They're terrible for the climate, terrible for the environment, terrible for the people around you, and terrible for you. But every time I go to Wales (difficult, without a car), I come back wishing I owned a car.

I was in Wales two weekends ago, and the car-want is lingering. For a long time I hoped we could could hold off on car-ownership until EVs were cheaper and made sense for the amount of driving we're likely to do. It doesn't make financial sense for us to spend £30k on an EV to go to Wales once a month, and any carbon-goodies we'd feel are wiped out by the fact that at such low annual mileage, and end-of-life banger from 2010 would easily be the most climate-friendly option.

So I'm begrudgingly looking at diesel and petrol. And within that constraint, I want to maximise fuel-efficiency and minimise lifecycle carbon emissions. I wasn't sure how to compare petrol and diesel and generally felt short of data, so I went knocking and found the UK Vehicle Certification Agency's [car fuel data](https://carfueldata.vehicle-certification-agency.gov.uk/downloads/default.aspx) archives. They are, slightly unhelpfully, split into separate CSVs for each year _and_ for different [European emission standards](https://en.wikipedia.org/wiki/European_emission_standards) (Euro 5, Euro 6 etc). Not only that but the column names changed and columns came and went. And not only _that_, but some time in the last five years, the testing scheme changed from [NEDC](https://en.wikipedia.org/wiki/New_European_Driving_Cycle) to [WLTP](https://en.wikipedia.org/wiki/Worldwide_Harmonised_Light_Vehicles_Test_Procedure). So I ~~wasted~~ spent an hour or two merging them all together into one big mega-CSV of about 55,000 rows, containing, ostensibly{%- include fn.html n=1 -%}, every car approved for sale in the UK between 2010 and 2022.

_If you just want the raw data, you can get it [here on Google Sheets](https://docs.google.com/spreadsheets/d/1cp68jPKkK2AjjX2oA8vZ75jS-DEWccZeySxz27YHmtU/edit#gid=157623882&fvid=1041876850). You can download it as a CSV from there if you like!_

Caveat emptor: I was pretty fast-and-loose with how I joined stuff together. I have combined all NEDC/WLTP data, which aren't actually comparable. Based on a thumb-suck, I assigned WLTP-Low to NEDC-Urban and WLTP-High to NEDC-ExtraUrban, dropped the extra two WLTP cycles, and equated the combined WLTP with the combined NEDC.

This first chart shows a sample of 5,000 random points from the full dataset (because I didn't want to dump 25 MB of [Vega-Lite](https://vega.github.io/vega-lite/) JSON on your computer). This chart is really just for fun and to get an idea of the shape of the data. It's that pointy bottom right bit full of Peugots that is interesting, rather than the Land Rover-y section in the top left. The two distinct bars are petrol to the left, and diesel to the right, showing quite clearly that diesels, in general, get more miles per gallon (sorry metric-lovers, working to a confused UK audience here). You can select car brands from the legend on the right, which should give quite a clear idea of where on this curve different brands see themselves!
<script src="/assets/cars/sample.js"></script>
<div id="vis-sample" style="padding:2rem 0"></div>
<script type="text/javascript">vegaEmbed('#vis-sample', sample)</script>

I then filtered for cars that have better than 64 MPG, less than 115 g of CO<sub>2</sub> per 100km, older than 2019 (because lifecycle emissions, also cost), automatic only (for other reasons, but also because it reduces the dimensions by one), and only those within a thumb-sucked list of non-silly brands (Ferrari out, Toyota in. Also BMW didn't make the cut). And now we get something a bit more useful! Again, diesel gets higher MPG.

But if you use the `X-axis column` dropdown under the chart, you can toggle to `MPG_price_adjust`, where I've multiplied the petrol MPG values by the diesel/petrol fuel price ratio. The resulting chart is actually more useful, and is effectively the "Miles per £". There we can see that there's actually not much difference. Still, if you investigate more carefully, the equivalent petrol-y points are generally for smaller cars than their diesel-y compatriots. Eg if you set the make to Peugeot (I was today years old when I learned how to spell that), you'll find petrol 208's hanging out with considerably larger 2008's.

If you change the x-axis again to `MPG_Hi_price_adjust`, which is the _highway_ MPG, surprisingly petrol doesn't lose out too much -- here I was expecting diesel to take the lead for highway driving, which, after all, is the one that's needed if you primary motivation is getting to Wales once a month. Again, diesel still generally comes out ahead for the same size car, but this is based on a relatively low diesel/petrol price ratio, which could widen/narrow in the future. Anyway, I feel satisfied that, on the basis of cost-per-mile, there's not toooo much in it. Unless you care about local pollution, where diesel is much worse! But you can make this problem go away by selecting the "Euro 6 only" option below. Then diesel are still worse, but not catastrophically so.
<script src="/assets/cars/good.js"></script>
<div id="vis-good" style="padding:2rem 0"></div>
<script type="text/javascript">vegaEmbed('#vis-good', good)</script>

That's all well and good but it's pretty useless without **price data!** And, as far as I can tell, there's no straight-forward way to get bulk data on UK second-hand car price data. AutoTrader is the obvious place to look, but they seem to be quite tight-fisted with it.

By manually looking around, I've chosen some cars from this last chart that make sense for our additional, but harder to quantify requirements: [small but not too small](https://www.carsized.com/en/cars/compare/citroen-c3-2016-5-door-hatchback-vs-skoda-fabia-2018-estate/), and cheap. Some of these are:
- Citroën C3
- Ford Focus
- Hyundai i30
- Kia Ceed
- Peugot 308
- Renault Megane
- Škoda Fabia Estate
- Vauxhall Astra

------------------------------

{% include fnn.html n=1 note="There are no Volkswagen group cars post-2017 or so, so clearly something is up. Emissions scandal I wonder..." %}