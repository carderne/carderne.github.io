---
layout: single
title: I made an app for my cycling club
date: 2026-02-15
---
And you should too!?

I'm a member of [Oxford's Friendliest Cycling Club](https://cowleyroadcondors.cc/), also apparently the "[Club of the Year](https://www.cyclingweekly.com/news/its-always-been-about-trying-to-be-friendly-and-inclusive-cycling-weeklys-club-of-the-year-on-what-it-takes-to-thrive)" of 2023.

About a year ago the club had a small administrative crisis around the club ride organisation process. From what I understand (quite little), most clubs are smaller and homogeneous-er. They have set ride times, everyone shows up, they split up and go for rides.

The Condors are different. It's a big club, the kinds of rides people want to do are quite diverse (slow trundles through the countryside, speedy chaingangs, gravel and mtb) and so during Covid a system of posting things on Facebook evolved. This annoyed everyone who doesn't like Facebook, so another system using Google Sheets evolved. This annoyed everyone{%- include fn.html n=1 -%}.

I was at home visiting family at the time and one morning I sat down and vibed out a simple app to take on the role of official club ride organising app. I say "vibed", but this was before the singularity<sup>[citation needed]</sup>, so I mostly made it by hand with some components from v0.

It's a simple CRUD app, club members create rides, others "join" them, leave comments etc. There's a map and some details about the distance, expected speed, planned coffee stops.

And it's been a huge success! It's hard to compare pre- and post-app, but there seem to be more rides happening, more people leading rides, more people trying out new types of rides. It's a simple thing, but it takes basically no effort from me, costs the club around £10 a month, and seems to be doing a lot of good. I recently added a map of all the routes the club has used recently, hoping to make it easier for aspiring ride leaders to get inspiration.

{% include image.html url="/assets/images/2026/condors-app.png" description="Condors typical migratory pattern" class="" %}

More than anything, it's been a success for me. I'd been playing footsie with different clubs in Oxford. I was a member of the Oxford Mountaineering Club, briefly the Cowley Chess Club, and still the Headington Road Runners, although I rarely make it. The app gave me a reason to get more stuck in with one club, along with a bit of free notoriety. And it's paid back such dividends in really becoming part of a community, building it and getting the joy of being part of something.

We're in a funny moment where the kind of app available for next to free is shifting from a static Wordpress site, to a fully-featured CRUD app. The marginal cost to build another one is basically 0, but there are still thousands of companies and people and clubs and things out there for whom they're inaccessible... Most problems are better solved in other ways, but in the right places a bit of software can do wonders, it turns out.

PS: If you're a member of a cycling club that is _also_ complicated, I'd be happy to hear from you. The app isn't currently open source (for no reason), but I'd be happy to open it up and help get your club going with it.

{% include fnn.html n=1 note="An app called Spond was also considered, but it requires downloads and logins and horrible stuff like that. Having our own app lets us carefully titrate the level of friction to new joiners." %}