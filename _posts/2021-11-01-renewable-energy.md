---
layout: single
title: "Thoughts on renewable energy"
date: "2021-11-01"
excerpt: "TLDR: It’s great, but developing countries need more"
---

As COP26 kicks off in Glasgow, it seems as good a moment as any to talk about one of the cornerstones of slowing climate change: decarbonising the electricity system. Many countries (such as the UK) have had easy wins by replacing coal with gas, and using that new flexibility to incorporate more wind. This strategy only goes so far, and doesn't work for most poorer countries.

If we're going to get anywhere, and if the COP promises are going to achieve anything, we need a lot more than wind and gas. We need storage, interconnects, and we desperately, desperately, need affordable, workable nuclear.

*NB: If this post sounds negative about renewables, I'm just trying to balance the discourse by pointing out that they don't solve every problem. I'm super pro the stuff, and we need more and more of it!*

## Dealing with intermittency
In my years working in and thinking about energy, I've often thought and talked and opined about the value of renewable energy to decarbonisation and energy supplies in general. I wish I’d made concrete predictions every year to benchmark myself, but I’ve probably been slightly too pessimistic on one question: the proportion of an energy supply that can be intermittent renewable energy (wind and solar, but not hydro, bio, geo) before the system collapses.

Clever markets, country interconnections, a handful of batteries, and lots and lots of gas have kept things turning at [impressively high](https://wernerantweiler.ca/blog.php?item=2021-10-21) levels of renewable penetration (in some places). But I've continued to bang (when asked and in private) the tired old drum of baseload: if you can’t guarantee a certain amount of energy in all eventualities, you’re going to run into problems. What ultimately happens depends on many things, but the options include:
- Unplanned blackouts (Texas).
- Planned blackouts (South Africa).
- Keeping the lights on by spending millions on natural gas, and de-mothballing coal plants (the UK and large parts of the world this year).

[To be fair](https://www.youtube.com/watch?v=G19B7lTgwCE), these events were not caused by renewables any more than by the vagaries of gas pipelines and coal prices. But they point to the delicacy of the systems and the importance of keeping them running{%- include fn.html n=1 -%}. And they point to a ceiling of the contribution that intermittent renewables can make.


## A quick primer on energy and power
Briefly,
- *Energy* is measured in things like kWh or MWh, and is something you *use up* every time you turn on a light. It is the quantity of electricity that is delivered and used in a given period of time. 
- *Power* is measured in things like MW or GW, and describes a system’s maximum instantaneous capacity: the *rate* at which it can produce under ideal conditions. Power doesn't get used up.

And another important concept, while we’re here:
- The *[capacity factor](https://en.wikipedia.org/wiki/Capacity_factor)* of a plant describes how much *energy* it is able to deliver in a year, compared to if at ran at full *power* 24/7. Thermal plants (nuclear, coal, gas) need repairs and maintenance, which means they aren't delivering energy during those times. Wind and solar panels deliver less or no energy when the wind doesn't blow.

This means a nuclear plant might deliver 90% of its theoretical maximum (if it never needed maintenance), with most of that 10% shortfall being planned. A wind farm might be around 45%, with the shortfall being at the whim of the weather. A solar farm might be 30% (much lower in less sunny places), with the shortfall mostly caused by the (quite predictable) night time.

## Reducing carbon vs adding capacity
Ultimately, countries investing in new energy supplies have one of two objectives in mind:
1. Rich countries: reduce the carbon intensity of the grid, without seriously changing its total power capacity. Every bit of *energy* that comes from a low-carbon source is a win. 
2. Everyone else: increase the grid’s *power* capacity to keep up with demand from people and industry. 

And this is where I think there’s a big disconnect in the general discourse on intermittent renewable energy. The UK can litter the North Sea with wind turbines, and “simply” turn on old plants when new ones disappoint. Poorer countries can’t do this: every new MW or GW is needed, and if some don’t deliver, someone will need to turn off their lights, as there are no old plants to turn on! The key takeaway is **wind MWs (and, to a lesser degree, solar MWs) don’t meaningfully add to a country’s power capacity.**

When it comes to the [crunch](https://www.youtube.com/watch?v=B7he8OyuQdg), they can’t be relied on and need to be backed up with something. So for developing countries, where even baseload supply is not all that reliable, it’s a losing proposition to spend money on capacity that doesn't increase the number of lights that can be turned on.

For these countries, the plummeting cost of wind turbines is almost irrelevant to the main goal of increasing capacity. It’s that plummeting cost, plus whatever storage is needed to make it reliable, that matters. Wind and solar can still be valuable in these places, by providing clean, cheap energy that can leave some coal or gas un-burned. But to divert investment from coal (which can reliably electrify homes and industry) to wind (which can’t) is not as easy as some in the North would like you to think.

## Aside on costs
Wealthy countries have it much easier. Every turn of the wind turbine equates to a reduction in emissions with zero marginal cost. But there is still a difference between dispatchable (gas and co.) and intermittent supplies (wind and solar): gas turbines can be turned on at will, making their energy more valuable than wind energy, which comes when it comes.

It is obvious that capital costs are insufficient as a comparison point. On that measure, gas plants are cheapest (ignoring their expensive fuel), solar plants are middling (free sunlight, but low capacity factor), while nuclear is laughed off the chart. Levelised cost of electricity ([LCOE](https://en.wikipedia.org/wiki/Levelized_cost_of_energy)) takes into account a plant’s entire lifetime but still [isn't a useful metric](https://www.wri.org/insights/insider-not-all-electricity-equal-uses-and-misuses-levelized-cost-electricity-lcoe) to compare different technologies, as it doesn't consider the value of energy when and where it’s wanted. 

One improvement is to use the [levelised avoided cost of electricity](https://www.eia.gov/outlooks/aeo/pdf/electricity_generation.pdf), which estimates the revenue a plant would produce over its lifetime, taking into account (for example) selling cheaper electricity at night, and more expensive during the peak hours of the day. The best method (which unfortunately doesn't produce the most compelling charts) is to create energy systems models and see what they say. This way, you set hard constraints on the amount of electricity that must be delivered at 8PM (lest you suffer the wrath of Great British Bake-Off watchers) and the amount of wind and sun that can be expected at different times of year, and let the model choose the best way forward. Unsurprisingly, it doesn't just look at the cost of solar and go all in.

## Back to baseload
All this means that developing countries that want to increase their power capacity, and provide energy to a growing demand (more lights, more TVs, more industry), have some hard choices to make.
1. Intermittent renewables plus energy storage: battery prices are coming down quickly, but not quickly enough. Other forms of storage are too novel or too reliant on geography.
2. Coal: the downsides of this are obvious.
3. Gas: not everyone has it, and pipelines can’t go everywhere. [LNG](https://en.wikipedia.org/wiki/Liquefied_natural_gas) capacity is growing, but there isn't enough yet. It’s still an expensive option, and still has high emissions.
4. Nuclear: complicated, high capital costs, and lots of public resistance. Most poor countries lack the ability to run (let alone build) a nuclear plant, making them [reliant](https://en.wikipedia.org/wiki/Build–operate–transfer) on a small menu of nuclear companies.
5. Interconnects: wire more countries together, in the hopes that the intermittency will even out. This is becoming a reality in rich countries, but far from being an option in large parts of the world.

Different countries are going to make different choices. Less wealthy ones that need to ramp up capacity will probably continue with coal to some degree (see: China, India). Many, hopefully, will decide that **nuclear is the least worst option.** This is extremely complicated and fraught with difficulties, especially for poor countries. That's why we need leadership on this front, renewed investment, and better, more scalable nuclear technologies.

There is some hope on this front:
- The UK seems to be [embracing nuclear](https://www.ft.com/content/e6426194-21e6-49c4-9520-97c337b350fd) as part of its Net Zero strategy. A mix of big plants, funding for [SMRs](https://en.wikipedia.org/wiki/Small_modular_reactor), and a bunch of fusion moonshots (three in Oxford alone I think).
- Even Japan seems to be [getting on board](https://www.marketwatch.com/story/japan-oks-plan-to-push-clean-energy-nuclear-to-cut-carbon-01634920487)?
- Ursula von der Leyen/the EU making some hints in the [same direction](https://twitter.com/vonderleyen/status/1451552759736582153).

## Appendix on plummeting costs
While nuclear has been stagnating, wind and solar costs have been falling, and installation increasing, consistently outpacing the [IEA's predictions](https://twitter.com/AukeHoekstra/status/1064529619951513600). Extrapolating this learning rate into the future, some predict [insanely cheap solar](https://rameznaam.com/2020/05/14/solars-future-is-insanely-cheap-2020/). Others [point out](https://twitter.com/AukeHoekstra/status/1261591413755691008){%- include fn.html n=1 -%} (as I have above) that solar capex is at best half of the story: infrastructure, transmission, and storage set some definite floors on the cost/usefulness of renewables. Still, there are plenty of sunny and windy places, and [growing appetite](https://qz.com/india/2078607/will-india-and-uks-global-solar-grid-plan-work/) for [large interconnects](https://climatecompatiblegrowth.com/gulf-undersea-india-transmission-system/).

Whether by atomic or renewable energy, there seems to be a (small?) possibility that within this century, we'll achieve not only widespread low-carbon electricity, but also extremely cheap electricity. It's a bit of a fever dream at the moment, given the number of people that have no electricity, or depend on dirty, unreliable, expensive electricity. But it's worth [asking](https://twitter.com/EggersMatt/status/1261012725716578304): what kind of transformative changes would it enable?

<span id="fn1">[1]&nbsp;<a href="#fn1b"><sup>go back</sup></a>&nbsp;</span><i>Interesting aside: wholesale electricity in the UK costs about [100 £/MWh](https://www.epexspot.com/), but the “value of lost load”, which indicates the “value that electricity users attribute to security of electricity supply” is [estimated](https://londoneconomics.co.uk/blog/publication/the-value-of-lost-load-voll-for-electricity-in-great-britain/) in the 5,000 - 10,000 £/MWh range. It’s a crazy asymmetry between what people pay for something, and how much you’d have to pay them to forgo that thing.</i>

<span id="fn2">[2]&nbsp;<a href="#fn2b"><sup>go back</sup></a>&nbsp;</span><i>Auke unfortunately cites Mark Jacobson here, who is a [bit](https://www.pnas.org/content/114/26/6722.full) of a [hack](https://www.latimes.com/business/hiltzik/la-fi-hiltzik-jacobson-lawsuit-20180223-story.html).</i>