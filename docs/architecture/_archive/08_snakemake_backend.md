# StarryNight Snakemake Backend

## Overview

The Snakemake backend is StarryNight's primary execution engine, responsible for translating Pipecraft pipelines into Snakemake workflows and executing them. This document explores how the Snakemake backend works, the structure of generated Snakefiles, and how they enable reproducible, containerized execution of image processing pipelines.

## Purpose

The Snakemake backend serves several key purposes:

1. **Workflow Translation** - Converts Pipecraft pipelines to Snakemake format
2. **Dependency Management** - Handles dependencies between pipeline steps
3. **Container Execution** - Manages execution of containerized operations
4. **Parallel Processing** - Controls parallel execution of independent steps
5. **Logging and Monitoring** - Captures execution details and results

This backend provides a bridge between the abstract pipelines defined by modules and concrete execution in computing environments.

## The "Aha Moment" of Automatic Generation

**Critical Point:** The Snakemake backend delivers one of the most impressive capabilities of the StarryNight system - the automatic generation of complex workflow files:

> "If anyone have written snake make files by hand, and if they see that, I can generate this 500 lines long, sneak make file automatically. I guess that's an aha moment at that point. Like, why this computer exists, because you can use this to, like, compile your thing into sneak me back."

This automatic generation of complex Snakefiles from high-level abstractions is a central architectural achievement that demonstrates the value of the entire system.

## Snakemake Introduction

[Snakemake](https://snakemake.readthedocs.io/) is a workflow management system that:

- Uses a Python-based language to define rules
- Manages dependencies between rules using input/output relationships
- Supports parallel execution of independent tasks
- Provides container integration (Docker, Singularity/Apptainer)
- Handles resource management and scheduling

## Generated Snakefile Structure

When a Pipecraft pipeline is compiled to a Snakefile, it generates a structure like this:

```python
# Generated Snakefile

rule all:
    input:
        "path/to/final/output.csv"

rule operation_name:
    input:
        input_name="path/to/input/file.csv",
        workspace="path/to/workspace"
    output:
        pipeline="path/to/output/pipeline.cppipe"
    container:
        "cellprofiler/starrynight:latest"
    shell:
        "starrynight segcheck generate-pipeline --output-path {output.pipeline} --load-data {input.input_name} --nuclear-channel DAPI --cell-channel CellMask"
```

As shown in the transcript:

> "I guess, if you are just running a single module, you will basically see one of, you know, rule all that's gonna depend on one of the rules that you have to invoke. This is all, again, very specific to how snake make works, but it says, like, what inputs it expects, what outputs it's gonna create, what container it's gonna use, and then what's the actual commands gonna invoke inside that container."

## Rule Structure

Each rule in the Snakefile represents a computational step and includes:

1. **Rule Name** - Identifier for the operation
2. **Inputs** - Files or directories required for the operation
3. **Outputs** - Files or directories produced by the operation
4. **Container** - Container image to use for execution
5. **Shell Command** - Command to execute inside the container

## Complex Workflow Example

For a multi-step pipeline, the Snakefile would contain multiple interconnected rules:

```python
rule all:
    input:
        "results/analysis_complete.txt"

rule generate_load_data:
    input:
        images="path/to/images"
    output:
        load_data="workspace/load_data/illum_calc_load_data.csv"
    container:
        "cellprofiler/starrynight:latest"
    shell:
        "starrynight illum generate-load-data --images-path {input.images} --output-path {output.load_data} --batch-id Batch1 --plate-id Plate1"

rule generate_pipeline:
    input:
        load_data="workspace/load_data/illum_calc_load_data.csv"
    output:
        pipeline="workspace/pipelines/illum_calc_pipeline.cppipe"
    container:
        "cellprofiler/starrynight:latest"
    shell:
        "starrynight illum generate-pipeline --output-path {output.pipeline} --load-data {input.load_data}"

rule run_pipeline:
    input:
        load_data="workspace/load_data/illum_calc_load_data.csv",
        pipeline="workspace/pipelines/illum_calc_pipeline.cppipe"
    output:
        results="workspace/results",
        complete="results/analysis_complete.txt"
    container:
        "cellprofiler/starrynight:latest"
    shell:
        """
        starrynight illum run-pipeline --load-data {input.load_data} --pipeline {input.pipeline} --output-dir {output.results}
        touch {output.complete}
        """
```

Snakemake automatically determines the execution order based on the input/output dependencies.

## Container Execution

The Snakemake backend handles container execution:

> "So, so we are only defending the container here. It's up to the execution engine how the execution engine wants to run it. For example, Snake make tries to run this as a singularity container or apptainer or something. They have their own thing. You can force it to run or use Docker, maybe."

This abstraction allows the same pipeline to run with different container technologies based on the environment.

## Benefit of Generated Snakefiles

The generation of Snakefiles provides several benefits:

1. **Inspection** - The generated workflow can be examined before execution
2. **Modification** - The Snakefile can be manually modified if needed
3. **Direct Execution** - The Snakefile can be executed directly with Snakemake
4. **Portability** - The Snakefile can be shared and run in different environments

As noted in the transcript:

> "So this will, like, give you full visibility what's actually being run. So that's the first thing, and then you can also, like, iterate on it, right? So this is also, like one of the handoff points, for example, if people want a next flow script that they want to run on their own infrastructure, and they don't care about cyanide at all, so they can still use cyanide to generate this and then run it however they want."

## Location of Generated Files

The Snakemake backend generates files in the specified working directory:

```python
exec_backend.run(
    pipeline=module.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "operation_name"
)
```

This creates a directory structure:

```
runs/
└── operation_name/
    ├── Snakefile                # The generated workflow
    ├── .snakemake/              # Snakemake's internal files
    ├── logs/                    # Execution logs
    └── [output files]           # Results of the execution
```

## Logs and Monitoring

The Snakemake backend captures detailed logs:

> "We also have all the logs here that you can go back and see, you know what happened during the execution, and this will keep all the logs Right, right? And again, it's aware, so you can configure it the way you want. But if you're running it locally, you still have all the things right."

These logs are essential for troubleshooting and monitoring.

## Compiling Without Executing

You can compile a pipeline without executing it:

```python
exec_backend.compile(
    pipeline=module.pipeline,
    config=backend_config,
    working_dir=working_dir
)
```

This generates the Snakefile without running it, allowing for inspection and manual execution.

## Direct Execution of Snakefiles

Once a Snakefile is generated, it can be run directly:

> "Got it, and this is something I can actually just run using sneak, Nick, yeah, directly on my command line, and it will run the command inside the container that is specified in the snake make file."

This provides flexibility for users who want to work directly with Snakemake.

## Parallelism in Snakemake

Snakemake automatically handles parallelism based on the dependency graph:

1. **Rule-level Parallelism** - Independent rules run in parallel
2. **Task-level Parallelism** - Multiple instances of the same rule can run in parallel

The level of parallelism can be controlled with Snakemake parameters:

```bash
snakemake --cores 4  # Run with 4 CPU cores
```

## Example: Full Pipeline Compilation

Here's how the Snakemake backend compiles a full pipeline with multiple modules:

```python
# Create pipeline
modules, pipeline = create_pcp_generic_pipeline(data_config, pcp_experiment)

# Compile to Snakefile
exec_backend.compile(
    pipeline=pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "complete_pipeline"
)
```

This generates a complex Snakefile with rules for each operation in the pipeline, including proper dependencies based on the pipeline structure.

## Snakemake's Role in the Architecture

Snakemake serves as the execution layer in the StarryNight architecture:

1. **Algorithms** define the core functionality
2. **Modules** provide abstraction and standardization
3. **Pipecraft** creates compute graphs
4. **Snakemake** executes the graphs in a reproducible way

This separation of concerns is a key architectural strength.

## Proof of Concept to Future Backends

The Snakemake backend demonstrates the power of the architecture:

> "Now, now this is the point where you can say that, okay, now if you buy into this idea, or, like, if you're comfortable with this idea, where, first of all, we have demonstrated proof that, you know, we can now take this computer graph and then convert it to snake wave file that we can run. So it's not a far festival idea from here on, that we can take this computer off and then write a back end that can execute it on AWS with whatever needs you want."

This shows how the architecture can be extended to support different execution environments in the future.

## Example: Generated Snakefile

Here's an excerpt from an actual generated Snakefile:

```python
# This file was generated by StarryNight

from snakemake.io import directory

rule all:
    input:
        "workspace/results/analysis_complete.txt"

rule cp_illum_calc_load_data:
    input:
        images="path/to/images/Batch1/Plate1"
    output:
        load_data="workspace/load_data/illum_calc_load_data.csv"
    container:
        "cellprofiler/starrynight:latest"
    shell:
        "starrynight illum generate-load-data --images-path {input.images} --output-path {output.load_data} --batch-id Batch1 --plate-id Plate1 --channel DAPI --channel CellMask --channel MitoTracker"

rule cp_illum_calc_pipeline:
    input:
        load_data="workspace/load_data/illum_calc_load_data.csv"
    output:
        pipeline="workspace/pipelines/illum_calc_pipeline.cppipe"
    container:
        "cellprofiler/starrynight:latest"
    shell:
        "starrynight illum generate-pipeline --output-path {output.pipeline} --load-data {input.load_data}"

# Additional rules...
```

## Benefits of Snakemake for Scientific Workflows

Snakemake is particularly well-suited for scientific image processing workflows:

1. **Reproducibility** - Ensures consistent execution across environments
2. **Scalability** - Scales from laptops to HPC clusters
3. **Restart Capability** - Can resume from failures without redoing completed work
4. **Resource Management** - Can specify CPU, memory, and other resource requirements
5. **Integration** - Works well with containers and existing tools

## Running with Different Backends

While Snakemake is the primary backend, the architecture allows for others:

> "For example, because we are running it in notebook, we are not using the open telemetry set up to export logs to a central server. And then we also saying, print all the execution that's happening in the just print it so that we can see in the inner logs, because we are not using the centralized server to collect all the logs."

This flexibility allows adaptation to different execution environments.

## Limitations and Considerations

Some limitations to be aware of:

1. **Complex Dependencies** - Very complex dependency patterns may be challenging to express
2. **Resource Specification** - Fine-grained resource control requires additional configuration
3. **Error Handling** - Error reporting depends on the quality of container logging
4. **Performance Overhead** - Container startup can add overhead for many small tasks

## Conclusion

The Snakemake backend provides a powerful, flexible execution engine for StarryNight pipelines. By translating abstract Pipecraft pipelines into concrete Snakemake workflows, it enables reproducible, containerized execution of complex image processing operations.

The automatic generation of detailed, executable Snakefiles from high-level abstractions is one of the most impressive achievements of the StarryNight architecture, demonstrating the power and flexibility of the separation between definition and execution in the system design.
