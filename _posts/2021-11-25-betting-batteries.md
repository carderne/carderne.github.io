---
layout: single
title: "Betting on batteries"
date: "2021-11-25"
excerpt: "I bet (stupidly?) that coal will be cheaper than batteries in 2028"
image: /assets/images/2021/solar-batteries-white.png
---

This is a follow-up up on my previous post on [renewable energy](./renewable-energy). 

*Aside: Apparently China is planning to build [tons of new nuclear](https://smallcaps.com.au/china-supercharge-uranium-race-150-new-nuclear-reactors/) — does Xi read my blog?*

**Nota bene**: I think coal is *bad* and we need to get rid of it. I also think many in the global north are unrealistic about how easy that will be for poor countries.

I had a fun argument with a colleague recently, about the outcome of COP26. Many (I mean, many elite climate-concerned COP-following types) in the wealthy world feel that India et al. are not doing enough; they should stop building new coal and go all-in on solar. Many in the developing world feel that the wealthy world should put their wealth where their mouth is and pay for it.

My simple point is that, as I argued in my previous [post](./renewable-energy), solar energy could achieve an LCOE (levelised cost of energy) of $0, but it still needs storage, or interconnects, or *something*, if it's going to let people watch cricket at 7PM. And right now, that something is more expensive than coal. And expecting Modi, or Ramaphosa, or whoever else, to bet their countries' economies (and their citizens' ability to keep food cold and run businesses) on untested strategies seems unfair{%- include fn.html n=1 -%}.

## The bet

My opposition said that solar + batteries would soon be cheaper, and in the long time it takes to build a coal plant, you could be way ahead with solar. So we made a bet on the following question;

> In 2028, will coal still be cheaper than solar plus 32 hours of battery storage?

{% include image.html url="/assets/images/2021/bet.jpg" description="Not my handwriting not my napkin" class="narrow-img" %}

I meant coal or nuclear, but that's not what made it onto the restaurant napkin. India was the context, but I don't remember whether that was specified. 32 hours of storage is arbitrary, and probably more than is needed. We *do* need storage for 32 hours, but probably not covering every single GW of capacity. But the idea is that a day of no wind, and clouds all over India, might be followed by some big event. And load-shedding is a serious no-no. Again, there are additional solutions besides chemical batteries, but they are even less battle-tested.

*And*, as I went over in my previous post, India and the UK (representative wealthy country) have very different futures when it comes to energy. Chart data from [here](https://data.worldbank.org/indicator/EG.USE.ELEC.KH.PC?locations=IN). The UK's electricity consumption per capita is very high, and not growing much. This will change with more EVs and more heat pumps. But India is another story. You can't tell because of the scale of the chart, but India is trying to hockey stick. And we *want* it to hockey stick: to get Indians to a vaguely UK quality of life, electricity consumption will have to 5x at least!

{% include image.html url="/assets/images/2021/elec.png" description="These lines need to get a lot closer together if it's going to be an outcome that anyone can be proud of." class="narrow-img" %}

## The numbers

The chart below uses numbers from [Lazard](https://www.lazard.com/perspective/levelized-cost-of-energy-levelized-cost-of-storage-and-levelized-cost-of-hydrogen/){%- include fn.html n=2 -%}. Calculations are [here](https://gist.github.com/carderne/506a7ad4cfdda34ecbcf21ab51c53468). Solar and wind are much cheaper! They're even sometimes cheaper than the marginal costs of nuclear and gas! But note, again, that this doesn't include storage, or the fact that solar energy is only available when the sun shines. 

{% include image.html url="/assets/images/2021/solar-all.png" description="In the right places (sunny ones), solar is astoundingly cheap!" class="narrow-img" %}

LCOE is relatively simple, as you simply account for the megawatt-hours created and how much they cost. Storage is slightly more complicated, as it doesn't actually generate energy{%- include fn.html n=3 -%}, but simply time-shifts it from when it's cheap or un-needed to when it's expensive and needed.

Like generation technologies, batteries have a maximum capacity that specifies how much power they can output. Unlike generation technologies, the also have a maximum storage capacity before they're depleted and have to be recharged. These two numbers are basically: how many lights they can turn on, and how long they can keep them on.

To compare coal with solar + batteries, let's construct a scenario. A 2GW coal plant that we want to replace with solar. At a 50% capacity factor (it spends half its time switched off for maintenance and disruptions) it will generate around 8760 GWh of energy per year. The solar plant would have an installed capacity of 5GW and a [capacity factor of 20%](https://www.nature.com/articles/s41467-020-18318-7) (most of the time it isn't very sunny), generating the same amount of energy over the year. The costs for both of these, created simply by multiplying the values from the chart above, are shown below. Despite having a peak capacity 2.5 times higher, solar is still much cheaper!

{% include image.html url="/assets/images/2021/solar-scenario.png" description="If you don't care what time your energy comes, solar wins easily." class="narrow-img" %}

So let's add batteries. We want something that can output at least 2 GW (the peak output of the coal plant), and maintain it for 32 hours. So 2 GW capacity and 64 GWh of storage. (About [double](https://www.woodmac.com/news/opinion/the-growth-and-growth-of-the-global-energy-storage-market/) the total installed battery storage in 2021. )

This multiplier of 32 is far higher than typical grid-scale batteries, which are more likely to have around 5 hours. Based on this, I'm going to use purely the *energy* costs from Lazard, under the assumption that a battery with 64 GWh of storage will easily cover the required 2 GW peak output{%- include fn.html n=4 -%}. That number is 131 -- 232 $/MWh{%- include fn.html n=5 -%}, and multiplied in the same way added to the chart below.

{% include image.html url="/assets/images/2021/solar-batteries.png" description="Unfortunately, batteries complicate things somewhat..." class="narrow-img" %}

So... *right now*, the cheapest possible solar + batteries is slightly more expensive than the highest estimate for coal. Solar is probably on the more expensive end in India (not quite sunny enough), while coal is complicated as it comes out of the ground and is probably subsidised in all sorts of ways. But I would guess it falls to the lower end of this spectrum? So maybe today, in 2021, solar + batteries is around 3x more expensive. So that cost needs to drop by ~66% to become competitive{%- include fn.html n=6 -%}. 

## The question
The question is, will batteries drop in price by two-thirds by 2028? NREL has put together [some projections](https://www.nrel.gov/docs/fy21osti/79236.pdf) that expect costs to drop 25% - 60% by 2030. Within reach of losing me the bet! These projections are often wrong, and sometimes spectacularly so. Some people [citation needed] don't think batteries will have the same dramatic price curves as solar, as it is limited by chemistry and the physical quantities of material that are needed to store a certain amount of charge.

{% include image.html url="/assets/images/2021/batteries.png" description="These things are always wrong, but at least I can point at something" class="narrow-img" %}

So how sure am I in winning the bet... the stakes are high: the loser has to plant 100 trees, with the resulting carbon benefits accruing to the winner! And of course (labour obligations aside), I hope that I lose my bet. But do I think coal will be cheaper than solar+batteries (32 hours) in India in January 2028? I have no idea, but for posterity's sake I'm going to put my credibility on the line and say

> yes (coal will be cheaper), with 60% confidence

What if we include nuclear? Unlike coal, it might have a future of improved technology and learning curves... but probably not before 2028.

See you in six years!

<hr>

<span id="fn1">[1]&nbsp;<a href="#fn1b"><sup>go back</sup></a>&nbsp;</span><i>There is currently around [20 GW of installed battery capacity](https://www.iea.org/reports/energy-storage) worldwide.  A drop compared to the [2,000 GW of installed coal](https://www.statista.com/statistics/217256/global-installed-coal-power-generation-capacity/) capacity. (But it's [growing fast](https://www.woodmac.com/news/opinion/the-growth-and-growth-of-the-global-energy-storage-market/)!)</i>

<span id="fn2">[2]&nbsp;<a href="#fn2b"><sup>go back</sup></a>&nbsp;</span><i>Someone tell me if Lazard is suspect for some reason.</i>

<span id="fn3">[3]&nbsp;<a href="#fn3b"><sup>go back</sup></a>&nbsp;</span><i>Except don't forget the [First Law of Thermodynamics](https://en.wikipedia.org/wiki/First_law_of_thermodynamics).</i>

<span id="fn4">[4]&nbsp;<a href="#fn4b"><sup>go back</sup></a>&nbsp;</span><i>I'm probably disadvantaging storage by using numbers for batteries with a lower ratio, and presumably they could be cheaper for this level of energy if designed with such a high ratio in mind.</i>

<span id="fn5">[5]&nbsp;<a href="#fn5b"><sup>go back</sup></a>&nbsp;</span><i> Note that this is per MWh delivered, not per MWh of storage installed. That number is about 1,000 times higher.</i>

<span id="fn6">[6]&nbsp;<a href="#fn6b"><sup>go back</sup></a>&nbsp;</span><i> A [report on LDES](https://www.ldescouncil.com/assets/LDES-2021-report-lowres.pdf) (long duration energy storage) suggests costs must drop by 60% for LDES specifically to be competitive. I imagine LDES is cheaper than Li-Ion (or has the potential to be). Anyway this feels like confirmation that I'm in the right ballpark.</i>


