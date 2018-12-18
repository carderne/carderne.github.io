---
layout: single
title: Fun with population dynamics
date: '2014-10-23 11:41:00'
tags:
- inside
---

Several years ago, when I was still very excited about Java, and read a lot of books on evolution, I had the fun idea to combine the two. I created a simple Java program ([here on GitHub](https://github.com/carderne/Altruism) to model one of the more interesting examples of game theory used to explain the origins of altruism (and its evolutionary benefits): [The Ultimatum Game](https://en.wikipedia.org/wiki/Ultimatum_game).

I'll let Wikipedia explain:

> One player, the proposer, is endowed with a sum of money. They are  tasked with splitting it with another player, the responder. Once the  proposer communicates their decision, the responder may accept it or  reject it. If the responder accepts, the money is split per the  proposal; if the responder rejects, both players receive nothing.

So I created a simple algorithm, and since I was neck-deep in the Object-Oriented Programming way of thinking, the players in the game were naturally represented with Classes and Objects! I set up the model to accept an arbitrary number of players (in the obnoxious GIF below it was 4000) and assign each player with a 'strategy': what kind of offers they make and what kind they accept. These are represented by numbers in the model:

 1. Very generous: offers large amounts, but accepts any amount offered
 2. ...
 3. ...
 4. ...
 5. The middling player: offers half, but only accepts if half or more is
    offered
 6. ...
 7. ...
 8. ...
 9. Stingy: offers small amounts, and only accepts large offers

The players then randomly play against each other, and keep track of how much money they've won. After each round, the player with least in their coffers is... killed. Then they play again and again until there are only a few players left.

As you can see in the video below, the 5's last the longest, with their in-between strategy! Note that I didn't allow players to combine strategies, as this would have complicated it a bit, and (if I remember) there is a suggestion that the offer and accept parameters are somehow linked evolutionarily.

<iframe src="https://giphy.com/embed/t6leavMMQwBQIrYiTo" width="480" height="378" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/t6leavMMQwBQIrYiTo"></a></p>