---
layout: single
title: "Beyond Hypermodern: Python is easy now"
date: 2024-07-19
excerpt: Postmodern, anyone?
image: /assets/images/2024/postmodern.png
---
{% include image.html url="/assets/images/2024/postmodern.png" description="" class="narrow-img" %}

It feels like eons, but it was actually just four years ago that [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/) did the rounds, going over the latest Best Practises™ for Python tooling. I remember reading it with a feeling of panic: I need to install like 20 packages, configure 30 more and do all this _stuff_ just to write some Python.

But now it's 2024, and it's finally all easy! A bunch of people saw how easy all this stuff was in Go and Rust, and did some amazing work to drag the Python ecosystem forward. It's no longer clever or special to do this stuff; everyone should be doing it.

If you just want the template, it's coming below in the TLDR. Otherwise hang in, I'm going to follow much the same structure as the original Hypermodern posts, as follows:
1. [Setup](#setup)
2. [Linting](#linting)
3. [Typing](#typing)
4. [Testing](#testing)
5. [Documentation](#documentation)
6. [CI/CD](#cicd)
7. [Monorepo](#monorepo)  (bonus section!)

If you're already using Rye and friends, much of this won't be new to you. But the monorepo section is where things get more interesting and there might be some new ideas there!

**TLDR** Here's the template repository: [carderne/postmodern-python](https://github.com/carderne/postmodern-python). Start from there, and the README will give you all the commands you need to know.

## Setup
Out with [pyenv](https://github.com/pyenv/pyenv) and [Poetry](https://python-poetry.org/), in with [Rye](https://rye.astral.sh/){%- include fn.html n=1 -%}. Created by Armin Ronacher (creator of [Flask](https://flask.palletsprojects.com/en/3.0.x/)), and now adopted by [Astral](https://astral.sh/), Rye is the new cool kid on the block. Despite the VC-backed vibes of Astral, it's actually really well-thought-through and entirely based on the new Python packaging standards. Unlike Poetry, which did what was necessary before those standards existed, but is now just a bit weird and unnecessarily different.

Rye will also install Python for you, creating and respecting a `.python-version` in the process. Then it helps you manage your `pyproject.toml` dependencies in a standard way (or leaves you to do it yourself), creates lock files (but normal ones that `pip` can understand, not Poetry-specific ones) and mostly gets out of the way. And because it's all written in Rust (duh), it's _fast_. It also bundles a linter and formatter, which will make our later section a bit shorter.

Convinced? Let's start. First off, install [Rye](https://rye.astral.sh/):
```bash
# if you don't like doing this, go to their website and find another way
curl -sSf https://rye.astral.sh/get | bash

# use PDM instead of Hatch (I'll explain why in the Monorepo section)
rye config --set default.build-system=pdm
# and use the "compatible operator" rather than ">= operator"
rye config --set default.dependency-operator='~='
```

Rye should have created a config directory with a config (modified by the command above) at `~/.rye/config.toml`. Python versions will also be installed into that directory, while virtual environments will be created inside your project (just like `node_module/` and similar).

So let's start a new project:
```bash
mkdir postmodern
cd postmodern
rye init       # create pyproject.toml and .python-version
rye sync       # create lockfiles and install Python + deps
```

Rye will create some structure and setup files for you.
```bash
$ tree .

.
├── .git                   # Rye was polite enough to init a git repo
├── .gitignore             # along with some standard ignores
├── .python-version        # and a Python version
├── .venv
│   └── ...                # deps will be installed here
├── pyproject.toml         # manage dependencies and all config
├── requirements.lock      # lockfile for deps
├── requirements-dev.lock  # ditto for dev deps
└── src
    └── postmodern
        └── __init__.py    # code goes here
```

Rye defaults to a `src/postmodern/` layout, but you can also just do `postmodern/` if you prefer (I generally do). The only really interesting thing here is the `pyproject.toml`. A quick history lesson: Python used to use a `setup.py` script for installing libraries, which everyone agreed was crazy. There was a brief dalliance with `setup.cfg` but then [PEP-518](https://peps.python.org/pep-0518/) [/PEP-621](https://peps.python.org/pep-0621/)/[PEP-631](https://peps.python.org/pep-0631/) came along and saved the day by standardising around `pyproject.toml`. Poetry started in the middle of all this, so it had to invent its own system. But now we have standards, so let's have a look:
```toml
[project]
name = "postmodern"
version = "0.1.0"
description = "Add your description here"
authors = [{ name = "Your Name", email = "you@example.com" }]
readme = "README.md"

# If you're building a public library, you'll want to be more lenient
# with the Python versions you permit. If this is internal, then you
# should use Python 3.12
requires-python = "~= 3.12"

# Your empty (for now) dependency table
dependencies = []

[tool.rye]
managed = true
# This is where testing and formatting tools will go
dev-dependencies = []

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
```

Now you can install dependencies by running for example `rye add pydantic` which will add it to your dependency table. Note that we told Rye to use `~=` rather than `>=`. This means we won't get accidentally upgraded to Pydantic v3, which could break stuff.
```toml
dependencies = [
    "pydantic~=2.8.2",
]
```

You can also just edit these dependencies manually (this is what I usually do), and just run `rye sync` whenever you do, to update your `.lock` files (you shouldn't edit these manually) and your venv. Speaking of lockfiles, let's have a look:
```python
-e file:.                    # install the current directory in editable mode
annotated-types==0.7.0
    # via pydantic           # the comments explain why each dep is there
pydantic==2.8.2
    # via postmodern
pydantic-core==2.20.1
    # via pydantic
typing-extensions==4.12.2
    # via pydantic
    # via pydantic-core
```

### Make it runnable
There are a few different kinds of project you could be building, and that affects the kinds of things you'll want to add to the above. If you're building an a CLI tool or similar, there are two things you might want to add, depending on how you're expecting people to use it. The one is a `__main__.py` next to your `__init__.py`. This lets people run your code using `python -m postmodern` which is vary handy if they don't want to mess with their `$PATH`.
```python
# postmodern/__init__.py
def main() -> None:
    print("Hello!")

# postmodern/__main__.py
from postmodern import main
main()
```

The next is to add a script in the standard Python way. The example below will mean that, after installing your library/app with `pip`, it will be added to their `$PATH` and they can run it as `postmodern` from the command line.
```toml
# add this to your pyproject.toml
[project.scripts]
# run `postmodern` will run the `postmodern.main` function
"postmodern" = "postmodern:main"
```

Thanks to [harkabeeparolus](https://github.com/harkabeeparolus) for pointing out that you can also just run `rye init --script` which will do both of these things for you!

### Public projects
Of course if your code will only ever be imported, you don't need an entrypoint. But if you're building a public package (i.e., you'll publish it to [pypi](https://pypi.org/)), you should decide how many Python versions you want to support, and set the `requires-python` value appropriately. Python 3.8 is [about to hit end-of-life](https://devguide.python.org/versions/) so I think it's reasonable to support `>= 3.9` only. If you think your users are more cutting-edge you can nudge higher. The only downside of supporting older versions is missing out on the many improved things in [3.10](https://docs.python.org/3/whatsnew/3.10.html), [3.11](https://docs.python.org/3/whatsnew/3.11.html) and [3.12](https://docs.python.org/3/whatsnew/3.12.html).

If it's an internal library or app, you should use a single version of Python across your libraries (and it should be Python 3.12) and you should manage a global lockfile (more on that [below](#monorepo).)
### Getting along with other Pythons
There's one last thing to mention: Rye is great for managing Python projects, but it's not as good for random short-term Python environments for messing around, where bootstrapping a bunch of pyproject.toml stuff feels like overkill. You can try out using a "[Virtual Project](https://rye.astral.sh/guide/virtual/)" in Rye, but you can also just continue using pyenv+virtualenv. Just change this setting in Rye:
```bash
rye config --set behavior.global-python=false
```

That will tell Rye to butt out of your other dirs where you want the `python` command to point somewhere else. Not that you asked, but I'd recommend checking out [mise-en-place](https://mise.jdx.dev/) as a replacement for pyenv, as it can also manage Node versions (so you can delete asdf), Ruby version etc...

## Linting
(And formatting). The original series has Testing next, but I think Linting, formatting, and Typing naturally come before Testing. This section will be very short. Throw out `black` and `isort` and `flake8` and all the rest, because [Ruff](https://docs.astral.sh/ruff/) now does everything they did, and Ruff comes for free with Rye!

So all you need to do is:
```bash
rye fmt         # runs `ruff format`
rye lint --fix  # runs `ruff check --fix`
```

And that's basically it! Except you obviously want a bit of control over how this works, so you can add the following to your pyproject (and fiddle with it as you like):
```toml
[tool.ruff]
# if this is a library, enter the _minimum_ version you
# want to support, otherwise do py312
target-version = "py312"
line-length = 120  # use whatever number makes you happy

[tool.ruff.lint]
# you can see the looong list of rules here:
# https://docs.astral.sh/ruff/rules/
# here's a couple to start with
select = [
	"A",    # warn about shadowing built-ins
	"E",    # style stuff, whitespaces
	"F",    # important pyflakes lints
	"I",    # import sorting
	"N",    # naming
	"T100", # breakpoints (probably don't want these in prod!)
]
# if you're feeling confident you can do:
# select = ["ALL"]
# and then manually ignore annoying ones:
# ignore = [...]

[tool.ruff.lint.isort]
# so it knows to group first-party stuff last
known-first-party = ["postmodern"]
```

Anyway, that's all you need to know for linting (and formatting). Obviously you should get these integrated into your editor, but I'm [not going to tell you how to do that](https://rdrn.me/neovim/).
## Typing
Types! Some people [don't like types](https://remysharp.com/2024/02/23/why-my-code-isnt-in-typescript) but writing maintainable, multi-contributor software in 2024 without types is some kind of black magic (that is best avoided). Many pixels have been spilled about the pros and cons of Python's approach to typing, and while it's great that for quick scripts and experiments you can ignore it, if you're starting something you except to care about in a few weeks, start with strict mode from day one. Don't wait until the debt builds.

Hypermodern Python recommended [mypy](https://mypy.readthedocs.io/en/stable/), but that's hard to do anymore except in specific cases. Pyright is [faster and generally a bit more useful](https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md), and plays much better with your [LSP](https://microsoft.github.io/language-server-protocol/) (editor), which is where instant type feedback is most useful. The downside is it runs on Node and needs to download the rest of the universe to work, but until someone rewrites it in Rust, that's where we are.

So first install it:
```bash
rye add --dev pyright

# Then you can check your work
cat pyproject.toml | grep pyright -C1
# dev-dependencies = [
#    "pyright~=1.1.372",
# ]
```

Then [configure it](https://github.com/microsoft/pyright/blob/main/docs/configuration.md) in your pyproject as below. Note we enable strict checking, which is really the most useful for a multi-contributor project. You can always add `type: ignore` to lines you can't fix, or disable specific rules that annoy you.
```toml
[tool.pyright]
venvPath = "."          # rye installs the venv in the current dir
venv = ".venv"          #       in a folder called `.venv`
strict = ["**/*.py"]    # use 'strict' checking on all files
pythonVersion = "3.12"  # if library, specify the _lowest_ you support
```

And now you can run it with `rye run pyright`. And, as with the formatters/linters, you should get it integrated with your editor.
## Testing
Good old [pytest](https://docs.pytest.org/en/8.2.x/) has yet to be disrupted. How and where and why to write your tests is a whole thing that I'm not going to wade into now. Linting and strict type-checking will get you far in life, but a good set of fast tests will do wonders to keep your code working and, if they're reasonably concise, well-documented too.

From a nuts-and-bolts perspective all we need to do is install pytest:
```bash
rye add --dev pytest
```

I'll leave the testing to you, but we can setup a useless example to make sure that everything is working.
```python
# tests/test_nothing.py
def test_nothing() -> None:
    assert True
```

Now that we have a couple of tools setup, we may as well make it a bit easier to remember how to run them. You could always use a `Makefile`, but Rye has nice support for running simple scripts like this, so add this to the top (where it's easy to find) of your pyproject:
```toml
[tool.rye.scripts]
fmt = "rye fmt"
lint = "rye lint --fix"
check = "pyright"
test = "rye test"
all = { chain = ["fmt", "lint", "check", "test"] }
```

Then any time you've made some changes or are preparing to commit, you can run `rye run test` or just run `rye run all` and the full suite of tools will get to work for you!

My predecessor recommended setting up [nox](https://nox.thea.codes/en/stable/) for automated testing in multiple Python environments. If you don't know what this means, or haven't heard of nox, then you probably don't need it. Unless you're writing a public library targetting multiple versions of Python, you don't need it. Even then, depending on the complexity of your project, you can probably get away with CI/CD alone (more below)x. And the simpler parts of nox (chaining linting, typechecking, testing) are already handled above by five lines of pyproject config.

## Documentation
We're getting slightly away from tooling and into the weeds here, but in general my advice would be to focus on getting as much information as possible into function/class names and type signatures.

For example:
```python
# instead of
def filter_stuff(accounts, include_closed):
	...

# or even
def filter_accounts(
	accounts: list[dict],
	include_closed: boolean
) -> list[dict]:
    ...

# why not try try
class Status(Enum):
    CLOSED = 0
    OPEN = 1

@dataclass
class Account:
    id: str
    status: Status 

def filter_account(
    accounts: Sequence[Account],
    include: Sequence[Status],
) -> list[Account]:
    ...
```

And then add docstrings to your functions and classes. Your code is fully typed, so you might not need to explain too much what goes into each parameter or what functions return. One thing you should definitely do is explain what types of Exceptions a function can raise! Maybe one day the language will have a built-in way of expressing that...
```python
def filter_accounts(...) -> list[Account]:
	"""
	Filters accounts base on the provided parameters and returns a copy.

	Be careful of calling this with Accounts that bla bla...

	Raises:
		AccountBalanceException: an Account was found that foo bar...
	"""
```

The next thing you should do is write tests! I know, we covered that. But the clearest way to show what a bit of code does, is to _show what that bit of code does!_ And also to show what it doesn't  (or isn't supposed to) do. You may need some super complex multi-stage tests to validate all sorts of stateful conditions, but if you can start with a few very simple, easy to understand tests, future you and your users will have a much easier time understanding how something works. And if they're wondering how `filter_accounts` works, they can grep for `test_filter_accounts` and maybe find the answer.

An even better solution, and something that has been done to great effect in Rust, is to add tests to your docstrings as in the example below. Not only are these super useful to the users of your code, pytest will ensure that they stay up-to-date by failing your test suite if the tests fail!
```python
# postmodern/adder.py

# you can ignore the fancy Python 3.12 generic syntax if you like
def add_two[T: (int, float)](num: T) -> T:
	"""
	Adds two to the given `num`

	>>> res = add_two(0.5)
	>>> assert res == 2.5

	>>> res = add_two(1)
	>>> assert res == 4    # note this is wrong!
	"""
	return num + 2
```

To get pytest in on this, add the following to your config:
```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--doctest-modules"
```

Then when you run `rye run test`, you'll get an error something like below, so can can fix the test and get it green again.
```bash
_________ [doctest] postmodern.adder.add_two _________
005     >>> res = add_two(0.5)
006     >>> assert res == 2.5
007
008     >>> res = add_two(1)
009     >>> assert res == 4
UNEXPECTED EXCEPTION: AssertionError()
```

And if you're writing a public library, you'll likely want public documentation at some point. You can probably get quite far with a GitHub readme and good docstrings, since modern editors make it so easy to `goto-definition` on source files. Sphinx or Mkdocs are the next steps. You'll know when you need them, and they're not worth the trouble until then.

## CI/CD
We're nearly there! Sharp-eyed readers will notice I didn't include [pre-commit](https://pre-commit.com/) anywhere above. This depends on your team and preferences, but there are cases where pre-commit becomes a bit of a configuration burden, doesn't play well with polyglot codebases (eg you also want to pre-commit your TypeScript code) and can just be annoying. So I've excluded it by default, and we'll instead rely on our CI.

### Integration
What you definitely do need, whether you use pre-commit or not, is enforced no-commit-to-main on your repository and then a good CI pipeline running on your PRs that must be green before code is merged to main.

Here's a simple example that runs all of our tools above on Github Actions. I've kept this as brief as possible, but you can see the fully-featured version [at the repository](https://github.com/carderne/postmodern-python/blob/main/.github/workflows/pr.yml). This will ensure, more strictly than pre-commit can, that everything that hits main is sparkling clean.
```yml
# .github/workflows/pr.yml
name: pr
on:
  pull_request:
    types: [opened, reopened, synchronize]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: eifinger/setup-rye@v3
      - run: rye pin 3.12         # pin your Python version
      - run: |                    # abort if the lockfile changes
          rye sync
          [[ -n $(git diff --stat requirements.lock) ]] && exit 1
      - run: rye fmt --check      # check formatting is correct
      - run: rye lint             # and linting
      - run: rye run check        # typecheck too
      - run: rye run test         # then run your tests!
```

And since I recommended against using nox (until you know you need it), this is also the spot to setup your multi-version/multi-platform testing. Github Actions allows you to define [matrix strategies](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs), where you can test a matrix of versions, platforms, etc. To add a strategy, we make these two additions to our `pr.yml` workflow:
```yml
    # after runs-on: ubuntu-latest
    strategy:
      matrix:
        py: ['3.10', '3.11', '3.12']

	# replace the rye pin step
	  - run: rye pin ${{ matrix.py }}
```

And that's it! Now your code will get tested against two additional Python version.
### Deployment
If you're building a library, you might be done once your code is merged. If it's a public library, you must tag and release a version, and push it to PyPI. You'll also need to set a version. You can either set one manually:
```toml
[project]
name = "postmodern"
version = "0.1.0"
...
```

Or do it dynamically:
```toml
[project]
name = "postmodern"
dynamic = ["version"]
...

[tool.pdm.version]
source = "scm"
```

The latter approach will get the version from the git tag, and saves having to manually bump stuff all over the place. Also note that you don't need to set a `__version__ = "0.1.0"` anywhere in your code. Interested parties can get it with:
```python
from importlib.metadata import version
version("postmodern")
```

With that done, you need to actually publish it. The Github Actions workflow below shows how you can do that. For this to work, you'll need to set up ["Trusted Publisher" with PyPI](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/). This allows you to publish without needing to copy-paste keys around (see, no keys in the workflow below!).
```yml
name: release
on:
  release:
    types: [published]
jobs:
  publish:
    environment: release       # needed for PyPI OIDC
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build && python -m build       # build
      - uses: pypa/gh-action-pypi-publish@release/v1    # publish
```


So that's libraries. But if you're building an App, and if that app needs to run somewhere, you probably want a Dockerfile. This is another area where things are simpler without Poetry. Since we have a standard `pyproject.toml` and standard requirements.txt files (except they have a `.lock` extension), we don't need Rye anywhere near the deployment process, just Python and pip. The Dockerfile below shows how simple this can be.
```Dockerfile
# always nice to pin as precisely as possible
FROM python:3.12.2-slim-bookworm

ENV PYTHONUNBUFFERED True
WORKDIR /app

# First we copy just the project definition files
# so these layers can be cached
COPY pyproject.toml requirements.lock ./

# remove the line that would make it install the app itself
# since we haven't copied that yet
RUN sed -i '/^-e file:/d' requirements.lock
RUN pip install . --constraint requirements.lock

# now copy in all the rest as late as possible
# and depending on how we're running this, we don't even need
# to install it, just copy-paste and run
COPY . ./

# if you DO want to install it, do that here

# or however else you bootstrap your app
CMD ["python", "/app/postmodern/main.py"]
```

I'll wait while you go compare that to the Poetry approach, and I'll wait for you to figure out how to set up a multi-stage build so you don't have a pile of unneeded Poetry stuff left lying around in your final Docker image.
## Monorepo
This is the bonus section that was promised! If you're building a library or a one-off, you might already be done. But if you're building something in a big team, and you don't have a monolith, you're likely to have multiple apps and libraries intermingling. Python's monorepo support isn't great, but it works, and it is far far better than the alternative repo-per-thingie approach that many teams take. The only place where separate repos make much sense is if you have teams with _very_ different code contribution patterns. For example, a data science team that uses GitHub to collaborate on Jupyter notebooks: minimal tests or CI, potentially meaningless commit messages. Apart from that, even with multiple languages and deployment patterns, you'll be far better off with a single repo than the repo-per-thing approach.

So, how do you monorepo with Python? If you're in a bigger organisation, you might already have [Bazel](https://bazel.build/reference/be/python) or similar ([Pants](https://www.pantsbuild.org/), maybe?) set up for building your graph of libraries and dependencies. Although Python doesn't need to be "built" per se, a bunch of stuff does need to be installed and copied around and having these dependencies and connections properly controlled is valuable.

If your needs aren't (yet) that complex, you can get quite far with the standard modern tooling. Rye has borrowed from Go/Rust the concept of a "workspace" that contains multiple packages that share a root. Notably, they share a lockfile (`requirements.lock` in this case). You need to decide how coupled you want your teams to be, but it's very likely that larger teams will need multiple workspaces in the single monorepository. This is because you can easily end up with incompatible versions, where, for example, Team A is using a library that enforces `pydantic<1.0` while Team B is desperate to use another library that requires `pydantic>=2.0`.

It's an organisational choice the degree to which you want to keep everyone in lockstep versus giving the flexibility to use different versions. But definitely the number of separate lockfiles should be kept as low as possible. Regardless, you'll end up with something that looks like this:
```bash
$ tree .

.
├── .git
├── .venv
├── workspace1               # maybe this is more "web" stuff
│   ├── pyproject.toml       # this only defines the workspace
│   ├── requirements.lock    # lockfile for this workspace
│   ├── .venv                # venv for this workspace
│   ├── libA
│   │   ├── pyproject.toml   # a normal pyproject for this package
│   │   └── libA
│   │       └── __init__.py  # library code here
│   └── appA
│       ├── pyproject.toml
│       └── appA
│           └── __init__.py  # app code here, probably imports libA
└── workspace2
    └── ...                  # separate venv, lockfile etc
```

So, how do you make this work. First of all, have a glance at the Rye [Workspace docs](https://rye.astral.sh/guide/workspaces/). Then let's create the pyproject that defines our first workspace:
```toml
# workspace1/pyproject.toml
[project]
name = "workspace1"
[tool.rye]
managed = true
virtual = true              # the workspace itself is not a package
[tool.rye.workspace]
members = ["lib*", "app*"]  # these are the packages that are included
                            # choose globs that make sense for you
```

Then you can create your library and app projects as usual. But there are a couple of gotchas around interdependencies that aren't very well-documented. I recommended way up at the start of this post to tell Rye to use the [PDM build backend](https://backend.pdm-project.org/) because it handles this situation slightly better than the the default [Hatch](https://github.com/pypa/hatch), although this might not be the case for long.

The core complexity is this: you have a single virtual environment, so everything is installed and available all the time. If `libA` has `pydantic` as a dependency, in your _local development_, `appA` will be able to import pydantic as well; but in _production_ (which we'll cover in a bit) it definitely won't. In addition, you shouldn't try to do `rye add libaA --path ../libA` from `appA`: it will work but it will use the absolute path to that lib, which means it won't work for anyone else.
### Testing dependencies in isolation
The first thing is to make sure that your PR CI process runs its tests with the correct non-global dependencies installed. This is very simple: in the Github Actions workflow, instead of using Rye, just use plain pip as you did in the Dockerfile:
```yml
# <snip>
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          # as with the Dockerfile, pip doesn't like 'file:.' entries
          sed -i '/^-e file:/d' requirements-dev.lock
          pip install libA --constraint requirements-dev.lock
          pip install ruff pyright pytest --constraint requirements-dev.lock
      - run: python -m ruff format --check
      - run: python -m ruff lint
      - run: python -m pyright
      - run: python -m pytest
```

So there's a downside that in local dev, you may accidentally import a library without realising you don't actually have it installed in that package, but at least your CI will catch you.
### Internal dependencies
So how we do we start using `libA` from `appA`? There's no standardised method (yet), but I'll explain one approach. To start with, _manually_ add the following to appA's pyproject (this is the standardised method to specify [optional dependencies](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#optional-dependencies)):
```toml
[project.optional-dependencies]
local = [
  "libA @ file:///${PROJECT_ROOT}/libA",
]
```

That `${PROJECT_ROOT}` is how PDM gets around Python's aversion to relative paths. It will inject the correct path at build-time. The above "local" dependency will be ignored by Rye during development, but then you can bring it into action during tests and builds by doing something like this:
```bash
# in place of
# COPY . .
# RUN pip install . --constraint requirements.lock

# we instead do the following (from workspace route)
COPY appA appA
COPY libA libA
RUN pip install 'appA[local]' --constraint requirements.lock
```

This is intentionally left a bit vague, as how exactly you want to manage this will depend on your team's preferences for clever-and-automated vs simple-and-reasonable solutions. For example, the Dockerfile above forces you to manually `COPY` the dependencies that you want for each library; a fancier solution would involve a script that automatically parses the pyproject.toml to figure out what's needed, copies just those directories into a build area, runs the Docker build... which is great and works, but people need to be on board with what exactly that script/process is getting up to!

If anyone gets in touch and wants to see the fully-fledged version and working monorepo I'll be happy to write another post, but I suspect this is the point at which preferences and working styles overwhelm a cookiecutter approach. The alternative is to set up Bazel or Pants, or something like [Polylith](https://davidvujic.github.io/python-polylith-docs/), but all of those will also require significant buy-in from your team.

And remember: even if the above sounds like a bit of a pain, it's still not a reason to have a hundred repos! You can just have a hundred non-workspaced packages instead, and use whatever dependency process you were already using.

That's that. Hopefully that was useful! Things have come a long way since Hypermodern Python was published, and writing maintainable Python has never been easier.
