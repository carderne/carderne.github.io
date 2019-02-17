---
layout: single
title: Places to go in Barcelona
date: '2018-12-15 12:01:00'
excerpt: "A basic web map featuring cool places and things discovered in the last few months in Barcelona."
tags:
- outside
---

After a few months of living in Barcelona and discovering interesting things, we decided to start keeping track of these in a Google Sheet. And so the natural progression was to make a simple web map based on that data, using [geocoder](https://geocoder.readthedocs.io/) (periodically) and [MapBox geocoding](https://docs.mapbox.com/mapbox.js/api/v3.1.1/l-mapbox-geocoder/) (on the fly) to find coordinates for all of our spots.

The app is here: [Barcelona Places](https://rdrn.me/barcelona-places/) and development is [here](https://github.com/carderne/barcelona-places).

It also works pretty well as a [PWA (Progressive Web App)](https://en.wikipedia.org/wiki/Progressive_web_applications) to provide a near-native mobile experience. To do this on iOS (I assume the procedure is similar on Android), navigate to the [site](https://rdrn.me/barcelona-places/) and click the 'share' up-arrow in the bottom centre and then choose 'Add to Home Screen'. You'll get an icon on your home screen to use the the map is if it was an installed app.