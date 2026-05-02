---
layout: single
title: An open source story
date: 2026-05-01
---
A fun thing happened over the last few years. I contributed in a small way to part of the open source geospatial ecosystem.

## First, some background on geo

Zarr is a format for storing large multidimensional arrays on cloud storage (like S3). It plays well with xarray and NumPy, and lets you efficiently query small slices of multi-TB datasets. For many people and workflows, it's the spiritual successor to GeoTiff and [Cloud Optimizted GeoTiff](https://cogeo.org/). But one big downside with Zarr is that it doesn't have "pyramids" built-in (pre-created zoomed-out views), since it's designed much more for analysis than visualisation.

The Holy Grail is to have a single Zarr array covering the entire globe, where you can index into not only latitude and longitude, but also time, date, altitude etc. Instead of thousands of Tiffs and chips and images, just one beautiful global array. And the wine in the grail would then be the ability to natively visualise this data in the browser at any zoom level. Ideally without a server — that's the whole point of cloud-native after all. Someone wrote a whole [blog post](https://medium.com/@tobias.ramalho.ferreira/zarr-in-the-browser-fast-flexible-and-surprisingly-powerful-for-big-geo-data-eeb90ddf8a3d) about this, but it has some spoilers for the story below.

## My small contribution

For several years, the nice people at CarbonPlan had a project called [carbonplan/maps](https://github.com/carbonplan/maps). It sort of let you do this, but was more a proof-of-concept than a library that could be used.

I riffed on it a little bit and created [zarr-gl](https://github.com/carderne/zarr-gl) (rhymes with gargle). Much the same thing, slightly fewer dependencies and simpler WebGL code that I could at least understand (although still not very well). The main difference is that I made it a _library_ so that anyone could use it to drop a Zarr layer into a Mapbox/MapLibre map. Still quite clunky, couldn't reproject or use non-Mercator projections. I had a itch, went as far as the itch took me. Made a little [demo site](https://rainy.rdrn.me/). But then hit some hard problems and didn't have the pressing need to push through them.

It wasn't great, but it was timely and a step in the right direction. A few people noticed, and then the folks at CarbonPlan picked up the reins again and made [something](https://carbonplan.org/blog/zarr-layer-maps) [much better](https://github.com/carbonplan/zarr-layer). Now it's actually useful and workable!

And then shortly after that, Development Seed [added Zarr support](https://developmentseed.org/deck.gl-raster/blog/initial-geozarr/) to deck.gl, which should make it possible to do interesting client stuff (animation, band math).

And that's it. Everyone else involved was much more competent and dedicated than me, and ultimately no one would or should use my little thing because it's been superseded. But it was fun to be part of a tiny little shift in the Zeitgeist in a specific niche of the open source world. People started realising that a thing should be possible, and over the course of a few years it went from hacky to glorious through vague cooperation and tinkering of different groups of people.

## Other open source stories

I've had a few stabs at Open Sourcery in the last few years. I generally get a burst of inspiration in the autumn; summer's over, evenings are quieter, time to rev up the brain again.

Around the same time as zarr-gl, I created a new ID format called [UPID](https://github.com/carderne/upid). I thought it was genius! It is genius. I think. I [wrote about it here](./upid). But ultimately no one wants to install a custom Postgres extension just to get a new ID type. Even though they should.

I also worked on a tool for Python monorepo builds called [una](https://github.com/carderne/una). I was frustrated by the huge leap from ~nothing~ to Pants/Bazel, and tried to fill the gap. I was inspired by [python-polilith](https://github.com/DavidVujic/python-polylith) and actually created it by starting from that codebase, deleting almost everything, and working from there. In between sleepless nights with a few-week old baby. But then [uv](https://docs.astral.sh/uv/) came along, and although there is still technically a need for una (uv works fine for monorepo Docker builds, but not for wheels), I stopped having my problem and didn't have users and ran out of steam.

Then last year I started something quite ambitious: a [Drizzle ORM](https://orm.drizzle.team/) wannabe for Python called [Embar](https://github.com/carderne/embar). None of the Python ORMs are any good with types, so I set out to create one. It'll never be as good as Drizzle because Python isn't as powerful as TypeScript. But I think it's pretty good already! I hope to keep working on it in a slower way, but it's hard to push through having neither (a) a strong need nor (b) users clamouring for it.

Noticing a common refrain in this? I've read comments from famous open sourcers decrying those (like me, I guess) who give up on projects after a few months, or expect people to trust us. But it's an easy thing to say from the vantage of having such a following that _anything_ you build will get attention. Not to say success: but you'll have the eyeballs to pick up on the signals of likely long-term value. You have to really believe in what you're building to keep at it for years with 86 GitHub stars and little engagement.

The latest thing that excited me was [agent-sql](https://github.com/carderne/agent-sql/). Holy smokes, this is the one to go viral I thought. I even deployed the demo site [sql.rdrn.me](https://sql.rdrn.me/) to Cloudflare so that it wouldn't go down in the inevitable virality! It's a TypeScript library to sanitise SQL queries so you can safely run untrusted SQL (from a SaaS user or LLM agent, for example) against a multi-tenant database. I still plan to work further on it, but in the absence of external interest, it requires loads more effort to figure out the next steps to take.

I posted about it on Twitter and got a single like. However, that single like got me a job I'm super excited about, but more on that later.

## Maintainerships

On the flipside to the above, some (not many) of my projects have been _more_ successful than I'd like. Mostly the ones that I'm not particularly excited in working on.

[signal-export](https://github.com/carderne/signal-export) is a thing I created (well forked actually, though the original code is all gone) in 2019 when my family moved from WhatsApp to Signal and I needed a way to continue to do backups. It has slowly racked up 732 GitHub stars, and receives a steady stream of bug reports, pull requests, and also emails to my inbox filled with gratitude or questions needing answers. I use it myself once a year, and so long as it vaguely works I don't want to think about it more than that. The code is a mess. 

But the maintenance burden is small, I write virtually none of the code now, and the community keeps it up-to-date with Single's data model changes. And there's a fun give and take: I'm happy I don't have to do the work, and contributors seem generally excited to contribute some Open Source Code! And it's one area where LLMs have actually made the contributions better: it's no where near famous or important enough to attract slop, and now many people are able to fix small bugs or make updates. My job is just to make sure it remains safe to use. I don't really care about the codebase otherwise, so I'm not particularly opinionated.

I have a similar story with [pi-sandbox](https://github.com/carderne/pi-sandbox). It's a little plugin I made for the [pi coding agent](https://pi.dev) that sandboxes network and filesystem access. I made it for myself, fixed a bunch of issues, got some stuff merged in [Anthropic's sandbox-runtime library](https://github.com/anthropic-experimental/sandbox-runtime/pulls?q=is%3Apr+author%3Acarderne+is%3Aclosed). Then I forgot about it and when I looked back a month or two later I had 10+ issues and a similar number of PRs that I hadn't noticed! Almost all were good quality and I'm working my way through them. I'm glad people find it useful and want to improve it, but it's still undeniably _work_.

Much like signal-export, it's a sensitive bit of software. People are relying on it (within reason) to prevent AI agents from doing bad stuff. I really don't want to ship security vulnerabilities. But I also want to keep it good and up-to-date and honour the effort that community contributors are putting into issues and pull requests. And I also want to do my job and play outside and all that.

It's a tiny view into what maintainers of really popular projects have to deal with. Certainly a tricky one to balance. Soon I'll be working somewhere with a very popular open source library. I expect this balance to be slightly easier (and more enjoyable) when it's your job. Let's see.