---
layout: single
title: "Python in the browser"
date: "2022-07-23"
excerpt: "Much easier than you think"
---

I often work at the interface between science and "tech". The tech is sometimes deep learning with satellite imagery, and sometimes clicky maps, and often other duller things.
Sometimes I work with scientists who prefer to stay on their side of that interface.
This means they begrudgingly learn Python, but do not want to learn JavaScript (and why should they).
Recently I was making a clicky web map for some of these scientists, and to make their lives easier, I decided to finally figure out how to get Python running in the browser.

And it's dead easy!

I'm a complete novice to the world-wide
[wasm](https://en.wikipedia.org/wiki/WebAssembly), but had remembered seeing
[PyScript](https://pyscript.net/),
[Brython](https://brython.info/), and
[Skulpt](https://skulpt.org/) making the rounds of social media-ish places.

I played around with the first two of these, but quickly realised they were overkill for me:
I'm not entirely sure what PyScript's niche is, but Brython is aiming to be a full DOM-manipulation language.
I just wanted some Python to run and expose a pure function communicating via JSON with the rest of my JavaScript app.
Basically a Python backend, but right there in the browser.

So I went right to the source: [Pyodide](https://pyodide.org/en/stable/), which is a complete port of CPython to WebAssembly, along with the bits needed to install common data-sciencey libraries.
It also has great documentation for both the JavaScript API (initialising things, helper functions etc) and the Python API (helpers, wrappers for things like `fetch`).

All it takes to get going is to pull the library in from a CDN in your `index.html`:
```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Python in the browser</title>
        <script defer
            src="https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js">
        </script>
    </head>
    <body>
        <script type="module" src="./main.js"></script>
    </body>
</html>
```

Then let's say we have the following Python script written by the scientists.
(In reality we'd want to enforce some static real type-checks here so they don't bring down a production website!).
```python
# funcs.py
def func(data: dict) -> dict:
    print(data)  # this will log to the console
    return {"msg": "Hello JS!"}
```

Then there are just a few simple steps to get make this available to your JavaScript app.
First load Pyodide and fetch the Python code.
```javascript
const pyodide = await loadPyodide({ fullStdLib: false });
const pyFuncText = await (await fetch("./funcs.py")).text();
```

Then you run the fetched code, which will make the Python function `run_model` available in the global Python namespace.
This can then be bound to a JS function name.
```js
pyodide.runPython(pyFuncText);
const func = pyodide.globals.get("func");
```

The function is almost ready to be used like normal, but there's one last step,
which is to convert the arguments to Python-esque objects, and then convert the returned results back to a JSON-esque object.
Like so:
```js
const func_js = (data) =>
  Object.fromEntries(func(pyodide.toPy(data)).toJs());
```

Then you can use the function like normal, eg `const res = func_js({"baz": "qux"})`.

Putting it all together, we might have the following:
```js
// main.js
const getPythonFunc = async (path) => {
  const pyodide = await loadPyodide({ fullStdLib: false });
  const pyModelText = await (await fetch(path)).text();
  pyodide.runPython(pyModelText);
  const func = pyodide.globals.get("run");
  return (data) =>
    Object.fromEntries(func(pyodide.toPy(data)).toJs());
};

(async () => {
  const func = await getPythonFunc("./funcs.py");
  const res = func({"hello": "Python"});
  document.body.innerText = res.msg;
})();
```

And that't it!
