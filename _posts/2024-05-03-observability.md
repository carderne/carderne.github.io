---
layout: single
title: Observability in 2024
date: 2024-05-03
excerpt: OpenTelemetry on the up and up
---
About every six months I Google something to the effect of "wtf is OpenTelemetry". Then I asked GTP-4. Now I ask Claude. Even though it's the _latest thing_, OTel always gave me corporate vibes. Dense documentation, no idea what anything is, like something from the Apache ~~graveyard~~ umbrella.

Today my semi-annual ritual was prompted by the announcement of [Pydantic's Logfire](https://news.ycombinator.com/item?id=40212490), which is some kind of frontend-backend thingie around OpenTelemetry. I feel like a few things finally grokked for me, so I'm sharing some notes for posterity.

## Concepts
Observability has coalesced around three main concepts:
1. **Logs**: you probably know about these. `console.log`, `logger.warn` and just plain `println`. If you're ~~lazy~~ agile, these get dumped to stdout and you scroll around until you find what you're after. If you're a bit more organised, you send them (preferably structured) to something like Axiom or Elastic, where you can query and visualise them.
2. **Metrics**: counts, gauges and histograms. How many bloops per time period, average request response time, p95s, that kind of thing. This is where Prometheus (plus Grafana) is the default choice. You sprinkle little counters and gauges around your code, and then you ask ChatGPT to write some PromQL and you populate some dashboards with pretty lines and bars and things. Metrics are super useful for performance monitoring (more on that shortly).
3. **Traces**: the sexy end of the observability stack. [Jaeger](https://www.jaegertracing.io/) seems to be the current cool-kid for traces. The idea is to trace a request/process through multiple systems: frontend, through a bajillion microservices, around databases and basically give a contextual, view of what the hell is going on, focusing on data over the boring messages that logs give you. The individual portions of a trace are called _spans_, btw.

There's a bonus fourth one:
4. **Error tracking**: this is basically monopolised (in the sort-of sexier than Azure, cheaper than DataDog space) by [Sentry](https://sentry.io/), which makes it super easy to send highly contextualised errors and stack traces to their dashboard where errors are grouped and sorted.

Sometimes you'll want to sample these things (especially metrics) rather than recording every single thing. This decision can happen at the start of an event (reduce compute) or at the end (reduce bandwidth) or in the persistence layer (reduce storage). But depending on your scale and retention needs, it's likely feasible to just record everything.

One note: these 3/4 concepts _frequently_ overlap! If you record something in your code somewhere, you can probably make a decent argument for it being processed in any one of the above four ways.

## Approaches
So it seems that there are basically four broad ways of ticking these boxes:
1. 🏢 **Use what your cloud gave you:** GCP, AWS and Azure all have things, and if that's your bag then go for it.
2. 💰 **The credit card method:** DataDog and NewRelic seem to be the obvious choices for teams that don't mind lock-in, have lots of cash, and just want a single easy solution with an after-sales rep hanging around to keep things rolling.
3. 🔥 **Bag of tricks:** basically cobble together the different tools I mentioned above under Concepts. Something for logs, Prometheus for metrics, and Jaeger/similar for traces. And probably you'll start with logs, add a decent log analytics tool when you realise scrolling sucks and set up Prometheus when p95s become important. Sentry arguably obviates the need for another tracing tool, and it's just so easy to set up. There's also the infrastructure layer to think about, and service meshes like [Istio](https://istio.io/) will give you a bunch of metrics out of the box, but they're pretty low-context.
4. 😎 **OpenTelemetry:** the point of this stupid blog post! OpenTelemetry promises to give you most of what the above offer, with better DevEx and without the enormous costs and vendor lock-in of some of them.

## OpenTelemetry?
OpenTelemetry officially went GA (General Availability) in late 2023 and, from a skimming of Reddit and Hacker News, seems to be winning over mindshare. Since you'll never figure out from its home page how it works, I'll tell you.

As I mentioned, logs/metrics/traces (and errors) are all quite similar. So OpenTelemetry just does them all in a cobweb of systems for creating, exporting and collecting them.
1. **Create:** SDKs in a [bunch of languages](https://opentelemetry.io/docs/languages/) to create traces, metrics and logs. Having only looked at the Python offering, I wouldn't call it lovely. But it does seem built to be very extensible (more on that in a bit.)
2. **Export:** there are a bunch of ways you can get your metrics and traces out of your code. `stdout` or JSON files or over the network with gRPC or probably a hundred other ways.
3. **Collect:** this isn't compulsory unless you're running multiple services, but this basically brings together all your exported stuff and makes it available for storage. And this is where it gets clever. You can continue to use Prometheus and Jaeger and DataDog, or dump everything to ClickHouse or all of the above or whatever.

{% include image.html url="/assets/images/2024/otel.png" description="Create, Collect, Store, Explore" class="" %}

One additional clever thing that OpenTelemetry does: auto-instrument common libraries. So if you have a Python service using FastAPI, SQLAlchemy, Requests etc, OTel will inject itself into all those libraries and automatically give you traces with spans covering your request, database interactions etc. Out of the box probably a lot more useful than whatever `print("Loaded data {data=}")` you were planning to do...

The other big change is basically deprecating logs in favour of traces, since the latter are basically logs plus data and context. So at the most basic, instead of logging something, stick it in a relatively empty trace and it should grow more useful with time. Then you can basically simplify the stack to metrics and traces only. And lots of what metrics give you can be figured out with traces anyway, with some caveats. If your scale isn't huge and your storage is cheap, you can basically persist all your traces for some period, and calculate most metrics from those.

## Recommendations
If I was starting a new project/team tomorrow and wanted to set things up in a decent, low-effort way.

Start with just Sentry and whatever plain logging system you like. It's dead-easy, gives you traces when you want them (errors), great error dashboard, and useful per-route performance stuff to boot that means you can delay setting up another metrics system.

As soon as it matters, skip Prometheus et al and set up OpenTelemetry with basic auto-instrumented traces and convert your logs to spans. You basically have two options for how you go about this:  
1. Self-host: use OpenTelemetry's libraries, persist your data in ClickHouse and use something like [SigNoz](https://github.com/SigNoz/signoz) for your UI.  
2. SaaS: [Logfire](https://pydantic.dev/logfire) (the inspiration for this post) and [HyperDX](https://www.hyperdx.io/) are both built on top of OpenTelemetry, provide a bit of sugar on the library side and sort out the storage and UI for you.
