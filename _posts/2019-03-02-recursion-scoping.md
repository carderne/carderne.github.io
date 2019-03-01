---
layout: single
title: "Fun with recursion and scoping"
date: "2019-03-02"
excerpt: "Creating a smart, tree-aware algorithm for optimising electrical networks led to an interesting exploration of recursion and variable scoping."
tags:
- inside
---

Part of the core algorithm in [openelec](https://openelec.me/) is a routine that finds the best (read: cheapest) way to connect villages. This is based on a [minimum spanning tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree) but, as the MST doesn't know about the existing grid (or the village populations, or whether there's a mountain between villages), I had to layer something on top of that. This 'something' (discussed [here](https://rdrn.me/modelling-universal-electrification/) about halfway down the page) starts at currently connected villages and explores outwards along the tree, finding the best configuration that brings electricity to the most people (or the highest demand) with the shortest amount of new wire. Naturally, this calls for a recursive function, which led to a fun exploration of variable scoping.

I find recursion very interesting, as it presents a completely different way of iterating through a task (compared to a `for` loop) that's a bit harder to wrap your head around, but often much more intuitive, and sometimes the only way of doing something. As a basic example, consider the function below:

```python
def recurse(keep=0, throw=0):
    keep += 1
    throw += 1
    if keep < 3:
        keep, _ = recurse(keep, throw)        
    return keep, throw

recurse()
```

Which outputs `(3, 1)`. This is because, although both variables have been iterated each time the function is called, `throw` is not 'saved' as control bubbles back up the stack. For a more interesting example, consider the tree below. Imagine that we start at `a` and want to find the route to `(e)`: a-c-e!

            a
           / \
          b   c
         /   / \
        d  (e)  f

Let's start by creating the objects to represent our tree. Each node is its own object, and all it knows is whether it's the target, and who its children are. And we give them names to make our lives easier.

```python
class Node:
    def __init__(self, name, target=False):
        self.children = []
        self.name = name
        self.target = target
    def add(self, *new):
        self.children.extend(new)

a = Node('a')
b = Node('b')
c = Node('c')
d = Node('d')
e = Node('e', True)
f = Node('f')
a.add(b, c)
b.add(d)
c.add(e, f)
```

Then we're ready to use a recursive function to find the solution. The first attempt is shown below. Every time the function is called, it adds the current node to `current` and then explores downstream from there. If the target is found, it copies `current` into best. Thus we expect that `best` will only contain the nodes that lead to the target, and the rest will never have bubbled back up the stack (as `current` is never returned).

```python
def explore(node, current=[], best=[]):
    current.append(node.name)
    if node.target:
        best = current
    for child in node.children:
        best = explore(child, current, best)
    return best
        
explore(a)
```

But this outputs `['a', 'b', 'd', 'c', 'e', 'f']` (that is, every node). This is because, in Python, assignment with `=` doesn't create objects; it creates a binding between a name and an object. With unmutable objects (2, for example, will always be 2), this does what we expect. But with mutable objects (such as lists), even though the scope would suggest we're dealing with a new variable, in actual fact they're all pointing to the same underlying object. As a demonstration, consider the following:

```python
foo = [1]
bar = foo
bar.append(2)
print(foo)
```

This outputs `[1, 2]`, because foo and bar are bound to the same underlying object. We can fix this by replacing `bar = foo` with `bar = foo.copy()`, and then we'll get the output that we expect (`[1]`). [`copy`](https://docs.python.org/2/library/copy.html) gets around this by copying the actual values (and using `deepcopy` you can go even further). So applying the same logic to our tree-search function, if we add `current = current.copy()` at the beginning of the function, we can force a locally scoped version of `current`.

```python
def explore(node, current=[], best=[]):
    current = current.copy()
    current.append(node.name)
    if node.gold:
        best = current
    for child in node.children:
        best = explore(child, current, best)
    return best
        
explore(a)
```

And voilà, it produces `['a', 'c', 'e']`, as expected.

