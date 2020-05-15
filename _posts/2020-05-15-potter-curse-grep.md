---
layout: single
title: "Harry Potter and the Curse of the Grep"
date: "2020-05-15"
excerpt: "Adverbs, adverbs, every where, nor any use for them. (aka Rowling's editor needed regular expressions)"
tags:
- inside
---

I know I'm not the [first](https://www.livemint.com/Leisure/i8wjh4uNOfjbcZNuVvMPQM/The-adverbs-that-gave-JK-Rowling-away.html) [person](https://www.livewritethrive.com/2015/11/23/oh-those-lovely-adverbs/) to notice this. But it's fun anyway. Also: I don't have a problem with either Harry Potter or adverbs.

Someone (who shall remain nameless) has been blasting her way through the Harry Potter series as a way of dealing with the pandemic, and was unfortunate enough to notice Rowling's, umm, creative ways with adverbs. After her umpteenth <span style="color:#AF4E38">lazily</span>, I couldn't stand by idly (cough) any longer, and had to get involved. With grep of course! Except actually with [ripgrep](https://github.com/BurntSushi/ripgrep) because it's super fast and has pretty colours.

I converted all seven ebooks to plaintext, dropped them in a directory together and got to work. (In all the following, you can replace `rg` with `grep` and the output should be much the same.) The first issue was that she recalled one particular offender, but only remembered that it was an adverb that started with a *p*... No problem:

```bash
rg " p[[:lower:]]{3,}ly"
# match a space
# followed by a 'p'
# followed by at least 3 lower case letters
# followed by 'ly'
```

Just within Harry Potter and the Order of the Phoenix (the tome in question), there were 202 matches! This prints out a massive wall of text (as the full context for each match is printed too) but this makes the sleuthing more enjoyable. Nonetheless, in a few moments the culprit is found:

> The class stared <span style="color:#AF4E38">perplexedly</span> at her and then at each other. Harry, however, thought he knew what was the matter.

Let's dig into some more analysis (and chuckles)

To make this a bit more amenable to analysis (and chuckles), let's drop the context, and count the number of uses of each unique adverb.

```bash
rg " p[[:lower:]]{3,}ly" -o | sed 's/^.*: //' | sort | uniq -c
# same regex
# -o (for --only-matching) leaves out the context
# sed to get rid of the line number (could also do with rg's --no-line-number and --no-filename)
# sort alphabetically
# unique values with counts
```

Which gives us this:

```python
      2 perplexedly
     13 personally
      1 piercingly
      1 pimply
      1 pitilessly
      1 pityingly
      3 placidly
     30 plainly
      1 playfully
      1 pleadingly
      9 pleasantly
      1 pleasurably
      5 pointedly
      2 pointlessly
      1 poisonously
      9 politely
      2 pompously
```

Perplexedly strikes twice, as does pompously and a horde of others: 61 different -ly words starting with a p! Let's go one step further and look for phrases that match the pattern verb-person-adverb, e.g. "said Snape snappishly":

```bash
rg " [[:lower:]]{4,} [[:upper:]][[:alpha:]]+ [[:lower:]]{4,}ly" -o | sed 's/^.*://' | sort | uniq -c
# match a space
# followed by a word with at least 4 lower-case letter
# followed by a space
# followed by an word starting with an upper-case letter
# followed by a space
# followed by our familiar adverb pattern, but this time with any first letter
```

This has a lot of false positives, such as "whole Weasley family", but also unearth such joys as:

> whispered Hermione <span style="color:#AF4E38">desperately</span> (she also whispers gleefully)

> thought Harry <span style="color:#AF4E38">scathingly</span> (he also thinks bitterly and miserably)

> squeaked Dobby <span style="color:#AF4E38">confidentially</span> (he also squeaks angrily, anxiously, and happily)

> said Umbridge <span style="color:#AF4E38">sleekly</span> (she does this twice, along with breathlessly, curtly, eagerly, furiously, harshly, impatiently, loudly, quietly, shrilly, silkily, smugly, softly, 4x sweetly, swiftly, and triumphantly)

> said Ron <span style="color:#AF4E38">weakly</span> (seven times! his favourite way of saying behind suddenly, slowly, sharply, quietly, quickly, loudly, irritably, impatiently, grumpily, furiously, excitedly, eagerly, darkly, bitterly, and angrily)

> said Percy <span style="color:#AF4E38">pompously</span> (twice!)

> said Hermione <span style="color:#AF4E38">sharply</span> (her preferred method, at 18 times)

> said Harry <span style="color:#AF4E38">incredulously</span> (four times, also irritably, exasperatedly, dispiritedly, and a host of other ways)

All in all, this pattern repeats itself 2860 times throughout the books!

One last thing, let's get a quick adverb count per 10,000 words. The following snippet goes through all files in subdirectories, gets the number of adverbs, then the total word count, then divides them.

```bash
for f in **/*.txt; do
    matches=$(rg " [[:lower:]]{4,}ly" --count-matches --no-filename -g "$f")
    wordcount=$(cat $f | wc -w)
    echo $f $(echo "10000*$matches/$wordcount" | bc)
done
```

And we have the following counts. Note that this is counting any words that match the pattern, so we have false positives (like 'family') and probably some false negatives as well (such as 'fast'). In general this is probably over-predicting on average.

```python
Philsophers Stone        107   adverbs per 10,000 words
Chamber of Secrets       153
Prisoner of Azkaban      154
Goblet of Fire           156
Order of the Phoenix     179
Half-Blood Prince        164
Deathly Hallows          112
```

So she starts off slowly, builds up to an astonishing 179 in book five (the one that started this investigation, unsurprisingly) and then settles down again (in response to critics?).

Let's have a quick look at some other authors. This was much less fun, as although there are loads of -ly words throughout, there are relatively few verb-person-adverb constructs to laugh at.

```python
                                       adverbs per 10k    vpa* per million
 JK Rowling       Harry Potter series  151                2587
 Garth Nix        Sabriel              138                337
 Leo Tolstoy      Anna Karenina        139                60
 Virginia Woolf   To the Lighthouse    124                43
 John Steinbeck   Grapes of Wrath      90                 38
 JRR Tolkien      Lord of the Rings    69                 235
 Cormac McCarthy  The Road             37                 0
 Mark Twain       Huckleberry Finn     35                 7

*vpa = verb-person-adverb
```

Unsurprisingly, *The Road* doesn't contain a single "said Snape snappishly", and *Huckleberry Finn* gets by with very few. *The Lord of the Rings* has plenty, and "said Strider suddenly" manages to sneak in twice. Tolstoy is quite generous with adverbs, and "perplexedly" even appeared in the Pevear and Volokhonsky translation. Unsurprisingly, the nearest competitor to Potter's dominance is another YA series: *Sabriel* by Garth Nix, one of my absolute favourite books then and now. But even in this case no expression is repeated more than twice, and it's a drab (but telling) "replied Sabriel distantly".

At this point I'd normally start building some charts out of this and seeing how we can analyse this in more interesting ways. For example, which character uses which adverb most often, some more interesting comparisons between authors... But instead, to show the value of a bit of bash knowledge for this kind of analysis, I'm going to show the amount of Python code necessary just to count the number of times each adverb is used within some files (what we did further up with one line in bash):

```python
import re
from pathlib import Path
from collections import defaultdict

p = re.compile(r" \w*ly")

data = []
for fi in Path().glob("**/*.txt"):
    with open(fi) as f:
        data.extend(l.strip() for l in f.readlines())

counts = defaultdict(int)
for l in data:
    m = p.search(l)
    if m:
        counts[m.group()] += 1

for k in sorted(counts):
    print(f"{k:<20}{counts[k]}")
```

And to do the whole list of books above, the Python script takes 1 second, to bash's 0.3 seconds. The big advantages of the Python approach, are that (a) I'll understand how it works in a year's time, and (b) if I wanted to now do something more interesting with that data (clustering, networks, NLP...) I would be able to without changing tools.
