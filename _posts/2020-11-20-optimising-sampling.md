---
layout: single
title: "Optimising Part I: Sampling rasters"
date: "2020-11-20"
excerpt: "If you ain't first yer last!"
---

*This is Part I, which looks at different methods of sampling array data at points. [Part II is here](/optimising-sql/) and focuses on the next step: getting it all into a database.*

This week I needed to do some geospatial processing, and it needed to go fast. One million locations, with 15,000 days of data each, all for three different climate variables. The raw data is several TB of raster images in the cloud somewhere, and we want our sampled data to end up in a well-organised database somewhere.

In the end we'll have 15 billion rows, with three variable columns, and some extra columns with the date, location etc. Almost 100 billion individual values to be written. Something like this:

| Date       | Location | VarA | VarB | VarC |
| ---------  | -------- | ----- | ----- | ----- |
| 2010-11-14 | 1        | 0.456 | 1.234 | 3.823 |
| 2010-11-15 | 1        | 0.500 | 1.432 | 4.012 |
| ...        | ...      | ...   | ...   | ...   |
| 2010-11-14 | 2        | 0.988 | 1.675 | 2.112 |
| ...        | ...      | ...   | ...   | ...   |

Then, when we want to know the values for a group of locations, instead of doing all the sampling and figuring out, we just pull it from the database!

Let's have a look at how to get this data out, or you can skip ahead to [Part II](/optimising-sql/) if you're more interested in SQL and Postgres.

<!--{% include fn.html n=1 %}-->

# Raster sampling (zonal statistics)
This is a common GIS problem: we have a bunch of locations (generally points or polygons) and raw raster data ([what's a raster](https://docs.qgis.org/2.8/en/docs/gentle_gis_introduction/raster_data.html)), and we want to know the values (mean, max, etc) at each location. If the location are polygons, this involves a bit of figuring out. For this exercise we're just using points with latitude/longitude for each location.

A normal two-dimensional raster is basically a big grid of values, with an x- and a y-coordinate for each cell in the grid. In the example below, it's a 4x4 grid with a single integer in each location. In Python this would generally be stored in a [Numpy](https://numpy.org/) array. In this case, I've used a red colour gradient to colour cells by increasing value. To get an RGB picture, you instead need *three* values for each pixel.

{% include image.html url="/assets/images/2020/opt1-arr.png" description="A very small raster, with a number value for each pixel, and how it might be displayed on a red gradient. The numbers outside the square are the row- and column-indices." class="narrow-img" %}

So all raster data is just much bigger versions of this. If I want a particular value, I just use the row- and columns indices, e.g. `arr[2, 1] => 9`. (Remember that in most coding, numbering starts at `0`.) You can also pull out larger chunks of data, e.g. `arr[2, :] => [3, 9, 3, 2]` pulls out the whole row!

Instead of a flat, two-dimensional raster, we have a four-dimensional "hypercube" of data: dates along the first axis, then the three variables, and then the x- and y-coordinates that we're already familiar with. Now if we want a certain value, we instead pass *four* indices. So if we for example wanted the first date, all three variablse, and again the bottom-leftish value, we might do `arr[0, :, 2, 1] => ...`.

# Benchmarking
While working on this problem, I decided to have some fun benchmarking it to keep track of my progress. I obviously couldn't do this with the full 15 billion rows, so I worked with a subset, and tried with different amounts of data, ranging from a single point up to a million (only for the fastest methods!). If you prefer, head over to the [benchmark suite on GitHub](https://github.com/carderne/benchmarking-sampling/blob/main/benchmark_sample.ipynb). You should be able to clone the repo and run the entire suite in a few minutes.

<div class="aside"><div>The results for each approach are shown in the text on the side!</div></div>

# Round 1: Rasterstats
The obvious tool for zonal statistics is [rasterstats](https://pythonhosted.org/rasterstats/index.html), so that's where I started. It has a clear downside: it only operates on one 2D raster at a time, so we have to manually loop through each data and each variable in our 4D cube.

So here's a little function that does that. Note, in this and subsequent code blocks, I'm leaving out some code to keep things to the barebones if what's being benchmarked. This includes additional columns to specify date and location, setting data types to control memory usage and others. All the functions will have the same function signature as the below -- `def name(locs, cube, aff)` -- and should return the exact same table.

```python
def rasterstats(locs, cube, aff):
    dfs = []
    for d in range(cube.shape[0]):
        res = {}
        for v in range(cube.shape[1]):
            # rasterstats can do much more than just mean, it's great stuff
            s = zonal_stats(locs, cube[d, v, :, :], stats="mean", affine=aff)
            res[v] = [x["mean"] for x in s]
        dfs.append(pd.DataFrame(res))
    return pd.concat(dfs)
```
<div class="aside"><div>This was too slow to run for even 365 days, so I ran it for just one day. Even so, it took 6 minutes for 10,000 points. That would be 6000 days for the whole dataset!</div></div>

# Round 2: Manual sampling
Clearly rasterstats was not designed for this application. Instead, let's pull the values out manually. The key thing is that we have lat/lon coordinates (e.g. 28°S 127°E is somewhere in Australia), and we need to convert those to a row/column coordinate to pull the right value out of the array. But once we have that, the magic of NumPy will let us pull out multiple days (thousands of days!) and variables in one go.

Let's see. Here we're using [rasterio](https://rasterio.readthedocs.io/en/latest/index.html) to create a virtual 'raster' from the cube, and then use its `index()` function to do the lat/lon => row/col conversion I just described.

```python
def manual(locs, cube, aff):
    with MemoryFile() as m:
        h, w, d = cube.shape[-2], cube.shape[-1], cube.dtype
        ds = m.open(driver="GTiff", count=1, height=h, width=w, dtype=d, transform=aff,)
    dfs = []
    for idx, row in locs.iterrows():
        # Convert lat/lon to row/col and use it in our NumPy array
        row, col = ds.index(row.geometry.x, row.geometry.y)
        res = cube[:, :, row, col]
        res = pd.DataFrame(res)
        dfs.append(res)
    return pd.concat(dfs)
```

<div class="aside"><div>This got it down to 3.2 seconds for a full year (365 days) and 10,000 points -- already about 5,000 times faster!</div></div>

# Round 3: No GeoPandas
In the function above, `locs` is a `GeoDataFrame`: basically a Pandas `DataFrame` + geometry. Look these up if that's gibberish. It doesn't seem necessary to pass all that through, so let's just send the x- and y-coordinates directly. We can pre-calculate them at the beginning and then re-use them again and again. So in the function below, `locs` is now a simple array of x- and y-coordinates.

```python
def latlon(locs, cube, aff):
    with MemoryFile() as m:
        h, w, d = cube.shape[-2], cube.shape[-1], cube.dtype
        ds = m.open(driver="GTiff", count=1, height=h, width=w, dtype=d, transform=aff,)
    dfs = []
    for i in range(len(locs)):
        # These simple array lookups are always faster than stuff with names
        row, col = ds.index(locs[i][0], locs[i][1])
        res = cube[:, :, row, col]
        res = pd.DataFrame(res)
        dfs.append(res)
    df = pd.concat(dfs)
    return df
```
<div class="aside"><div>Now down to 1.7 seconds.</div></div>

# Round 4: No Pandas
We got a speed boost by dropping one use of Pandas, let's do more. It was creating a new Pandas `DataFrame` in each loop. As is often the case, these higher-level abstractions bring a bit overhead with them that can start to matter in cases like this.

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
    # why make a million DataFrames when one will do!
    df = pd.DataFrame(np.concatenate(res))
    return df
```

<div class="aside"><div>An order of magnitude drop to 0.19 seconds!</div></div>

# Round 5: Drop Rasterio
All that `MemoryFile` stuff with the `rasterio` dataset seems unnecessary, when all we want from it is the `index()` function. I had a look at the source, and lo, it's basically just one line. So I ditched it and just wrote out that line myself.

```python
def norasterio(locs, cube, aff):
    xs, ys = locs
    res = []
    for i in range(len(xs)):
        # One line of matrix-multiplication magic
        col, row = ~aff * (xs[i], ys[i])
        res.append(cube[:, :, floor(row), floor(col)])
    df = pd.DataFrame(np.concatenate(res))
    return df
```
<div class="aside"><div>Shaved some more off, to 0.13 seconds.</div></div>

# Round 6: No Affine
The whole time, `aff` has been an [Affine](https://github.com/sgillies/affine). Basically a matrix with some special helpers that does the job of translating between lat/lon and row/col. I looked into how it works, and just did the matrix multiplication myself. Have a look at [perrygeo](https://www.perrygeo.com/python-affine-transforms.html) if you want see how this stuff works.

```python
def noaffine(locs, cube, aff):
    xs, ys = locs
    invaff = tuple(~aff)
    sa, sb, sc, sd, se, sf, _, _, _ = invaff
    res = []
    for i in range(len(xs)):
        # Each of these letters stands for something...
        col, row = (xs[i] * sa + ys[i] * sb + sc, xs[i] * sd + ys[i] * se + sf)
        res.append(cube[:, :, floor(row), floor(col)])
    df = pd.DataFrame(np.concatenate(res))
    return df
```
<div class="aside"><div>A small drop to 0.12 seconds.</div></div>

# Round 7: Compiling Just-in-Time
Normally Python 'interprets' code: as it goes, it figures out what each bit means in machine language and then runs it. But in this case I'm running a snippet of code thousands of times - why not compile it once and then skip all that interpreting. A library called [Numba](https://numba.pydata.org/) makes this extremely easy. Just decorate the function with `@jit`! The code inside the function here is exactly the same.

```python
@jit
def jitted(locs, cube, aff):
    # Same exact function code as above
    ...
```
<div class="aside"><div>No improvement. Numba couldn't do much with that.</div></div>

# Round 8: No more fancy objects
One of the thing that makes Python easy is that anything can be just about anything. But to really squeeze out every drop of performance, we want a bit of predictability in the underlying representation. Numba offers this through `@njit`, where everything is only allowed to be integers, floats, etc, and arrays of these.

Now I had to add a wrapper function, as Affines, DataFrames, list appending and things like that aren't allowed inside the `njitted` function. The outer function is called directly, and the inner `_njitted()` does the number crunching. Notice how now the arrays are set with a pre-configured size, and results are neatly slotted in. The code starts to get significantly less readable around here...

```python
@njit
def _njitted(xs, ys, cube, invaff):
    # This is the inner function
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
    # And this is the un-jitted wrapper
    xs, ys = locs
    invaff = tuple(~aff)
    avals = _njitted(xs, ys, cube, invaff)
    df = pd.DataFrame(data=avals)
    return df
```
<div class="aside"><div>Now we're talking! 0.11 seconds.</div></div>

# Round 9: In parallel this time
The calculation is basically doing the same thing thousands of times, and each calculation does not depend on any other. The perfect opportunity to run them all in parallel, i.e. on different threads and cores in the processor. Once again, Numba makes this extremely easy, just add `parallel=True` and replace `range` with their special `prange`.

```python
@njit(parallel=True)
def _parallel(xs, ys, cube, invaff):
    # All the same in here
    ...
    for i in prange(num_points):
        ...

def parallel(locs, cube, aff):
    # Here too
    ...
```
<div class="aside"><div>This got it down to 0.08 seconds! And should make even more difference on the cloud with a 32 core processor!</div></div>

# Round 10: Off the deep end
These functions have all been creating `DataFrames`. If that isn't a hard requirement, we can probably eke out a bit more speed (and lower memory use from less copying) using NumPy [Structured Arrays](https://numpy.org/doc/stable/user/basics.rec.html), which provide labelled "columns" like Pandas, with less overhead.

Once again, we have an inner `jit`ed function, within a wrapper. Note also that the empty array is created in the wrapper and passed into the inner function, because Numba doesn't play nice with all data types.
```python
@njit(parallel=True)
def _recarrays(xs, ys, cube, invaff, rec):
    sa, sb, sc, sd, se, sf, _, _, _ = invaff
    num_scenes = cube.shape[1]
    for i in prange(len(xs)):
        col, row = (xs[i] * sa + ys[i] * sb + sc, xs[i] * sd + ys[i] * se + sf)
        res = cube[:, :, floor(row), floor(col)]
        fr = i * num_scenes
        to = (i + 1) * num_scenes
        # We can assign values to the array by name (A, B, C) which is quite nice
        rec.A[fr:to] = res[0]
        rec.B[fr:to] = res[1]
        rec.C[fr:to] = res[2]
    return rec

def recarrays(locs, cube, aff):
    xs, ys = locs
    invaff = tuple(~aff)
    cube = np.moveaxis(cube, 1, 0)
    rows = len(xs) * cube.shape[1]
    # A recarray/structure array is basically an array with multiple data types
    rec = np.empty(rows, dtype=[("A", "f4"), ("B", "f4"), ("C", "f4")])
    rec = _recarrays(xs, ys, cube, invaff, rec)
    return rec
```
<div class="aside"><div>And another boost down to 0.07 seconds!</div></div>

# Winner winner

All in all a 5,000x speed-up from dropping rasterstats, and another 50x speed-up from the remaining optimisations. A total of 250,000 times faster!

*Quick note: I'm not trying to knock rasterstats, Pandas, GeoPandas, rasterio or anything. These are all great libraries that I use every day. But there's a time and place for everything.*

{% include image.html url="/assets/images/2020/opt1-chart.png" description="No space for the rasterstats lines." %}

And will get even better with more data!


<!--{% include fnn.html n=1 note="" %}-->
