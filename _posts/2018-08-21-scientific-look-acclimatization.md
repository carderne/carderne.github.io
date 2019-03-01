---
layout: single
title: A semi-scientific look at acclimatization
date: '2018-08-21 13:15:00'
excerpt: "I've climbed about seven mountains above 4,000 metres. After my latest trip to Kyrgyzstan, where I took a very careful approach to acclimatization, I decided to have a look at my previous trips to see if anything of statistical value could be dredged out..."
tags:
- mountains
- outside
---

I've climbed about seven (depending on what we count) mountains above 4,000 metres, and lots more of other altitudes. After my latest trip (to [Ala Archa National Park](https://en.wikipedia.org/wiki/Ala_Archa_National_Park) in Kyrgyzstan) where I took a very careful approach to acclimatization, I decided to have a look at my previous trips to see if anything of statistical value could be dredged out...

...it couldn't, so I decided to make some pretty visualizations instead! First up, I tabulated the twice-daily elevation on each of eight selected trips: how high I woke up, and the highest point attained in the day. The trips are as follows (in order of height, not date!):

 * South Africa: many many ascents of [Table Mountain](https://en.wikipedia.org/wiki/Table_Mountain) (1,085 m)
 * Sweden: a winter ski-ascent of [Kebnekaise](https://en.wikipedia.org/wiki/Kebnekaise) (2,099 m – Sweden's highest)
 * Washington, USA: two hikes, followed by ascents of [Black Peak](https://en.wikipedia.org/wiki/Black_Peak_(Washington))  (2,736 m) and [Mt Adams](https://en.wikipedia.org/wiki/Mount_Adams_(Washington)) (3,742 m) and then [Pigeon Spire](https://en.wikipedia.org/wiki/Pigeon_Spire) in Canada (3,156 m – not charted below)
 * California, USA: a spring hike of parts of the [JMT](https://en.wikipedia.org/wiki/John_Muir_Trail), including Mather Pass (3682 m) and [Mt Langley](https://en.wikipedia.org/wiki/Mount_Langley) (4,275 m)
 * Kyrgyzstan: an acclimatisation climb in Ala Archa National Park of [Uchitel](http://www.ericandtaylor.com/climbing-peak-uchitel/) (4,535 m) and [Korona](http://www.tuncfindik.com/kirgizistan-ala-archa-daglari-korona-peak-4800m-cikisi/) (4,860 m) in preparation for an (abandoned) attempt on [Khan Tengri](https://en.wikipedia.org/wiki/Khan_Tengri) (7,010 m)
 * Georgia: an expedition-style climb of [Kazbek](https://en.wikipedia.org/wiki/Mount_Kazbek) (5,047 m), documented [here](https://rdrn.me/summer-in-europe/)
 * Mexico: a half-hearted attempt on [Orizaba](https://en.wikipedia.org/wiki/Pico_de_Orizaba) (5,636 m – we pulled out
   before making an attempt) followed by acclimatization on [Iztaccíhuatl](https://en.wikipedia.org/wiki/Iztaccihuatl) (5,230 m) and then a successful summit of Orizaba, all documented [here](https://rdrn.me/primero-somos-tontos/)
 * Boliva: lots of backpacking followed by a guided climb of [Huayna Potosí](https://en.wikipedia.org/wiki/Huayna_Potos%C3%AD) (6,088 m)

The twice-daily values from each trip are plotted in the chart below (created using [Bokeh](https://bokeh.pydata.org/en/latest/)). Note that I've squared the vertical axis to exaggerate the differences,so Kebnekaise appears quadruple Table Mountain, when it's actually double.

The only time I've suffered altitude sickness was on our first Orizaba attempt(Mexico, day 5) where we got up to ~4,800 m just five days after leaving sea level. As you can see we quickly dropped down as low as we could and reassessed.After acclimatizing on Iztaccíhuatl, where we spent several hours above 5,000 metres, we returned to Orizaba for an easy climb to the top.

The chart makes clear that Kazbek was easily the most steady ascent, and the graph doesn't even show that I'd been up to around 3,000 m in [Spain](https://en.wikipedia.org/wiki/GR_11_(Spain)) just over a week before – as a result, the 5,047 m summit was a breeze, physically.

![Mountains][acc1]

The above is very attractive, but it doesn't make it very easy to compare altitudes. The bar chart below ditches the time axis to make this a bit easier.Each vertical jump represents a time where I ascended higher than I had previously been on that trip, ignoring times when I stayed still or descended.Bolivia starts at 2,810 m because I spent weeks in [Sucre](https://en.wikipedia.org/wiki/Sucre), so that almost became my 'sea level'.

Most of the big jumps are sensibly below 4,000 m, where altitude effects are generally less <sup>[[citation needed](https://en.wikipedia.org/wiki/Altitude_sickness)]</sup>. As you can see, the single biggest jump was in California, where, a day after exploring [Death Valley](https://en.wikipedia.org/wiki/Death_valley) (-86 m), we ascended 3,020 vertical metres (some by car) to Bishop Pass (3,649 m) and slept in the snow at pretty much that height.

Another big jump was in Kyrgyzstan. After a 35 hour flight and one night's sleep in Bishkek, we ascended 2,500 metres to our camp site. Although Huayna Potosí inBolivia is still the highest elevation I've reached, I never ascended more than 1,000 in a single day, and my baseline was already extremely high. Result – I felt great, even at 6,088 metres above sea level!

![Delta][acc2]

Note that because this graph has no temporal information, it masks how quickly these pushes happened. So although Mexico and Kyrgyzstan look quite similar, in reality we spent several rest days at altitude in Kyrgyzstan before daring to above 4,800 metres, whereas in Mexico we rushed straight at it without a moment's pause.

What both of these charts lose is technical difficulty: Korona is the only mountain that required steep ice climbing near the summit – not easy at around 4,800 metres!

[acc1]: /assets/images/2018/acc1.png
[acc2]: /assets/images/2018/acc2.png