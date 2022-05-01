---
layout: single
title: Visualizing book club cliques (and replacing them with AI)
date: '2018-02-15 10:58:00'
excerpt: "My book club is quite good about recording what we read each month, and noting what score each of us give each book. Let's see if it would be possible to do away with book club meetings altogether and replace my fellow book-readers with a less argumentative machine learning model."
image: /assets/images/2018/mg1.png
---

My book club is quite good about recording what we read each month, and noting what score each of us give each book (out of 13, for historical reasons) on a growing spreadsheet. The dataset is imperfect, as people have joined and left,and not everyone has read every book, but there should be enough meat for some fun.

First off, the scores look something like the table below, but with 17 more rows. Blanks are books that people either didn't read or didn't finish.

{% include image.html url="/assets/images/2018/book1.png" description="The books and their scores." %}

We then pair everyone up, and calculate a 'disagreement' standard deviation between each possible pairing, ignoring books that either person didn't read. This gives us a nice looking heat map, where higher numbers indicate a higher level of disagreement. The biggest difference is between Kyle and Jeff, whose ratings differ by an SD of 4.8. The most closely paired are Adam and me, with an SD of 1.7.

{% include image.html url="/assets/images/2018/book2.png" description="These PNGs really need transparent backgrounds." %}

Then we can use the magic of [NetworkX](https://networkx.github.io/) to visualize these cliques in a better  prettier way. Node size represents number of books read, while line weight and darkness scales by how many books a pair has in common. People's disagreements are modelled as springs, so members with closer agreements are pulled closer together on the diagram by stronger springs.

As noted, Kyle is the definite outlier, while Tim and Adam float around a bit in the middle of the network. The newer members have thinner connecting lines,while the stalwarts are connected by pleasing thick blue lines.

{% include image.html url="/assets/images/2018/book3.png" description="A network of book-club disagreements." %}

## Off the deep end: teaching a machine to book club
Finally, let's see if it would be possible to do away with book club meetings altogether and replace my fellow book-readers with a less argumentative machine learning model. Skipping over the obvious fact that there is nowhere near enough data for this to be meaningful, how closely can a model predict what score each member is likely to give a specific book?

I started off by adding additional metadata to each book we've read: genre,length and year, as well as author country, language and gender. I also decided to make the challenge a bit easier: instead of a score from 1-13, the model only needs to tell if someone liked the book, which I define as a score above 8.

Before building and training the model, the data needs to be prepared a bit more. I dropped members who hadn't read enough books, and books that hadn't been read by enough people. Non-numerical columns (such as genre) need to be replaced with binary values that the model can more easily understand. Finally, we split it into a training set (about 75% of the rows) which the model will use to learn, and a test set (the remaining 25%) that it doesn't get to see until it's time to assess its performance.

Finally, using the lovely [scikit-learn](scikit-learn.org) libraries, I created and trained a [k-NN model](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm) and ran a bunch of tests to see if it successfully managed to impersonate anyone in the book club. And in turns out that the person it impersonates best is... me! Let's see what the model thinks of itself, in terms of how well it predicts likes:

 * Accuracy (guesses that are correct): 60%
 * Precision (like identifications that are correct): 50%
 * Recall (actual likes identified): 100%
 * [F1 score](https://en.wikipedia.org/wiki/F1_score) (a balance between precision and recall): 67%

The recall may sound impressive, but in this case it is because the model is a bit trigger-ready with likes. The table below shows the test results forAI-Chris, with an L for like and a D for dislike. This makes it pretty clear why the recall is perfect, but the precision is as good as guessing. Still, 60%correct guesses is better than I expected!

{% include image.html url="/assets/images/2018/book4.png" description="AI-Chris is slightly more generous than the real me!" %}
