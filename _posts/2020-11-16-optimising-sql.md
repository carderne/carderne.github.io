---
layout: single
title: "Optimising II: blazing SQL"
date: "2020-11-16"
excerpt: "Turns out a billion insert statements isn't the best way."
---

# Putting it all in the database
Now that I got the sampling process down to basically instantaneous, the database insertion became the main bottleneck. I'm pretty handy with NumPy and Python in general, but have never had the excuse to really tinker with database performance before. I'm going over the methods I tried below, but note that I didn't at all play with database settings or configuration: I purely wanted to see how much I could improve by changing the `INSERT` method. Also note that our use-case is using a cloud database, so the data has to traverse a network (hopefully not to much) in addition to everything else.

```sql
CREATE TABLE test (
    date integer,
    loc integer,
    varA real,
    varB real,
    varC real,
    UNIQUE (date, loc)
)
```

As with the raster sampling, I set up a simple benchmarking tool that also handles the setting-up and tearing-down of the database, and makes sure everything commits. I'm using `psycopg2` to connect to a Postgres database. Running the benchmarks on my local machine, so I'm not testing for network latency unfortunately (forunately?).

## Insert statements
First up, a simple dumb insert. Loop through the `DataFrame` row by row and insert the values.

```python
def insert(df, table):
    for _, row in df.iterrows():
        cur.execute(
            f"""
            INSERT INTO {table} (date, loc, varA, varB, varC)
            VALUES (%s, %s, %s, %s, %s)
            """,
            row.tolist(),
        )
```
<div class="aside"><div>Unsurprisngly, slow: 182 seconds for a million rows.</div></div>


## execeute_values
A quick Google and [this link](https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/) suggested that `psycopg2.extra.execute_values()` would be the fastest 'normal' method.

Instead of looping through and `INSERT`ing again and again, it handles the rows under-the-hood, and al I need to do is through my array at it.

```python
def values(df, table):
    sql = f"INSERT INTO {table} (date, loc, varA, varB, varC) VALUES %s"
    extras.execute_values(cur, sql, df.values)
```
<div class="aside"><div>Much faster, at 38 seconds for the same rows.</div></div>

## Upsert
I also wanted to see what impact there would be from using Postgres's `UPSERT` syntax. This allows for new data to be inserted, and to replace existing rows if there's a match on any fields (`date` and `loc` in this case). This won't frequently happen for us, but it makes it a bit easier to automatically deal with if we accidentally re-insert some existing rows.

It looks like this.

```python
def upsert(df, table):
    sql = f"""
    INSERT INTO {table} (date, loc, varA, varB, varC) 
    VALUES %s
    ON CONFLICT (date, loc)
    DO UPDATE SET varA = excluded.varA, 
                  varB = excluded.varB,
                  varC = excluded.varC;
    """
    extras.execute_values(cur, sql, df.values)
```
<div class="aside"><div>I didn't test it with any conflicting data. But doesn't cause much of a slowdown here. Up to 41 seconds, for a 10% slowdown.</div></div>

## Copying
The same link also showed that using `COPY` would be the fastest. However, I was hesitatnt to try it initially, as it would mean first dumping everything to CSV, and then `COPY`ing that. This didn't seem ideal from a speed point of view, when the CSV could be 10's of GB at a time.

But `execute_values()` wasn't fast enough for our 15 billion rows to load in a reasonable amount of time, so I had to try it out.

```python
def copy(df, table):
    tmp = "tmp.csv"
    df.to_csv(tmp, index=False, header=False)
    f = open(tmp, "r")
    cur.copy_from(f, table, sep=",")
```
<div class="aside"><div>All inserted in 9.1 seconds!</div></div>

## Copy from memory
Why make the round-trip to disk when we can just go straight from memory (so long as there's enough!).

```python
def copy_mem(df, table):
    buff = StringIO()
    df.to_csv(buff, index=False, header=False)
    buff.seek(0)
    cur.copy_from(buff, table, sep=",")
```
<div class="aside"><div>Almost the exact same speed. Is my SSD really fast? Or my old 8GB's of RAM too slow...</div></div>

## Copy from memory, dealing with duplicates (upsert)
Once again, let's see what impact the `UPSERT` approach has. We can't do it natively with `COPY`, so we have to do it in three steps:
1. Create a temporary table
2. `COPY` into the temporary table
3. `UPSERT` from there into the main table

So let's add two functions for making the temp table, and then upserting to the main table.
```python
def make_temp(table, temp):
    cur.execute(
        f"""
    CREATE TEMP TABLE {name} ON COMMIT DROP
    AS SELECT * FROM {table} WITH NO DATA;
    """
    )

def temp_to_main(temp, table):
    cur.execute(
        f"""
    INSERT INTO {table}
    SELECT * FROM {temp}
    ON CONFLICT (date, loc)
    DO UPDATE SET varA = excluded.varA,
                  varB = excluded.varB,
                  varC = excluded.varC;
    """
    )
```

Now we can run the new function, using the above two, along with `copy_mem()` from above.

```python
def copy_mem_upsert(df, table):
    temp = "tmp"
    make_temp(table, temp)
    copy_mem(df, temp)
    temp_to_main(table, temp)
```
<div class="aside"><div>A 40% drop in performance. The benefit of the COPY is hit by having to go row-by-row.</div></div>

## Time for binary!
The problem with the above is that we have a `DataFrame` with each column carefully assigned a datatype of float32, int32 etc, but then we write it to CSV and everything just becomes text! So our value of 0.2436123, which occupied 4 bytes of float32, is now 9 horrible bytes of text. To make it worse, there's a large processing step in doing all this binary => text conversion. And even worse still, is that Postgres has to do the reverse on the other side!

Far better if everything stays in its native binary format. To do this, we need to make sure our `DataFrame` datatypes exactly match the datatypes specified for each column in the database table. We can't shove a float32 into a hole made for a float16. We also need to convert the Pandas/Numpy data into something that Postgres natively understands.

I found a [function](https://stackoverflow.com/a/8150329) on StackOverflow (where else), that does this second step. Basically what it takes is takes a Numpy [structured array](https://numpy.org/doc/stable/user/basics.rec.html) and converts it into the exact byte representation that Postgres expects, including the gibberish that begins and closes that representation.

```python
def prepare_binary(data):
    pgcopy_dtype = [("num_fields", ">i2")]
    for field, dtype in data.dtype.descr:
        pgcopy_dtype += [(field + "_length", ">i4"), (field, dtype.replace("<", ">"))]
    pgcopy = np.empty(data.shape, pgcopy_dtype)
    pgcopy["num_fields"] = len(data.dtype)
    for i in range(len(data.dtype)):
        field = data.dtype.names[i]
        pgcopy[field + "_length"] = data.dtype[i].alignment
        pgcopy[field] = data[field]
    byt = BytesIO()
    byt.write(pack("!11sii", b"PGCOPY\n\377\r\n\0", 0, 0))
    byt.write(pgcopy.tobytes())
    byt.write(pack("!h", -1))
    byt.seek(0)
    return byt
```

Now we can joyfully throw this at the database.

```python
def copy_bin(df, table):
    data = df.to_records(index=False)
    byt = prepare_binary(data)
    cur.copy_expert(f"COPY {table} FROM STDIN WITH BINARY", byt)
```
<div class="aside"><div>Another huge improvement to 2.9 seconds!</div></div>

## And one last upsert check
Let's just check what impact upserting has.
```python
def copy_bin_upsert(df, table):
    temp = make_temp(table)
    copy_bin(df, temp)
    temp_to_main(temp, table)
```
<div class="aside"><div>Horrible - a 128% slowdown to 6.6 seconds.</div></div>

## Wrapping it up

{% include image.html url="/assets/images/2020/opt2-chart.png" description="Amazing" %}
