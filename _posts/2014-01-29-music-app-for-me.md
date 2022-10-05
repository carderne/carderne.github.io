---
layout: single
title: A music app in Java, that still works eight years later!
date: '2014-01-29 12:25:00'
excerpt: "Flexing my Java skills in high-school."
---

My high school IT class (so, 2010) culminated in a programming project – we were free to create whatever we wanted (in Java), so long as we demonstrated what we'd learned in the class. I'd started teaching myself Java two years earlier, with a very simple command-line based music organizer: you typed in metadata, had it displayed back to you in a simple table, and probably didn't expect it to still be there next time you ran the program.

In the intervening year, a friend and I had spent many late dorm-room nights fiddling with the program. Coding without internet (no StackOverflow, no new packages) seems unimaginable looking back.

So it seemed like the obvious choice to pick this up again for my high school project, but with a GUI (all the rage) and actual music-playing abilities. I hijacked an mp3 reading library [JavaZOOM](http://www.javazoom.net/jlgui/api.html), (mis-)used a lot of [javax.swing](https://en.wikipedia.org/wiki/Swing_(Java)) and created an assortment of lovely Objects, and ended up with something almost as useful as iTunes v1.0. Thus was born the [Chris Arderne Music Organiser](https://github.com/carderne/CAMO)!

Miraculously – writing this in late 2018 – the program still (mostly) works!

<video width="100%" height="500" controls>
    <source src="/assets/videos/camo.mp4" type="video/mp4">
    Your browser does not support the video tag.
    </source>
</video>
