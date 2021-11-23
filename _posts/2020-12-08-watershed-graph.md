---
layout: single
title: "Oh, the places your pee will go"
date: "2020-12-08"
excerpt: "Graphing the world's water basins with Neo4j"
image: /assets/images/2020/basin-geom.png
---

The great compilation of river and watershed data from [HydroSHEDS](https://hydrosheds.org/) plus the power of [Neo4j](https://neo4j.com/) make it pretty easy to do some fun things with water.


The fun thing, in this case: ['Watershed Explorer'](https://water.rdrn.me/). A 'tool' to find all the upstream area and downstream flow for any point on earth, with the click of a buton. The code and more details [are here on GitHub](https://github.com/carderne/water).

A watershed or [drainage basin](https://en.wikipedia.org/wiki/Drainage_basin) is "any area of land where precipitation collects and drains off into a common outlet, such as into a river, bay, or other body of water." Calculating this normally involves the following steps using a high-resolution [digital elevation map](https://en.wikipedia.org/wiki/Digital_elevation_model) (a map of land height at each point), then calculating the flow direction (North, South, etc) at each point, and then following these directions to calculate the region that contributes to a single outlet.

The people at HydroSHEDS have already done this at many different [Pfafstetter levels](https://en.wikipedia.org/wiki/Pfafstetter_Coding_System), which means we have small drainage basins at up to 5-10km pre-calculated for a set of points. The dataset also says, for each little basin, which basin is _downstream_ of it.

Downstream is easy, because every basin always flows into exactly one downstream basin (or the sea, or the sink of an [endorheic basin](https://en.wikipedia.org/wiki/Endorheic_basin)). _Upstream_ is slightly more involved, because each basin can have multiple upstream basins, or none (if it's a headwater).

However, if we link these basins up into a graph (network, if you prefer) with basins as nodes and their up-/downstream relations as directed edges, we can do this easily. I first did this with Python's [NetworkX](https://networkx.org/), but decided to load it into Neo4j once it promised to be interesting. Neo4j is a graph database that is made for this kind of thing, and provides its own query language `Cypher` as well as some neat built-in visualization tools to get a more intuitive idea of what you're querying.

{% include image.html url="/assets/images/2020/basin-graph.png" class="narrow-img" description="The basin graph upstream of a point in the Breede River in South Africa." %}

The dataset has just over a million basins (nodes) with one relationship (edge) each. After exporting it as a CSV, I loaded it into Neo4j as follows.
```
LOAD CSV WITH HEADERS
FROM 'file:///file.csv' AS row
CREATE (:Basin {
    idd: toInteger(row.idd),
    down: toInteger(row.down)
})
```

And then created the relationships.
```
MATCH (a:Basin)
MATCH (b:Basin {idd: a.down})
CREATE (a)-[:down]->(b)
```

Once this is done, the database knows exactly how everything related to everything else, so getting the points upstream from somewhere is straightforward. We simply get the location of interest, and then follow the `[:down]` relationships in reverse as far as possible.
```
MATCH (n:Basin)
WHERE n.idd = $idd
OPTIONAL MATCH (u)-[:down*]->(n)
WITH COLLECT(DISTINCT u) AS x
RETURN x
```

I also added spatial data to each node, so that its possible to query by latitude-longitude coordinates and not just by ID. It's also simple to get everything downstream from a point simply by using `(n)-[:down*]->(d)` in the query above for the `MATCH`.

To turn this into the fun web app, I wrapped the query into a Flask app, and am serving the results at a simple little API endpoint that you can try for yourself: e.g. [https://water.rdrn.me/api/1002300140/](https://water.rdrn.me/api/1002300140/).

To make it clicky and pretty, I loaded the million basin geometries into Mapbox and wrote some Javascript to filter the geometries based on the IDs that come back from the API. All the latitude-longitude and geometry stuff happens on the frontend to take the load off the little server I'm renting, but it would be trivial to add an API endpoint that accepts coordinates and returns a geometry.

{% include image.html url="/assets/images/2020/basin-geom.png" description="And we get this map for same point in the Breede River as the graph above. Red is the upstream drainage basin, and blue is downstream." %}

[Give it a try!](https://water.rdrn.me/)
