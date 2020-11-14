---
layout: single
title: "Optimising I: Sampling rasters"
date: "2020-11-15"
excerpt: "If you ain't first yet last!"
---

This week I needed to do some geospatial processing, and it needed to go fast. One million locations, with 15,000 days of data, and three variables. We need to get the values for each location on each day (from a huge pile of raster images), and stuff it all into a big database. In the end we'll have 15 billion rows, with three variable columns, and some extra columns with the date, location etc. Almost 100 billion individual values to be written.

Something like this:

| Date       | Location | Var_1 | Var_2 | Var_3 |
| ---------  | -------- | ----- | ----- | ----- |
| 2010-11-14 | 1        | 0.456 | 1.234 | 3.823 |
| 2010-11-15 | 1        | 0.500 | 1.432 | 4.012 |
| 2010-11-14 | 2        | 0.988 | 1.675 | 2.112 |
| ...        | ...      | ...   | ...   | ...   |

Then when we want to know the values for a group of locations, instead of doing all the sampling and figuring out, we just pull it from the database!

There are a few steps to this process:
1. Load the rasters that contain the raw data
2. Get the latitude/longitude of the points
3. Sample the rasters at each point
4. Tabulate this data
5. Shove it into a database

Step 1 depends on where we're getting the data from (the cloud, in this case) and step 2 comes for free because we already have the coordinates. But the rest were ripe for optimisation! I'm going to go through how I sped up 3-4 in the first section, and then step 5 in the next section.

## Raster sampling (zonal statistics)
This is a common GIS problem: we have location and raw data, and we want to know the values (mean, max, etc) at each location. If the location are polygons, this involves a bit of figuring out. In this case we got the centroids for each polygon, so we just have a simple lat/lon point to work with. In this case, instead of a flat raster, we have four-dimensional "cube" of data: dates along the first axis, then the three variables, and then x- and y-coordinates.

While speeding up this code, I decided to have some fun benchmarking it to see how much faster it could get. I obviously couldn't do this with the full 15 billion rows, so I worked with a subset. But I still wanted to get an idea of how different approaches scaled on different axes, so I did it with multiple input data sizes.

{% include image.html url="/assets/images/2020/opt1-cube.png" description="So many axes" %}

In this case, although number of days and number of variables definitely have an influence, number of locations is the largest dimension and probably the most important. So to avoid having 4D charts all over the place, I'm sticking with that. I wrote a little function that tests each function at a range of locations from 1 to 10,000, and runs it four times for each , taking the fastest run for each. I'm keeping to 365 days (a.k.a. a year) for each one to keep the runs short enough.

## Rasterstats
The obvious tool for zonal statitics is [rasterstats](https://pythonhosted.org/rasterstats/index.html), so that's where I started. It has a clear downside that it can only operate on one 2D raster at a time, so we have to manually loop through each data and each variable in our 4D cube.

So here's a little function that does that. Note, in this and subsequent code blocks, I'm leaving out some code to keep things to the barebones if what's being benchmarked. This includes additional columns to specify date and location, setting data types to control memory usage and others. All the functions will have the same function signature as the below -- `def name(locs, cube, aff)` -- and should return the exact same table.

```python
def rasterstats(locs, cube, aff):
    dfs = []
    for d in range(cube.shape[0]):
        res = {}
        for v in range(cube.shape[1]):
            s = zonal_stats(locs, cube[d, v, :, :], stats="mean", affine=aff)
            res[v] = [x["mean"] for x in s]
        dfs.append(pd.DataFrame(res))
    return pd.concat(dfs)
```
<div class="aside"><div>This was too slow to run for even 365 days, so I ran it for just one day. Even so, it took 6 minutes for 10,000 points. That would be 6000 days for the whole dataset!</div></div>

## Manual
Clearly `rasterstats` was not designed for this application. Instead, let's pull the values out manually. The key thing is that we have lat/lon coordinates (e.g. 28°S 127°E is somewhere in Australia), and we need to convert those to a row/column coordinate to pull the right value out of the raster/array. But once we have that, the magic of NumPy will let us pull out multiple days (thousands of days!) and variables in one go.

Let's see. Here we're using [rasterio](https://rasterio.readthedocs.io/en/latest/index.html) to create a virtual 'raster' from the cube, and then use its `index()` function to do the lat/lon => row/col conversion I just described.

```python
def manual(locs, cube, aff):
    with MemoryFile() as m:
        h, w, d = cube.shape[-2], cube.shape[-1], cube.dtype
        ds = m.open(driver="GTiff", count=1, height=h, width=w, dtype=d, transform=aff,)
    dfs = []
    for idx, row in locs.iterrows():
        x, y = ds.index(row.geometry.x, row.geometry.y)
        res = cube[:, :, x, y]
        res = pd.DataFrame(res)
        dfs.append(res)
    return pd.concat(dfs)
```

<div class="aside"><div>This got it down to 3.9 seconds for a full year (365 days) -- already about 5,000 times faster!</div></div>

## Latlon
Doesn't seem necessary for the function to have the full `GeoDataFrame` geometries, let's just send the x- and y-coordinates directly. We can pre-calculate them at the beginning and then re-use them again and again. Note that `locs` is now an array, not a `GeoDataFrame`.

```python
def latlon(locs, cube, aff):
    with MemoryFile() as m:
        h, w, d = cube.shape[-2], cube.shape[-1], cube.dtype
        ds = m.open(driver="GTiff", count=1, height=h, width=w, dtype=d, transform=aff,)
    dfs = []
    for i in range(len(locs)):
        row, col = ds.index(locs[i][0], locs[i][1])
        res = cube[:, :, row, col]
        res = pd.DataFrame(res)
        dfs.append(res)
    df = pd.concat(dfs)
    return df
```
<div class="aside"><div>Now down to 2.1 seconds.</div></div>

## No Pandas
I spotted another bottleneck: creating a whole Pandas `DataFrame` in each loop. Pandas makes everything extremely easy, but as always with such abstractions, bring a bit of overhead with it.

So I took the `DataFrame` stuff out of the loop, and just stuffed it all into a `DataFrame` right at the end instead. I also changed `locs` again: now it's two separate arrays of ox x-values and y-values.

```python
def nopandas(locs, cube, aff):
    xs, ys = locs
    with MemoryFile() as m:
        h, w, d = cube.shape[-2], cube.shape[-1], cube.dtype
        ds = m.open(driver="GTiff", count=1, height=h, width=w, dtype=d, transform=aff,)
    res = []
    for i in range(len(xs)):
        row, col = ds.index(xs[i], ys[i])
        res.append(cube[:, :, row, col])
    df = pd.DataFrame(np.concatenate(res))
    return df
```

<div class="aside"><div>An order of magnitude drop to 0.27 seconds!</div></div>

## Don't use Rasterio
Creating that `rasterio` dataset seems unnecessary, when all we want from it is the `index()` function. I had a look at the source, and lo, it's basically just one line. So I ditched it and just wrote out that line myself.

```python
def norasterio(locs, cube, aff):
    xs, ys = locs
    res = []
    for i in range(len(xs)):
        col, row = ~aff * (xs[i], ys[i])
        res.append(cube[:, :, floor(row), floor(col)])
    df = pd.DataFrame(np.concatenate(res))
    return df
```
<div class="aside"><div>Shaved some more off, to 0.20 seconds.</div></div>

## No Affine
The whole time, `aff` has been an [Affine](https://github.com/sgillies/affine). Baically a matrix with some special helpers that does the job of translating between lat/lon and row/col. I looked into how it works, and just did the matrix multiplication myself.

```python
def noaffine(locs, cube, aff):
    xs, ys = locs
    invaff = tuple(~aff)
    sa, sb, sc, sd, se, sf, _, _, _ = invaff
    res = []
    for i in range(len(xs)):
        col, row = (xs[i] * sa + ys[i] * sb + sc, xs[i] * sd + ys[i] * se + sf)
        res.append(cube[:, :, floor(row), floor(col)])
    df = pd.DataFrame(np.concatenate(res))
    return df
```
<div class="aside"><div>A small drop to 0.19 seconds.</div></div>

## Compiling Just-in-Time
Normally Python 'interprets' code: as it goes, it figures out what that means in machine language and then runs it. But in this case I'm running a snippet of code thousands of times - why not compile it once and then don't have to do all this interpreting. A library called [Numba](https://numba.pydata.org/) makes this extremely easy. Just decorate the function with `@jit`! The code inside the function here is exactly the same.

```python
@jit
def jitted(locs, cube, aff):
	...
```
<div class="aside"><div>No improvement. Numba couldn't do much with that.</div></div>

## No more fancy objects
One of the thing that makes Python easy is that anything can be just about anything. But to really squeeze out every drop of performance, we want a bit of predictability in the underlying representation. Numba offers this through `@njit`, where everything is only allowed to be integers, floats, etc, and arrays of these.

Now I had to add a wrapper function, as Affines, DataFrames, list appending and things like that aren't allowed inside the `njitted` function. The outer function is called directly, and the inner `_njitted()` does the number crunching. Notice how now the arrays are set with a pre-configured size, and results are neatly slotted in.

```python
@njit
def _njitted(xs, ys, cube, invaff):
    sa, sb, sc, sd, se, sf, _, _, _ = invaff
    num_points = len(xs)
    num_scenes = cube.shape[0]
    num_bands = cube.shape[1]
    avals = np.empty((num_points * num_scenes, num_bands), dtype=np.float32)
    for i in range(num_points):
        col, row = (xs[i] * sa + ys[i] * sb + sc, xs[i] * sd + ys[i] * se + sf)
        res = cube[:, :, floor(row), floor(col)]
        avals[i * num_scenes : (i + 1) * num_scenes, :] = res
    return avals

def njitted(locs, cube, aff):
    xs, ys = locs
    invaff = tuple(~aff)
    avals = _njitted(xs, ys, cube, invaff)
    df = pd.DataFrame(data=avals)
    return df
```
<div class="aside"><div>Now we're talking! 0.16 seconds.</div></div>

## Parallel
The calculation is basically doing the same thing thousands of times, and each calculation does not depend on any other. The perfect opportunity to run them all in parallel, i.e. on different threads and cores in the processer. Once again, Numba makes this extremely easy, just add `parallel=True` and replace `range` with their special `prange`.

```python
@njit(parallel=True)
def _parallel(xs, ys, cube, invaff):
    ...
    for i in prange(num_points):
        ...

def parallel(locs, cube, aff):
    ...
```
<div class="aside"><div>This got it down to 0.09 seconds! And should make even more difference on the cloud with a 32 core processor!</div></div>

All in all a 5,000x speed-up from dropping `rasterstats`, and another 50x speed-up from the remaining optimisations. A total of 250,000 times faster!

{% include image.html url="/assets/images/2020/opt1-chart.png" description="Amazing" %}

And will get even better with more data!
