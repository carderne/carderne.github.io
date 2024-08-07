---
layout: single
title: Why we left Fly.io
date: 2024-08-07
image: /assets/images/2024/fly-banner.png
---
{% include image.html url="/assets/images/2024/fly-banner.png" description="" class="" %}

TLDR: Scroll down to [Problems](#problems) if you want to skip all the "my grandmother taught me this recipe in Sicily" stuff and just get to the point.
## Context
Putting together a new product/service/thing involves a bunch of stack decisions: what language, cloud, persistence, architecture... At a startup this often has to be done quite quickly, and with limited foresight of where things will be in 2, 4, 6 months. You know you'll regret many of the decisions, you just don't know which.

At $PreviousCo we went through a few of these migrations as we figured out what exactly we were building, and for whom. We had put together an MVP with a grab bag of tools. Within about six months, most had been replaced, for various reasons:

- [Clerk](https://clerk.com/) was unbeatable for getting off the ground, but we had some particular OAuth needs, wanted a bit more control, and so we switched to [Auth0](https://auth0.com/) and [nextjs-auth0](https://github.com/auth0/nextjs-auth0), which was _painful_. My kingdom for a session cookie.
- [MeiliSearch](https://www.meilisearch.com/) was lacking some specific features useful for multi-tenant and multi-index, so we switched to [TypeSense](https://typesense.org/). I'm sure the gap was closed a few months later but it was an easy move.
- [BigQuery](https://cloud.google.com/bigquery) and [PipeDream](https://pipedream.com/) fell to Postgres and [Prefect](https://www.prefect.io/). No surprise, they were really just for the MVP.
- [Supabase](https://supabase.com/) was okay, but since we weren't using [Supabase Auth](https://supabase.com/docs/guides/auth) or many of their other features, the value-add was minimal. The downsides were that, as satisfying as row-based-security might be, it's unfamiliar to many (important in a fast-growing team) and doesn't have a great version-control story. Added to that the local dev story wasn't great.
- And finally [Vercel](https://vercel.com/carderne-team)! Our app was full-stack Next.js, but we wanted a non-serverless [tRPC](https://trpc.io/) backend, so we moved to Fly.io. Soon we had our Next app, tRPC backend, a Python service, Postgres database, Redis cluster, [Cerbos](https://www.cerbos.dev/) authorization service all running on Fly.io.

We clearly used up our [innovation tokens](https://boringtechnology.club/)! Most of this was just stuff thrown together for an MVP. Some of this was painful, some was easy. Choosing a tech stack to get going but also to last until you Make It Big isn't easy. For example, as painful as the Clerk migration was, I'd use it again to get going — it's just so easy to get social login working.

{% include image.html url="/assets/images/2024/insanity.png" description="" class="" %}

## Honeymoon
The main reason we chose Fly.io was a thesis that multi-region would quickly become very important for us. More on that later, but I see you tut-tutting sagely. But Fly was great! We were still just a few people, and a few `fly create app` and `fly create postgres` commands were more appealing than the equivalent Kubernetes or even just Cloud Run + whatever Google DB. Fly made it easy to get some Dockerfiles and Postgres running in regions around the world, simple scaling, fast builds with persistent build disks. And some Grafana dashboards for free, to go with our [observability](/observability) setup.

We added a few other services, all running in the private network. Snappy local network, decent ops, and a useful integration with [Doppler](https://www.cerbos.dev/) for secrets handling. We used their partnership with Upstash for a serverless Redis cluster, but that was a bit of a mess — Upstash Redis seems prone to all sorts of weird TCP issues that you just don't get with non-serverless Redis. Anyways, _mea culpa_.

We even added ephemeral apps for PR "Preview Deployments", much like what you get with Vercel, Netlify etc. Except depending on the reach of your changeset, you'd get either just a Preview frontend, or the full-stack including a fresh DB, authorization etc. This was pretty great for DevX, and Fly made it easy. Sometimes the `fly delete` after the PR was closed would fail, but a weekly cron job cleared up any orphaned instances.

## Priorities
Multi-AZ had seemed critical. We realised it wasn't really. Quite a few of our features relied on big queries that took one to two seconds anyway, so adding a bit of latency wasn't a killer. Plus we hadn't yet figured all the nuances: globally replicate all data, or silo region-specific data. Or some mix? It introduced the complexity of read replicas, but any read or write that required a trip to the primary DB instantly negated any benefits, and we weren't always careful enough. All that set, Fly has some nifty [solutions](https://fly.io/docs/blueprints/multi-region-fly-replay/) for these problems.

I think it's an example of a classic difficulty in startup land: how big, how soon? Engineers say X, Product says Y, Marketers say 🤪. Needless to say, I'll think more carefully next time about rushing to building a multi-AZ solution.

Anyway. Once we'd decided this was no longer a priority, a major selling point of Fly vanished. This also happened around the time our team had grown big enough that managing a Kubernetes cluster or two (disclosure: we already had one for our Prefect/orchestration stuff) was starting to look a lot easier.

## Problems
So why did we ditch Fly? In the end it came down to the following four things. Until these are improved, I'd be unlikely to recommend it for Production™ work. (Unless you actually need the global thing. And to be fair to Fly, they were really [upfront](https://news.ycombinator.com/item?id=35044516#35048244) that the global thing is their raison d'être.)

### 1. Not declarative enough
 Fly gives you a [fly.toml](https://fly.io/docs/reference/configuration/) while where you specify images and ports and rollout strategies and whatnot. But you still have to run quite a few commands to get your app to the state you want. Scaling, region counts, IPs, database credentials. For this to work in a growing team required documenting the scripts that had been (or should have been) run, writing some wrappers for common tasks etc. And the only way to know the current state of an app is to check the dashboard, which is mostly read-only, and might not have the info you want. If you're into GitOps, this is not great. Compare to Terraform or kubernetes, where, any dev can check the current config files and be confident (as long as you trust your CI) about the current state of the system. And when they _change_ it, it won't be a Slack message "hey I increased Frankfurt to 4 nodes" but a PR. Wildly enough, you can now do [Kubernetes on Fly](https://fly.io/blog/fks-beta-live/), so this may be moot.
 
{% include image.html url="/assets/images/2024/fly-vs-gitops.png" description="Plus, you know, writing the diff" class="" %}

### 2. Reliability
Fly has had ups and downs with [reliability](https://community.fly.io/t/reliability-its-not-great/11253). It's much better than it was, and I imagine it's even better now than it was a few months ago. The builds were flaky. Fly uses machines with persistent volumes for builds, which is great: you don't need a hundred clever caching mechanisms to keep your Docker/npm/Cargo builds quick. It's a machine with a hard drive and it will cache stuff. But too often builds would fail, new rollouts would get stuck, or new Postgres instances would sit in limbo. A flaky CI system is a real buzzkill to dev productivity. And then there were also the outages. It's stressful when your app is down and you can't do anything but shake your fist at the cloud.

{% include image.html url="/assets/images/2024/freq-visit.png" description="I don't even know where GKE's status page is..." class="" %}

### 3. Permissions not granular enough
This one was disappointing, especially given that other much less-funded SaaSy solutions have nailed this. But, as with the previous two issues, everything is just much harder when you're inventing a new type of cloud on the fly (I've been dying for a pun). And, as with everything else, they have a [very clever solution](https://fly.io/blog/macaroons-escalated-quickly/) with Macaroons. But it hasn't yet been made useful enough for a larger team. You can't invite a read-only user (check logs, metrics) or even a billing user. You couldn't create app-scoped tokens, but now you can. Afaik you still can't scope things more carefully than that. I emailed about this and got promising noises from tptacek and others on the team. I'm sure it'll be great when it's ready, but it isn't yet. 

{% include image.html url="/assets/images/2024/fly-delete-app.png" description="This needs to be harder for just anyone to do." class="" %}

### 4. Private networking
Fly uses Wireguard for [everything](https://fly.io/blog/our-user-mode-wireguard-year/). So long as you're within their ecosystem (which is growing), it's great. Private networks and private IPv6 everywhere. But locking down network access as part of a wider ecosystem became a bit of a challenge. We wanted to peer with a GCP VPC (say that ten times fast). Okay, I set up a Wireguard bastion, that's not too bad. But since Fly apps have [no persistent outbound IP address](https://community.fly.io/t/outbound-ip-address/1366/11), you get issues trying to lock down ingress on other services. Well so I setup HAProxy running inside GCP to get right through to these services with a static IP address, but that's getting a bit unwieldy. Basically it just became incompatible with our priorities. If you're happy leaving all your stuff open to `0.0.0.0/0` then this likely won't bother you. But if you've got highly sensitive multi-tenant data, a bit of private networking does wonders for sleep quality. Even if you don't care about that, you still miss out on the performance benefits of getting everything on the same network. Obviously none of that matters if you only use Fly containers.

{% include image.html url="/assets/images/2024/vpc.png" description="There's a reason Solutions Architect types love these reassuring VPC boxes." class="narrow-img" %}
# Result
We moved to Google Kubernetes Engine. Declarative, reliable, granular, and private. The upfront setup cost is higher, it's not global. You need to have people on staff who like fiddling with k8s and yaml and kustomize and CI. And figuring out why a deployment isn't scaling. And and and. But `kubectl` is generally more responsive than email support.

I still use Fly for some personal stuff, and will again in the future. In the PaaS space, I prefer those (like [Render](https://render.com/)) that pull from my repo, rather than forcing me to write workflow code. But that's just a taste, and it will likely change. I'll definitely reach for Fly if I'm building something that must be multi-region. And despite all the above I still love their product, am amazed by the work they're doing, and love the technical writing they share. (Eg [this great post](https://fly.io/blog/tokenized-tokens/) about keeping secrets away from untrusted code.)