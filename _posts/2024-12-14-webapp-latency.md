---
layout: single
title: A boring latency investigation
date: 2024-12-14
---
I built a toy Next.js app as an excuse to play around with some stuff (like [React 19 forms](/react-forsm)). I had a form that would create a new object and then redirect to it. Mostly submit-to-loaded was <200ms, but occasionally it would spike to over one second, which is very much loading spinner territory. It seemed to mostly happen after not using the app for a few minutes. So I decided to investigate a bit.

<small style="color:gray">TLDR: unsurprisingly, the culprit was my mediocre internet slash DNS server. But it made for a fun investigation anyway.</small>

## Traces
First... well first I bumped the server and database specs to at least have a single core each (logical or physical? we'll never know). To at least reduce the likelihood that it's all just resource contention with some other persons's app.

Then I setup [Sentry](https://sentry.io/) as an easy way to get some distributed full-stack traces. These suggested that [node-postgres](https://node-postgres.com/)' `connect` was a potential culprit. So I set up a connection pool, configured it to never terminate connections, and swapped in [pg-native](https://node-postgres.com/features/native). There was some marginal improvement but I was still seeing the occasional spike in latency. I set up a simple API with some manual traces to remove React rendering and the data transfer as possible culprits. An example trace is shown below, and I never saw the time for the core logic of this route go above 35 ms. I wasn't being at all careful with queries (using [Drizzle](https://orm.drizzle.team/), fwiw) and this proves that's the right decision: each one is ~2 ms, so I could add 20 more and it would hardly matter.

{% include image.html url="/assets/images/2024/sentry.png" description="" class="narrow-img" %}

I think this is also shows the advantage of colocating your server and database (on [Render](https://render.com/), in this case). There are plenty of fancy modern database/backend tools ([Supabase](https://supabase.com/), [Turso](https://turso.tech/), [Neon](https://neon.tech/) and 20 more) but if you just use them like a normal database from your backend, and aren't careful about where they're physically located, you might just add a bunch of milliseconds to every single query.

## Synthetic tests
So I wondered if the actual navigation or React-y stuff was slowing things down and set [Checkly](https://www.checklyhq.com/) to work filling out and submitting my form every 5 minutes. Checkly doesn't seem very well set up for performance monitoring (unless I also ship my traces to them), but I never saw the full submit-reload go much above 250 ms.

```typescript
const { expect, test } = require('@playwright/test')

test.setTimeout(5000)
test('form-submit', async ({ page }) => {
  await page.context().addCookies([{ ... }])
  await page.goto('https://.../new')
  await page.locator('button[aria-label="Add"]').click()
  await page.locator('div[data-value="Foo"]').click()
  await page.locator('textarea[name="content"]').fill('Hello')

  const start = Date.now()
  const [submitResponse] = await Promise.all([
    page.waitForResponse(response =>
      response.url().includes('/new') &&
      response.request().method() === 'POST'),
    page.locator('form').evaluate(form => form.submit())
  ])
  expect(submitResponse.status()).toBe(303)
  await page.waitForLoadState('networkidle')
  
  const end = Date.now()
  console.log({ duration: end - start })
})
```

So clearly the form is fine... and my internet is wonky. But I wanted to see what was actually going on, and neither Sentry nor Checkly provided enough detail on what was sucking up the time when there was a slow response.

## Curl
I wrote (well, Claude wrote) a little script to GET the API route, then immediately again, then sleep for 5 minutes and repeat. Wondering whether it would be slower after 5 minutes of inactivity. This is easy in my case, because no one else is using my toy app 😄.

```bash
while true; do
    curl 'https://.../api' -w '%{json}' \
      | jq -s 'add + {clock: now}' \
      >> data.json
    # repeat
    sleep 300
done
```

I ran this for an hour or two on my laptop over WiFi and my mediocre internet. I also ran it on a Hetzner box in Falkenstein, about a four-hour drive from my app server in Frankfurt. See the results below, showing the histogram of time taken (in milliseconds) for each operation. "Core logic" is measured and returned by the app, the rest are recorded by curl.

A couple of interesting things (to me at least):
- The **Core logic** slowed down by about 10ms because I removed `pg-native`. So the eight queries are each about a millisecond slower.
- The initial **TCP connection** was always <10ms on Hetzner, but all over the place on my laptop. Presumably because of the lower latency connection for the back-and-forward (thanks [zoomie](https://github.com/zoomie/) for pointing this out).
- If you look closely at the **DNS  lookup** for my laptop, you can see the tail lifting again at 200 ms. I think this is ultimately what was causing my latency: I'm currently experimenting with [Eero's ad-blocking](https://eero.com/eerosecure), and presumably it has a low cache TTL, so it's looking up the domain again after a few minutes. But I'm surprised Hetzner also had a tail at almost 100ms.
- The **SSL handshake** is about four times faster on my laptop: presumably my Apple M2 running circles around a little Hetzner single-core box (again, thanks [zoomie](https://github.com/zoomie/)).
- The time to **Send first byte** I think are much the same, the spread is probably just wider for Laptop because I got far more data points (sorry, Science). Note that this excludes the DNS/TCP/SSL steps. Median of 100 ms in either case, which isn't bad for a little Node backend doing a bunch of database queries.
- And then the **Total time** is much the same.

{% include image.html url="/assets/images/2024/curl.png" description="All times in milliseconds" class="" %}