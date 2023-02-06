---
layout: single
title: "Trunk-based development with Vercel"
date: "2023-02-06"
excerpt: "Branches != deployments"
---

Vercel's core workflow is based around tying a git branch (probably `main`) to your Production deployment. You then get loads of snazzy features like automatic "Preview" deployments on your PRs.

You can also create additional Preview deployments _tied to branches_, eg `staging`. But to you use this, you have to do some horrible [Gitflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) stuff like merging feature branches to `staging` and then merging that (plus any hotfixes you find along the way) into your `main` branch so that Vercel will deploy it to Production.

I couldn't believe Vercel would make me do such an old-fashioned thing as that, where what we obviously want is to merge _once_ to `main` and then release to Production with tags or buttons or something of that nature.

Luckily I found their guide [Can you deploy based on tags/releases on Vercel?](https://vercel.com/guides/can-you-deploy-based-on-tags-releases-on-vercel),{%- include fn.html n=1 -%} which suggested the hacky workaround of tying your Production deployment to some unused branch, and then using GitHub Actions plus a Deploy Hook to trigger a deployment whenever you push a tag or whatever. Unfortunately I didn't appreciate how deeply the  `branches == deployments` mantra goes at Vercel, so I then tied `main` to our Preview domain. And lo, when I hit the Deploy Hook, instead of deploying Production, it deployed the Preview...

It turns out that the only way to beat that mantra is to use the [Vercel CLI with GitHub Actions](https://vercel.com/guides/how-can-i-use-github-actions-with-vercel), where you can tell Vercel to take _this_ code and put it on _that_ deployment, thank you. To do this we:
1. As before, use Vercel's web console to connect Production to some unused branch `ignore` and (important!) apply some GitHub branch protection on that branch to make it read-only.
2. Create a Preview domain and tie it to the `main` branch.
3. Create a GitHub Action something like this to deploy based on tags (or whatever you want):

{% raw %}
```yaml
on:
  push:
    tags:        
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - run: npm install --global vercel@latest
    - run: vercel pull --yes --environment=production --token=${{ secrets.TOKEN }}
    - run: vercel build --prod --token=${{ secrets.TOKEN }}
    - run: vercel deploy --prebuilt --prod --token=${{ secrets.TOKEN }}

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```
{% endraw %}

Just make sure you have your Vercel Build and Root Directory settings configured correctly, as the `vercel pull` command will pull them down and use them for the build step. Luckily you can test these exact same commands from a local shell to check that they work (except maybe drop the `--prod`) flag until you're ready!

------------------------------

{% include fnn.html n=1 note="Still unclear to me whether this follows Betteridge's law." %}