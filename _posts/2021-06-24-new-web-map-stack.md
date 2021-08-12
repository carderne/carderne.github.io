---
layout: single
title: "The new web mapping stack"
date: "2021-06-24"
excerpt: "Long live Mapbox tiles"
---

[Web maps are back in the news!](https://news.ycombinator.com/item?id=27605656) It seems like “the” solution for making performant, light-weight web maps has crystallised around [Mapbox-y](https://docs.mapbox.com/mapbox-gl-js/api/) vector tiles and related technologies. Except for Google Maps — they use vector files but not Mapbox-y ones. And Apple Maps. But everyone else making cool, interesting maps for stuff other than moving cars around.

## Background
Generally speaking, web maps have a basemap (borders, roads, buildings etc) plus whatever you layer on top of that (trails for a hiking map, power plants for that map etc). Then you have a JavaScript frontend that draws all this on the screen and lets you play with it.

(It's more confusing than that, because often your “basemap” and “layers” are all actually coming from the same place.)

The most generalised stack I can think of is:
- Data: the actual GIS data that you want to visualise (flat files, PostGIS database, tile images etc)
- Server: serve the above at an API/URL that a front end library can consume
- Frontend: visualise the data coming from the server and allow user interaction

The more old school approach (which probably has many benefits that I've yet to understand) is to implement the following stack:
- Data: [PostGIS](https://postgis.net/)
- Server: [GeoServer](http://geoserver.org/)
- Frontend: [OpenLayers](https://openlayers.org/)

This would generally use _raster tiles_ for basemap (and other) data. These are small 256x256 pixel PNGs that are loaded as needed for different zoom, x, and y coordinates.

## Vector tiles
The “new” method uses vector tiles instead of raster tiles: in place of little images, there are little vectors that also only cover small 256x256 (or whatever you specify) areas. These are smaller (less bytes), can be styled by the frontend instead of having fixed colours etc, and can be used in between zoom levels (so you don't “jump” from zoom 5 to 6, but can smoothly transition between).

By far the easiest way to use this stack is to go all in with Mapbox. Sign up for an account, and use [Mapbox Studio](https://studio.mapbox.com/) to manage the Data and Server parts of the stack, along with graphically styling elements and uploading additional data layers. Then use [Mapbox GL JS](https://gdal.org/programs/gdaldem.html) to display your map, and add additional data (such as user-specific layers) from GeoJSON or a server (more further down). It's fast, easy, mostly open source (enough) and has a very generous free tier.

## Aside
If you’re happy with default OSM basemap styles and have relatively simple data layers, you can get pretty far just using [Leaflet](https://leafletjs.com/) with GeoJSON/another data source. It has a much easier learning curve than Mapbox and comes with lots of nice things like layer switching and pop ups out of the box.

## Fully open
The only downside to Mapbox is that you’re in a proprietary system, and if you have a lot of users (I'm fortunate enough never to have had this problem) or a non-standard use-case, it could get expensive. Or you might just brefer the enriching breeze of a fully open source stack.

**NB:** I'm not suggesting a ditch-Mapbox parade. Their software, tooling and cartography are incredible, and their contributions to open source massive. The alternatives below are mostly directly based on Mapbox technologies/contributions.

The alternative is to self-host a fully open source stack, and this is where things get more confusing. And I'm clearly not the only one: Mapbox had a [hard time explaining](https://github.com/osm2vectortiles/osm2vectortiles/issues/387) to some developers exactly which part of their stack was _not_ openly licensed.

Probably the “lightest” solution for the basemap is to use [MBTiles](https://docs.mapbox.com/help/glossary/mbtiles/) directly. These are protobuf Mapbox Vector Tiles packaged into a SQLite file. But you still need to create them, and then serve them!

The easiest method that I've found is as follows:
1. Download an OpenStreetMap extract from [Geofabrik](https://download.geofabrik.de/).
2. Use [tilemaker](https://github.com/systemed/tilemaker) with the OpenMapTiles [_schema_](https://openmaptiles.org/schema/ ) to convert this into MBTiles.
3. Then you can use [tileserver-gl-light](https://github.com/maptiler/tileserver-gl) together with a _style_ (OMT have a number of [free styles](https://github.com/openmaptiles/osm-bright-gl-style/) compatible with their schema) to serve this data to your frontend.
4. Finally, you can use [MapLibre](https://github.com/maplibre/maplibre-gl-js) (forked from the last fully free Mapbox GL) to dismay your maps.
5. You can also use [tippecanoe](https://github.com/mapbox/tippecanoe) to create additional non-OSM MBTiles from GeoJSON vectors. And [GDAL](https://gdal.org/programs/gdaldem.html) (don’t forget colour, these are harder to style in the front-end!) to do the same for raster data.
6. You’ll presumably want to edit the style further, so there's [Maputnik](https://github.com/maputnik/editor) as an alternative to Mapbox Studio. (Note that you can also control this in the frontend code, or just hand-edit the JSON)

## With a database
If you expect your data to change more frequently, or if you have user-specific data, you’ll probably need to have a database (usually PostGIS) installed. In that case it _might_ be simpler to skip MBTiles and serve vector tiles directly from your database. You can get OSM data _into_ your database using [osm2pgsql](https://osm2pgsql.org/), and then use something like [Tegola](https://tegola.io/) to serve this on an endpoint.

At this point you'll want to use whatever server stack you're familiar with (e.g. Flask + [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/en/latest/index.html)) and use as much of the modern MBTiles stuff as you can!

## Postscript
I started out with web maps (and JavaScript) using Python's [Folium](http://python-visualization.github.io/folium/) in Jupyter notebooks. I then wanted more control over my maps, so I opened the exported Leaflet `.js` files and fiddled, and it don't take long to figure out that the API was super friendly. I started using Mapbox (non-GL) on a whim (it's JavaScript, after all) and so in the years since that Leaflet peak of “it's all so simple!”, I've become steadily more confused (but also more capable — GL is so fast!).
