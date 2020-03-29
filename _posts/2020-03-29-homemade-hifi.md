---
layout: single
title: "I made millenial pink wireless speakers"
date: "2020-03-29"
excerpt: "The software side was disappointingly easy; the hardware unsurprisingly messy. They sound better than any smart speaker, and don't spy on me!"
tags:
- inside
---

*Note to readers: I'm mostly writing this so I don't forget how I made these, in case I ever want to make another set.*

*Unrelated: how much would you pay for a pair of these?*

*Note to self: next time I do a project, take more photos and notes of the process.*

Many years ago in another country I had beautiful floor-standing speakers, a classy big amplifier and even a well-looked after turntable. Several years of globe-trotting have left me relying on some horrible generic bluetooth speakers. The sound is horrible, you constantly have to re-dingle the Bluetooth, and the battery is always running out. I started lusting after a proper set of WiFi-connected speakers but a yearning for the smell of sawdust, along with an innate fear of Siri and her intelligent ilk, lead me to a better idea: make my own!

The basic idea: hook up a Raspberry Pi to a small amplifier and some speaker drivers. Initially, inspired by the Apple HomePod, I planned a single multi-directional smart speaker. There were a lot of questions:
- Which software to use?
- Which Rasperry Pi model?
- What kind of amp?
- What speaker drivers? Mid-range and tweeters, or just mid-range?
- What kind of [crossover](https://en.wikipedia.org/wiki/Audio_crossover)?
- What kind of box to put it all in?

I started Googling, and was inevitably brought to [diyAudio.com](https://www.diyaudio.com/), which was partly interesting, partly overwhelming, and mostly insane. Audio enthusiasts are known for their esoteric views on physics and reality, and apparently the DIY crowd are no different. After a brief trip down the wormhole of exotic capacitor materials, I decided to change tack. The signal-to-noise ratio (ahem) just isn't high enough.

Instead I found this guy on YouTube: [Kirby Meets Audio](https://www.youtube.com/channel/UCOuow_HIYmeaIqi42zVs3qg). Less wondering about 3<sup>rd</sup> order frequency roll-off; more power tools and sawdust. Inspired by one of his [designs](https://kmakits.com/collections/speaker-build-plans/products/mini-tower-speakers-diy-build-plans) I changed tack: a stereo pair of speakers (rather than a single multi-directional), a single mid-range driver per speaker (so no cross-over design needed) and whichever speaker box size was most convenient ([*Q* factors](https://en.wikipedia.org/wiki/Q_factor) be damned). I went for a slightly shorter design than Kirby's, aiming for about the profile of a hard back book, and came up with the following.

{% include image.html url="/assets/images/2020/hifi1.png" description="The hardest part of this whole project was learning how to use FreeCAD." class="narrow-img" %}

But I still needed to figure out the other bits. I um'd and ah'd about cheaper options, but quickly settled on getting a [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) and a [HiFiBerry Amp2](https://www.hifiberry.com/shop/boards/hifiberry-amp2/). The latter is am amazing bit of kit: a 60W stereo amplifier that simply plugs on top of the Raspberry Pi. It also solved the software problem: the same people make [HiFiBerryOS](https://www.hifiberry.com/hifiberryos/), a bare-bones operating system that provides just the features I wanted: AirPlay and Spotify support, and a simple web interface for managing it. (I'm actually currently using [Volumio](https://volumio.org/), but only because its based on Debian, making it easier to install other things and mess around. As soon as I have a dedicated messing-around RPi, I'll be back to HiFiBerryOS.)

{% include image.html url="/assets/images/2020/hifi2.png" description="It is a sleak interface. (Picture lifted from HiFiBerryOS home page.)" class="narrow-img" %}

Pretty soon I had three exciting parcels waiting to be unwrapped: the Rpi, the amp, and the [Dayton Audio PS95-8](https://www.parts-express.com/dayton-audio-ps95-8-3-1-2-point-source-full-range-driver-8-ohm--295-349) 3.5" speakers recommended by Kirby. I installed the OS, wired up the speakers and plugged everything in, and a second later was streaming from my phone! I was almost disappointed by how easy it was...

Finally convinced that it would work, I took my engineering drawings to the wood store and bought some wood. The most exciting bit: drilling ~80 mm holes (useful if I could remember) for the drivers. The most confounding part: using my limited skills and single clamp to glue everything together into a box.

{% include image.html url="/assets/images/2020/hifi3.jpg" description="Very scientific things going on." class="narrow-img" %}

Lots of messy glue, sanding (note to self: rent an electric sander next time) and a can of pink spray paint later, and I had a single bookshelf speaker! I decided this would be the left speaker. The right speaker would be a bit more complicated, because it would house the RPi and the amp. This meant its guts needed to be somehow accessible. The best solution I came up with was for the back panel to be removable with a screw in each corner. And so I unwillingly learned about another new thing: [threaded inserts](https://duckduckgo.com/?q=threaded+insert&iax=images&ia=images). These allowed me to use bolts on the back panel and easily remove it whenever I want to fiddle.

I also needed to find a way to snugly secure the RPi and amp inside the box. I found a [design](https://www.hifiberry.com/blog/a-universal-base-for-the-raspberry-pi/) for a base, and got it 3D printed at my co-working space for €5! So that was the most futuristic part of the project. More sanding, more spray paint and soon there was only one thing left to do. A volume knob! I found a pretty piece of wood, got it laser cut (same place, same price, just as exciting!) and attached it to a [KY-040 rotary encoder](https://duckduckgo.com/?q=ky-040&iax=images&ia=images) (basically a turning shaft that sends pulses to the RPi). This was the first time I had to write any code: [a listener](https://github.com/carderne/volumio-rotary-encoder) for knob-turns to change the volume in the appropriate direction.

{% include image.html url="/assets/images/2020/hifi4.jpg" description="I know this seems far-fetched, but they look even better in person." class="narrow-img" %}

And that's it! They look lovely, sound amazing and work so easily, happily streaming straight from Spotify or any other app/computer. We quickly dubbed them Darcy, specifically referring to Colin Firth's representation of Mr Darcy from 1995's TV adaptation of Jane Austen's Pride and Prejudice.
