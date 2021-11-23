---
layout: single
title: "Scaling out with Prefect"
date: "2021-11-23"
excerpt: "How to set up a production workflow on Prefect"
image: /assets/images/2021/prefect.png
---

Over the last two weeks, I went deep figuring out the best way to orchestrate some relatively involved satellite imagery and deep learning tasks. Some of the main objectives were:
1. Run on Google Cloud Platform
2. Bonus: run on AWS too without starting from scratch
3. Define jobs in Python 
4. Have a good git-centric version control system
5. Handle variable parallelism at multiple levels
6. First-class support for running jobs with different parameters
7. Ability to trigger jobs via GUI or by HTTP

I’ve played around with [Luigi](https://luigi.readthedocs.io/en/stable/) and [Airflow](https://airflow.apache.org/) in the past, and even wrote my own very light pipeline manager, using class-based [DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html) and some hacky Redis stuff to keep track of things. The main reason I rolled my own that time, and am not using Luigi/Airflow now, is their [lack of support for very heterogenous job runs](https://news.ycombinator.com/item?id=13761071) (points 5 and 6 above). In classic ELT/ETL tasks, you want to run the same DAG, more or less the same way, every x minutes/hours/days. Our use is loading/training/predicting for different areas, using different models and different imagery sources, and often with no schedule. Airflow (since quite recently) lets you specify parameters via the web interface, but provides very little visibility into the fact that a new run with new parameters is *not* the same as the previous one. It’s just not what it’s made for.

I considered rolling our own system again, using a custom scheduling app and UI, and leaving the heavy lifting to Google’s PubSub, Tasks at al., probably using [Terraform](https://www.terraform.io/) to manage the whims of our infrastructure needs.

I ultimately decided that [Prefect](https://www.prefect.io/), the newer kid on the block, was the way to go for us. Shrugging aside my concern that my dabbles in JavaScript frontend-ery had given me shiny-new-library syndrome, I got stuck into their docs and started building some pipelines. [Argo](https://argoproj.github.io/) and [Dagster](https://dagster.io/) are two other similar-ish modern tools, that could probably achieve most of our objectives, but I was drawn in by Prefect’s super-active community and Hitchhiker’s Guide to the Galaxy references. YMMV. 

I’m not going to spend too much time talking about how Prefect [Flows](https://docs.prefect.io/core/concepts/flows.html) (their word for DAG) work, and how to write them. [Others have already done a good job of this](https://towardsdatascience.com/orchestrate-a-data-science-project-in-python-with-prefect-e69c61a49074) (seriously, read that and then come back), and their [docs](https://docs.prefect.io/core/) in this area are great. I'm going to spend more time on the *infrastructure* side of things, where I found their docs less clear, but where they have some clear wins.

Like Airflow, you write your Flows/DAGs (I’ll stick to Flows from here) in Python, set up schedules if needed and manage via a web interface ([Prefect Cloud](https://cloud.prefect.io), [probably](https://docs.prefect.io/orchestration/server/overview.html)). Similarly, there is a [library of common tasks](https://docs.prefect.io/core/task_library/overview.html) (querying databases, notifying Slack), and first-class support for [parallelism](https://docs.prefect.io/core/concepts/engine.html#executors). Unlike Airflow, Flows are much more dynamic and don’t need to be specified explicitly. Unlike Airflow, the built-in parallelism support goes much deeper, which means you can forget about [Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html). And unlike Airflow, there is great support for heterogenous flow runs and a great [GitOps](https://about.gitlab.com/topics/gitops/) story. One thing Prefect lacks is [Sensors](https://airflow.apache.org/docs/apache-airflow/stable/concepts/sensors.html), to enable event-based flows.

## Writing a Flow
You’re better covered by [other](https://towardsdatascience.com/orchestrate-a-data-science-project-in-python-with-prefect-e69c61a49074) [sources](https://docs.prefect.io/core/getting_started/quick-start.html), but I’ll cover this briefly so we know what we’re talking about. A basic flow looks like this:

```python
@task
def get_letters(word: str) -> int:
    # call Python libs, shell out to bash
    return list(word)

@task
def display(letter: str):
    # or talk to Cloud services, or whatever else
    print(f"My letter: '{letter}'")

with Flow("myflow") as flow:
    word = Parameter("word")
    letters = get_letters(word)
    display.map(letters)
```

Note that the `Flow` block can't have any "business logic", and is only allowed to define the relationship between tasks! The `map()` on the last line maps the iterable `letters` across the task, running it once for each element (and automatically parallelising it if allowed).

Prefect’s core idea (or one of them, anyway) is that it will find the implicit dependency graph between your tasks; in this case, task_two depends on the output of task_one, which depends on the parameter.
```
word -> task_one -> task_two
```

As you add more complex relationships, Prefect will figure out the graph, and automatically (well, if you ask it to) run in parallel those parts that are happy to happen in parallel. Then you can add improve your tasks with retries (with automatically cached results), persistence and more, lean on the library of common tasks, and improve your Flow with more Parameters, branching logic, and [map/reduce patterns](https://docs.prefect.io/core/concepts/mapping.html), and then build bigger [Flows consisting of smaller Flows](https://docs.prefect.io/core/idioms/flow-to-flow.html#scheduling-a-flow-of-flows)!

And *then* you're ready to orchestrate your flows!

## Scaling out and up
There are several layers to Prefect's orchestration system. At the simplest, you can simply run
```bash
prefect run -p myflow.py --param word=help

# output (will be interspersed by Prefect logs)
# My letter: 'h'
# My letter: 'e'
# My letter: 'l'
# My letter: 'p'
# Flow run succeeded!
```

And you'll already get the benefit of useful logging, retries, paralellism and anything else you've added. But to be really useful, you want to be able to manage this with a web UI somewhere, and send tasks to work in the cloud somewhere.

Prefect's system for this is slightly complicated, and the terminology isn't always clear. This is partly because the cloud is a complex beastie, and partly because of their [Hybrid model](https://www.prefect.io/why-prefect/hybrid-model/), of which more below. But there are basically four layers:
1. Orchestration
2. Agents
3. Flow runs (plus Storage)
4. Task execution

{% include image.html url="/assets/images/2021/prefect.png" description="Does this make it seem simpler? Opinions differ. Any credit to the always-useful Excalidraw." %}

### Orchestration
The first component is orchestration. Up above this was simply running `prefect run` at the command line. Getting more serious, there is [Prefect Cloud](https://cloud.prefect.io) (their managed offering) or [Prefect Server](https://docs.prefect.io/orchestration/server/overview.html) (self-hosted). These provide a web UI, user management and a GraphQL API (changing to REST in the future, thankfully).

You upload a Flow to the Cloud (or Server) by [registering](https://docs.prefect.io/orchestration/getting-started/registering-and-running-a-flow.html#register-a-flow) it.

```bash
prefect register --project my-project -p myflow.py
```

This doesn't actually upload any of your business logic, but simply the metadata and task graph as defined in your `Flow` block. When you run a flow (by whatever means), the Cloud then does... *nothing*. It makes that information available to any Agents (see below) that you have running. This means that Prefect Cloud doesn't need access to any of your cloud infrastructure, as it purely handles the orchestration. (This is their Hybrid model.)

*Ops*: Every time we push code to GitHub, a GitHub Action re-registers all of our flows with Cloud, to ensure things stay up-to-date.

### Agents
The [Agents](https://docs.prefect.io/orchestration/agents/overview.html) are simple daemon-like processes that you point at the cloud. They look for tasks, run them if any are available (using tags to assign to different agents if needed) and update the Cloud when they're done.

Prefect's nomenclature for agents was a bit confusing for me. They have a `LocalAgent`, `DockerAgent`, `ECSAgent` etc. All you need to realise is this: they're named after *where they run flows*, not after where they themselves run. So if you really wanted, you could have an FargateAgent running in Google Cloud and sending Flow runs back to Fargate on AWS.

*Ops*: We're using a `VertexAgent`, running on a custom Docker image with Prefect installed. It itself is running on a [Google Vertex](https://cloud.google.com/vertex-ai) custom job (the nearest thing Google has to Amazon ECS), with an Action to redeploy it whenever the `Dockerfile` or dependencies change. (The Docker image itself is also naturally rebuilt any time these change.)
```Dockerfile
# last line of the Dockerfile
CMD prefect agent vertex start ...
```

### Flow runs
The Prefect docs don't really separate out this layer as I am, but I think it's clearer this way. This is where your Flows are actually run, as defined by the type of Agent you're using and the `run_config` you specify in your `Flow`. In our case, our `VertexAgent` sends Flow runs to Google Vertex. (Support for Google Vertex just landed in Prefect `0.15.8`.)

```python
run_config = VertexRun(
    labels=["vertex"],
    image="docker-image-name",
    machine_type="n1-highmem-2",
)

with Flow("myflow", run_config=run_config) as flow:
    ...
```

This means that each time you run a flow, a new Vertex instance is spun up and dedicated to that Flow run. Vertex is quite slow to provision resources, so there's  a decent chance we'll move to Kubernetes. More below!

This is one more "layer" here: **Storage**. Prefect Cloud doesn't have access to your business logic, so it can't share it with your Agents or Flow run. So you can choose from a long list of places to pull it from, such as your Docker image (not very flexible), or Cloud Storage (not very git-y); the obvious solution for us was GitHub. This means that as soon as code is pushed, the next Flow that you run will have access to it. (The only caveat is of course that any new dependencies must be added to the Docker image!)

```python
storage = GitHub(
    repo="your-org/repo-name",
    path="src/flows/myflow.py",
    access_token_secret="...",
)

with Flow("myflow", run_config=run_config, storage=storage) as flow:
    ...
```

*Ops*: The Docker image is rebuilt by Google Cloud Build Triggers whenever the dependencies change. The Storage is always up-to-date, as it's available to the Flow as soon as its on GitHub. There's a lot of authentication going on at this point, with code moving between Prefect, Google and GitHub, so we use secret stores from each of them to provide them as needed to register flows, build images, load code, spin up compute.

### Task execution
We're at layer four and finally some code can run! Prefect uses different `Executors`, which decide how this happens.

By default, tasks will run in a single thread on the machine running the Flow. Unless your task has no potential for simultaneous tasks, or no mapping, you should run it on a `LocalDaskExecutor`, which uses a local [Dask](https://dask.org/) scheduler to use as much of the machines available resources as possible.
```python
@task
def crunch(array: List[np.ndarray]):
    # compute-intensive task here

executor = LocalDaskExecutor()

with Flow(
    "myflow",
    run_config=run_config,
    storage=storage,
    executor=executor,
) as flow:
    crunch.map(big_list_of_arrays)
    ...
```

Once things get very parallel (very quickly with satellite imagery), the `DaskExecutor` comes into play. We're currently using it with an ephemeral [DaskCloudProvider](https://cloudprovider.dask.org/en/stable/gcp.html) cluster on [Google Compute Engine](https://cloud.google.com/compute) (Google's EC2). This means as your Flow starts, it spins up a Dask scheduler, and then spins up workers as needed (or as defined) to complete your tasks. At the end, everything is torn down again.

```python
executor = DaskExecutor(
    cluster_class=GCPCluster,
    adapt_kwargs={...},
    cluster_kwargs={
        "projectid": "gcp-project-name",
        "source_image": "os-image-from-packer",
        "docker_image": "docker-image",
    },
)

# provide it to the Flow as before
```

You can also simply supply the address of an existing Dask scheduler, and Prefect will use that for your flow runs.

DaskCloudProvider runs on GCE, so it needs full OS images, not just Docker images. To this end, we have another Action to rebuild an OS image with [Packer](https://www.packer.io/) any time the definitions change. (All this image does is pull the Docker image and run it!)

Prefect does a great job of passing state, data and context between these layers, so logging that happens inside your Dask worker on GCE bubbles its way back up to the Cloud interface.

*Ops*: The Packer images are rebuilt whenever necessary, along with the Docker images.

### Bringing it together
And now we have a lovely, robust system. Creating new Flows is as simple as writing a few lines of Python and pushing it. Moments later, you can pick your parameters (using nice forms or JSON, as you prefer) and submit your Flow run to be picked up by an Agent, run on Vertex and paralellised to your heart's desire.

Vertex and GCE are both quite slow to start up, so we'll probably shift our Flow runs and Task execution to Kubernetes (with [GKE](https://cloud.google.com/kubernetes-engine)) at some point, using [KubernetesAgent](https://docs.prefect.io/api/latest/agent/kubernetes.html#kubernetesagent) together with [Dask-Kubernetes](https://kubernetes.dask.org/en/latest/kubecluster.html). For now, while we focus on flexibility, and while most of our Flows are quite long-running, the setup as described works well!

## Appendix
Big shoutout to the [Prefect Slack community](https://www.prefect.io/slack/) for their help!