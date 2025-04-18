# Starry Night Pipecraft Integration

## Overview

Pipecraft is a library that enables the creation of composable pipeline graphs in Starry Night. It provides primitives for defining computational operations, containers, and their connections, allowing modules to generate executable compute graphs without being tied to specific execution backends.

## Purpose

The Pipecraft integration serves several key purposes in Starry Night:

1. **Compute Graph Definition** - Creating structured representations of computational tasks
2. **Container Configuration** - Specifying container settings for isolated execution
3. **Pipeline Composition** - Combining operations into cohesive workflows
4. **Backend Independence** - Separating pipeline definition from execution
5. **Parallelism Specification** - Defining which operations can run in parallel

As explained in the transcript:

> "Here we are saying, you know, we first constructed the CLI command that we would run inside the container, and then we define, okay, you know, there is and [...] we are constructing the commands, and then we are describing our container to use and giving it the command to invoke and which image to use to run that container."

## Pipecraft's Dual Role

**Critical Point:** Pipecraft serves two essential functions in the Starry Night architecture:

> "Pipe craft is used for two things. One is, you can just create the compute graph with an additional view. It also provides the back end to execute the computer."

This dual capability - both defining compute graphs AND providing execution backends - makes Pipecraft the central technical component that enables the separation between definition and execution, which is fundamental to the entire system.

## Integration Point

In the Starry Night architecture, Pipecraft integration happens inside modules:

> "We were able to, we were able to use bilayers to create the spec. Yeah. We were able to, by default, populate it in some way. Now we have specked it out, but now we need to define, start defining a pipeline. And here's where starting at is now interfacing with pipecraft."

This marks the transition from specification (what needs to be done) to implementation (how to do it).

## Pipeline Construction

Pipecraft uses a Python API for constructing pipelines:

```python
def create_pipeline(self) -> pc.Pipeline:
    """Create the compute graph (Pipecraft pipeline) for this module."""
    # Construct the CLI command
    command = [
        "starrynight", "segcheck", "generate-pipeline",
        "--output-path", str(self.spec.outputs["pipeline"].value),
        "--load-data", str(self.spec.inputs["load_data"].value),
        "--nuclear-channel", str(self.spec.inputs["nuclear_channel"].value),
        "--cell-channel", str(self.spec.inputs["cell_channel"].value)
    ]

    # Create pipeline with container
    pipeline = pc.Pipeline()
    with pipeline.sequential() as seq:
        seq.container(
            name="segcheck_pipeline_gen",
            inputs={
                "load_data": str(self.spec.inputs["load_data"].value),
                "workspace": str(self.spec.inputs["workspace_path"].value)
            },
            outputs={
                "pipeline": str(self.spec.outputs["pipeline"].value)
            },
            container_config=pc.ContainerConfig(
                image="cellprofiler/starrynight:latest",
                command=command
            )
        )

    return pipeline
```

## Core Pipecraft Concepts

### Pipeline

A `Pipeline` is the root object that represents the complete compute graph:

```python
pipeline = pc.Pipeline()
```

### Sequential and Parallel Blocks

Pipecraft provides context managers for defining execution order:

```python
# Sequential execution (operations run one after another)
with pipeline.sequential() as seq:
    # Operations defined here run in sequence

# Parallel execution (operations can run simultaneously)
with pipeline.parallel() as par:
    # Operations defined here can run in parallel
```

These blocks can be nested to create complex execution patterns.

### Container Nodes

Container nodes represent operations that run in containerized environments:

```python
seq.container(
    name="operation_name",
    inputs={
        "input_name": "input_path"
    },
    outputs={
        "output_name": "output_path"
    },
    container_config=pc.ContainerConfig(
        image="container/image:tag",
        command=["command", "arg1", "arg2"]
    )
)
```

### ContainerConfig

ContainerConfig objects specify the container execution environment:

```python
pc.ContainerConfig(
    image="cellprofiler/starrynight:latest",
    command=command,
    environment={
        "ENV_VAR": "value"
    }
)
```

## Simple vs. Complex Pipelines

For single-module operations, pipelines are simple:

> "This might sound redundant, but here we only have one node. So you might be asking, like, why you need a computer off here? But this is because these, this, this compute graph that we generate is composable, right?"

More complex pipelines can connect multiple operations:

```python
with pipeline.sequential() as seq:
    # First operation
    node1 = seq.container(
        name="operation1",
        # config...
    )

    # Second operation
    node2 = seq.container(
        name="operation2",
        # config...
    )

    # Connect nodes
    pipeline.connect(node1.outputs["result"], node2.inputs["source"])
```

## Container Execution

A critical aspect of Pipecraft integration is container specification:

> "We're saying, run this container with this name, with this input and output paths, and with this container config, which says, Use this image and then run with this command line, command line that we constructed before."

This containerization provides isolation and reproducibility.

### Container Runtime Flexibility

The container specification is runtime-agnostic:

> "So, so we are only defending the container here. It's up to the execution engine how the execution engine wants to run it. For example, Snake make tries to run this as a singularity container or apptainer or something."

This abstraction allows the same pipeline to run with different container technologies.

## Pipecraft and CLI Commands

A common pattern in Starry Night is constructing CLI commands to run inside containers:

```python
# Construct CLI command from spec
command = [
    "starrynight", "illum", "calculate",
    "--images-path", str(self.spec.inputs["images_path"].value),
    "--output-path", str(self.spec.outputs["illum_path"].value),
    "--batch-id", self.spec.inputs["batch_id"].value,
    "--plate-id", self.spec.inputs["plate_id"].value
]

# Add any additional parameters
for channel in self.spec.inputs["channels"].value:
    command.extend(["--channel", channel])
```

These commands invoke the Starry Night CLI inside containers, leveraging the algorithm implementations.

## Pipeline Composition

The true power of Pipecraft comes from pipeline composition:

> "When we create a pipeline out of multiple modules, will then compose. But anyway, so here we are creating a computer app. It's with a single node, and we are saying that, you know, run whatever inside this sequential block sequentially."

This composability enables complex workflows from simple modules.

## The "Aha Moment" of Automatic Generation

One of the most important aspects of Pipecraft's role is its ability to generate complex execution plans automatically:

> "If anyone have written snake make files by hand, and if they see that, I can generate this 500 lines long, sneak make file automatically. I guess that's an aha moment at that point. Like, why this computer exists, because you can use this to, like, compile your thing into sneak me back."

This automatic generation of complex execution plans is a key value of the entire architecture.

## Experimental Parallelism API

The transcript also mentions an experimental API for parallelism:

> "So this thing, this is an experimental API. I'm not so you can, like, ignore it for now, but the whole idea here is somehow try to express the parallelism inherent in that step, right?"

This "unit of work" API aims to express finer-grained parallelism within operations.

## Two Levels of Parallelism

Starry Night/Pipecraft supports two levels of parallelism:

1. **Between Steps** - Different pipeline steps running in parallel:
   > "There's parallelism between different steps. So certain steps can be run, you know, independently of each other."

2. **Within Steps** - Parallel execution within a single step:
   > "But there's also parallelism in in the in single nodes as well, right? For example, you can run ILLUM apply parallely, right?"

Both levels can be expressed in the pipeline structure.

## Pipeline Visualization

Though not shown in the transcript, Pipecraft pipelines can typically be visualized to show the compute graph structure, which is valuable for understanding complex workflows.

## Complete Module Pipeline Example

Here's a more complex example showing Pipecraft integration for a module that processes multiple samples in parallel:

```python
def create_pipeline(self) -> pc.Pipeline:
    """Create compute graph with parallel processing."""
    pipeline = pc.Pipeline()

    # Get samples from spec
    samples = self.spec.inputs["samples"].value

    with pipeline.sequential() as seq:
        # First create output directory
        setup = seq.container(
            name="setup_output_dir",
            outputs={
                "output_dir": str(self.spec.outputs["results_dir"].value)
            },
            container_config=pc.ContainerConfig(
                image="alpine:latest",
                command=["mkdir", "-p", str(self.spec.outputs["results_dir"].value)]
            )
        )

        # Then process samples in parallel
        with seq.parallel() as par:
            for sample in samples:
                # For each sample, create a processing container
                par.container(
                    name=f"process_{sample['id']}",
                    inputs={
                        "sample_data": str(sample['path']),
                        "output_dir": str(self.spec.outputs["results_dir"].value)
                    },
                    outputs={
                        "result": str(self.spec.outputs["results_dir"].value / f"{sample['id']}_result.csv")
                    },
                    container_config=pc.ContainerConfig(
                        image="cellprofiler/starrynight:latest",
                        command=[
                            "starrynight", "analysis", "run-pipeline",
                            "--pipeline", str(self.spec.inputs["pipeline"].value),
                            "--input", str(sample['path']),
                            "--output", str(self.spec.outputs["results_dir"].value / f"{sample['id']}_result.csv")
                        ]
                    )
                )

    return pipeline
```

## Compilation to Execution Backends

Pipecraft pipelines are compiled to execution backend formats:

> "It outputs like, you know, like, once this is run, it outputs a configured stainite module, that is the terminology, yeah, a configured star at night module, which includes more than just pipeline."

The actual execution is handled by backends, such as Snakemake.

## Beyond Academic Exercise - A Key Architectural Component

Pipecraft integration is not just an academic exercise but a crucial architectural component:

> "This is not just, you know, some weird attraction or something that we want. Just we built it because we wanted to build it. It's there because it's, it's a very key piece. It's a central piece of like the entire system."

The ability to define compute graphs independently of execution engines is what enables the entire Starry Night architecture to function.

## Conclusion

Pipecraft integration is a critical part of the Starry Night architecture, providing the bridge between specification (Bilayers) and execution (backends). It enables the creation of composable, containerized compute graphs that can express complex workflows with parallelism at multiple levels.

By separating pipeline definition from execution, Pipecraft allows Starry Night to potentially support multiple execution environments while maintaining a consistent pipeline definition approach. This separation is not just a nice feature but the core architectural element that makes the entire system work.
