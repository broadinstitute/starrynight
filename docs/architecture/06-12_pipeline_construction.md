# Starry Night Pipeline Construction and Execution

## Table of Contents
- [Overview](#overview)
- [Purpose](#purpose)
- [Pipecraft Integration](#pipecraft-integration)
  - [Pipecraft's Dual Role](#pipecrafts-dual-role)
  - [Core Pipecraft Concepts](#core-pipecraft-concepts)
  - [Container Nodes and Configuration](#container-nodes-and-configuration)
  - [Simple vs. Complex Pipelines](#simple-vs-complex-pipelines)
- [Pipeline Composition](#pipeline-composition)
  - [Pipeline Composition Function](#pipeline-composition-function)
  - [Module Creation and Configuration](#module-creation-and-configuration)
  - [Building the Pipeline Structure](#building-the-pipeline-structure)
  - [Parallel and Sequential Blocks](#parallel-and-sequential-blocks)
- [Expressing Parallelism](#expressing-parallelism)
  - [Between Steps Parallelism](#between-steps-parallelism)
  - [Within Steps Parallelism](#within-steps-parallelism)
  - [Experimental Parallelism API](#experimental-parallelism-api)
- [Pipeline Execution](#pipeline-execution)
  - [Using the Composed Pipeline](#using-the-composed-pipeline)
  - [Container Execution](#container-execution)
  - [Pipeline Visualization](#pipeline-visualization)
  - [Execution with Telemetry](#execution-with-telemetry)
- [Complete Examples](#complete-examples)
  - [Example: Complete Pipeline Composition](#example-complete-pipeline-composition)
  - [Notebook Example for Pipeline Execution](#notebook-example-for-pipeline-execution)
  - [Modifying Modules After Composition](#modifying-modules-after-composition)
- [The Power of Automatic Generation](#the-power-of-automatic-generation)
- [Conclusion](#conclusion)

## Overview

Pipeline construction in Starry Night combines two critical aspects: Pipecraft integration for defining compute graphs and pipeline composition for building complete workflows. This document explores how individual modules are integrated with Pipecraft to define their compute graphs, and how these modules are then composed into complete executable pipelines. This represents the highest level of abstraction in the Starry Night architecture.

## Purpose

Pipeline construction and composition serve several key purposes in the Starry Night architecture:

1. **Compute Graph Definition** - Creating structured representations of computational tasks
2. **Container Configuration** - Specifying container settings for isolated execution
3. **Pipeline Composition** - Combining operations into cohesive workflows
4. **Backend Independence** - Separating pipeline definition from execution
5. **Parallelism Specification** - Defining which operations can run in parallel
6. **Workflow Definition** - Creating end-to-end processing workflows
7. **Module Coordination** - Connecting modules in the correct sequence
8. **Execution Preparation** - Preparing the complete pipeline for execution

These capabilities enable the creation of complex, reproducible workflows for scientific image processing.

## Pipecraft Integration

Pipecraft is a library that enables the creation of composable pipeline graphs in Starry Night. It provides primitives for defining computational operations, containers, and their connections, allowing modules to generate executable compute graphs without being tied to specific execution backends.

As explained in the architecture discussions:

> "Here we are saying, you know, we first constructed the CLI command that we would run inside the container, and then we define, okay, you know, there is and [...] we are constructing the commands, and then we are describing our container to use and giving it the command to invoke and which image to use to run that container."

### Pipecraft's Dual Role

**Critical Point:** Pipecraft serves two essential functions in the Starry Night architecture:

> "Pipe craft is used for two things. One is, you can just create the compute graph with an additional view. It also provides the back end to execute the computer."

This dual capability - both defining compute graphs AND providing execution backends - makes Pipecraft the central technical component that enables the separation between definition and execution, which is fundamental to the entire system.

In the Starry Night architecture, Pipecraft integration happens inside modules:

> "We were able to, we were able to use bilayers to create the spec. Yeah. We were able to, by default, populate it in some way. Now we have specked it out, but now we need to define, start defining a pipeline. And here's where starting at is now interfacing with pipecraft."

This marks the transition from specification (what needs to be done) to implementation (how to do it).

### Core Pipecraft Concepts

#### Pipeline

A `Pipeline` is the root object that represents the complete compute graph:

```python
pipeline = pc.Pipeline()
```

#### Sequential and Parallel Blocks

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

### Container Nodes and Configuration

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

A critical aspect of Pipecraft integration is container specification:

> "We're saying, run this container with this name, with this input and output paths, and with this container config, which says, Use this image and then run with this command line, command line that we constructed before."

This containerization provides isolation and reproducibility.

The container specification is runtime-agnostic:

> "So, so we are only defending the container here. It's up to the execution engine how the execution engine wants to run it. For example, Snake make tries to run this as a singularity container or apptainer or something."

This abstraction allows the same pipeline to run with different container technologies.

### Simple vs. Complex Pipelines

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

## Pipeline Composition

Pipeline composition is the final layer of abstraction in Starry Night, allowing multiple modules to be combined into complete workflows.

As explained in the transcript:

> "So instead of now running individual modules, what we are doing here is really composing all the models together, right? So you know, we are saying that run all these steps in sequentially, so all the CP steps sequentially, and then all the SBS steps sequentially, but run these two sets in parallel, and then after this, run the analysis steps sequentially, right?"

### Pipeline Composition Function

Pipeline composition is typically implemented as a function that takes configurations and returns a composed pipeline:

```python
def create_pcp_generic_pipeline(
    data_config: DataConfig,
    experiment: PCPGenericExperiment
) -> Tuple[List[StarryNightModule], pc.Pipeline]:
    """
    Create a complete PCP generic pipeline.

    Parameters
    ----------
    data_config : DataConfig
        Data configuration with paths
    experiment : PCPGenericExperiment
        Experiment configuration

    Returns
    -------
    Tuple[List[StarryNightModule], pc.Pipeline]
        List of configured modules and the composed pipeline
    """
    # Implementation...
```

### Module Creation and Configuration

The pipeline composition function first creates and configures all necessary modules:

```python
# Create modules
modules = []

# Index and inventory
index_module = GenIndexModule.from_config(data_config)
modules.append(index_module)

inventory_module = GenInvModule.from_config(data_config)
modules.append(inventory_module)

# Cell Painting modules
cp_illum_calc_load_data = CPIllumCalcGenLoadDataModule.from_config(data_config, experiment)
modules.append(cp_illum_calc_load_data)

cp_illum_calc_pipeline = CPIllumCalcGenCPipeModule.from_config(data_config, experiment)
modules.append(cp_illum_calc_pipeline)

# More module creation...
```

### Building the Pipeline Structure

After creating modules, the function constructs the pipeline structure:

```python
# Create main pipeline
pipeline = pc.Pipeline()

with pipeline.sequential() as main_seq:
    # First run index and inventory
    with main_seq.sequential() as setup_seq:
        setup_seq.add_pipeline(index_module.pipeline)
        setup_seq.add_pipeline(inventory_module.pipeline)

    # Then run CP and SBS in parallel
    with main_seq.parallel() as parallel_proc:
        # CP pipeline branch
        with parallel_proc.sequential() as cp_seq:
            cp_seq.add_pipeline(cp_illum_calc_load_data.pipeline)
            cp_seq.add_pipeline(cp_illum_calc_pipeline.pipeline)
            # Add more CP modules...

        # SBS pipeline branch
        with parallel_proc.sequential() as sbs_seq:
            sbs_seq.add_pipeline(sbs_illum_calc_load_data.pipeline)
            sbs_seq.add_pipeline(sbs_illum_calc_pipeline.pipeline)
            # Add more SBS modules...

    # Finally run analysis
    with main_seq.sequential() as analysis_seq:
        analysis_seq.add_pipeline(analysis_load_data.pipeline)
        analysis_seq.add_pipeline(analysis_pipeline.pipeline)
```

This structure defines both sequencing and parallelism in the pipeline.

The composition function returns both the configured modules and the composed pipeline:

```python
return modules, pipeline
```

This allows users to access both the individual modules (for inspection or modification) and the complete pipeline (for execution).

> "This is your, this is your pipecraft pipeline. Pipecraft pipeline... Now you might be asking, like, why, why you wanted? Because the module itself has a pipe craft pipeline inside it, yeah... this is, this is because you can individually inspect how these individual models are configured. You can then change it and then invoke this function again with the updated, updated spec."

### Parallel and Sequential Blocks

The pipeline composition can express complex execution patterns through nested sequential and parallel blocks:

```python
with pipeline.sequential() as main_seq:
    # First step runs sequentially
    with main_seq.sequential() as first_step:
        # Operations that must run one after another
        first_step.add_pipeline(module1.pipeline)
        first_step.add_pipeline(module2.pipeline)

    # Second step has parallel branches
    with main_seq.parallel() as parallel_branches:
        # Branch A runs sequentially
        with parallel_branches.sequential() as branch_a:
            branch_a.add_pipeline(module3.pipeline)
            branch_a.add_pipeline(module4.pipeline)

        # Branch B runs sequentially
        with parallel_branches.sequential() as branch_b:
            branch_b.add_pipeline(module5.pipeline)
            branch_b.add_pipeline(module6.pipeline)

    # Final step runs after all parallel branches complete
    with main_seq.sequential() as final_step:
        final_step.add_pipeline(module7.pipeline)
```

This structure allows for expressing complex workflows with appropriate dependencies.

## Expressing Parallelism

### Between Steps Parallelism

The pipeline composition can express parallelism between different steps:

> "There's parallelism between different steps. So certain steps can be run, you know, independently of each other. We have eight steps or nine steps, right? Some of them can be run independently. For example, like SBS part can be run independently of the self painting part, right, up until some point."

This is expressed using parallel blocks in the pipeline composition:

```python
with pipeline.parallel() as par:
    # These branches run in parallel
    with par.sequential() as branch_a:
        # Operations in branch A

    with par.sequential() as branch_b:
        # Operations in branch B
```

### Within Steps Parallelism

There's also parallelism within specific steps:

> "But there's also parallelism in in the in single nodes as well, right? For example, you can run ILLUM apply parallely, right? You can use you can, you know you have multiple images. You can apply ILLUM on multiple images simultaneously, right?"

This can be expressed using parallel operations within a module:

```python
def create_pipeline(self) -> pc.Pipeline:
    """Create compute graph with parallel processing."""
    pipeline = pc.Pipeline()

    # Get samples from spec
    samples = self.spec.inputs["samples"].value

    with pipeline.sequential() as seq:
        # First create output directory
        setup = seq.container(/* ... */)

        # Then process samples in parallel
        with seq.parallel() as par:
            for sample in samples:
                # Each sample processed in parallel
                par.container(/* ... */)

    return pipeline
```

### Experimental Parallelism API

The architecture discussions mention an experimental API for finer-grained parallelism:

> "So this thing, this is an experimental API. I'm not so you can, like, ignore it for now, but the whole idea here is somehow try to express the parallelism inherent in that step, right?"

This "unit of work" API aims to express more detailed parallelism within operations.

## Pipeline Execution

### Using the Composed Pipeline

Once a pipeline is composed, it can be executed using a backend:

```python
# Create pipeline
modules, pipeline = create_pcp_generic_pipeline(data_config, pcp_experiment)

# Execute pipeline
exec_backend.run(
    pipeline=pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "complete_pipeline"
)
```

This executes the entire workflow in a single operation.

The Snakemake backend handles the execution of composed pipelines:

> "So in theory, anything like any, anything that can run, sneak, make files across multiple cores, whatever multiple units can now make use of this."

This allows pipelines to run on various infrastructures that support Snakemake.

### Container Execution

All pipeline steps run in containers:

> "We're saying, run this container with this name, with this input and output paths, and with this container config, which says, Use this image and then run with this command line, command line that we constructed before."

This ensures reproducibility and isolation.

### Pipeline Visualization

While not shown explicitly in the architecture discussions, composed pipelines can typically be visualized to show the complete workflow structure. This can be valuable for understanding complex pipelines.

### Execution with Telemetry

For production environments, telemetry can be enabled:

> "For example, because we are running it in notebook, we are not using the open telemetry set up to export logs to a central server... because we are not using the centralized server to collect all the logs."

In production, telemetry would typically be enabled for centralized monitoring.

## Complete Examples

### Example: Complete Pipeline Composition

Here's a detailed example of pipeline composition:

```python
def create_pcp_generic_pipeline(data_config, experiment):
    """Create complete PCP generic pipeline."""
    # Create all modules
    modules = []

    # Setup modules
    index_module = GenIndexModule.from_config(data_config)
    modules.append(index_module)

    inventory_module = GenInvModule.from_config(data_config)
    modules.append(inventory_module)

    # Cell Painting modules
    cp_modules = []

    cp_illum_calc_load_data = CPIllumCalcGenLoadDataModule.from_config(data_config, experiment)
    cp_modules.append(cp_illum_calc_load_data)
    modules.append(cp_illum_calc_load_data)

    cp_illum_calc_pipeline = CPIllumCalcGenCPipeModule.from_config(data_config, experiment)
    cp_modules.append(cp_illum_calc_pipeline)
    modules.append(cp_illum_calc_pipeline)

    cp_illum_calc_run = CPIllumCalcRunModule.from_config(data_config, experiment)
    cp_modules.append(cp_illum_calc_run)
    modules.append(cp_illum_calc_run)

    cp_illum_apply_load_data = CPIllumApplyGenLoadDataModule.from_config(data_config, experiment)
    cp_modules.append(cp_illum_apply_load_data)
    modules.append(cp_illum_apply_load_data)

    cp_illum_apply_pipeline = CPIllumApplyGenCPipeModule.from_config(data_config, experiment)
    cp_modules.append(cp_illum_apply_pipeline)
    modules.append(cp_illum_apply_pipeline)

    cp_illum_apply_run = CPIllumApplyRunModule.from_config(data_config, experiment)
    cp_modules.append(cp_illum_apply_run)
    modules.append(cp_illum_apply_run)

    cp_segcheck_load_data = CPSegcheckGenLoadDataModule.from_config(data_config, experiment)
    cp_modules.append(cp_segcheck_load_data)
    modules.append(cp_segcheck_load_data)

    cp_segcheck_pipeline = CPSegcheckGenCPipeModule.from_config(data_config, experiment)
    cp_modules.append(cp_segcheck_pipeline)
    modules.append(cp_segcheck_pipeline)

    cp_segcheck_run = CPSegcheckRunModule.from_config(data_config, experiment)
    cp_modules.append(cp_segcheck_run)
    modules.append(cp_segcheck_run)

    # SBS modules
    sbs_modules = []

    sbs_illum_calc_load_data = SBSIllumCalcGenLoadDataModule.from_config(data_config, experiment)
    sbs_modules.append(sbs_illum_calc_load_data)
    modules.append(sbs_illum_calc_load_data)

    # Additional SBS modules...

    # Analysis modules
    analysis_modules = []

    analysis_load_data = AnalysisGenLoadDataModule.from_config(data_config, experiment)
    analysis_modules.append(analysis_load_data)
    modules.append(analysis_load_data)

    analysis_pipeline = AnalysisGenCPipeModule.from_config(data_config, experiment)
    analysis_modules.append(analysis_pipeline)
    modules.append(analysis_pipeline)

    analysis_run = AnalysisRunModule.from_config(data_config, experiment)
    analysis_modules.append(analysis_run)
    modules.append(analysis_run)

    # Create main pipeline
    pipeline = pc.Pipeline()

    with pipeline.sequential() as main_seq:
        # First run index and inventory
        with main_seq.sequential() as setup_seq:
            setup_seq.add_pipeline(index_module.pipeline)
            setup_seq.add_pipeline(inventory_module.pipeline)

        # Then run CP and SBS in parallel
        with main_seq.parallel() as parallel_proc:
            # CP pipeline branch
            with parallel_proc.sequential() as cp_seq:
                for module in cp_modules:
                    cp_seq.add_pipeline(module.pipeline)

            # SBS pipeline branch
            with parallel_proc.sequential() as sbs_seq:
                for module in sbs_modules:
                    sbs_seq.add_pipeline(module.pipeline)

        # Finally run analysis
        with main_seq.sequential() as analysis_seq:
            for module in analysis_modules:
                analysis_seq.add_pipeline(module.pipeline)

    # Return modules and pipeline
    return modules, pipeline
```

### Notebook Example for Pipeline Execution

Here's a complete notebook example for creating and executing a pipeline:

```python
# Import necessary components
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
from starrynight.pipelines.pcp_generic import create_pcp_generic_pipeline
import pipecraft as pc
from pathlib import Path

# Set up paths
workspace_path = Path("/path/to/workspace")
images_path = Path("/path/to/images")
scratch_path = Path("/path/to/scratch")

# Create data config
data_config = DataConfig(
    workspace_path=workspace_path,
    images_path=images_path,
    scratch_path=scratch_path
)

# Configure experiment
pcp_init_config = {
    "nuclear_channel": "DAPI",
    "cell_channel": "CellMask",
    "mito_channel": "MitoTracker",
    "barcode_csv_path": str(workspace_path / "barcodes.csv"),
    "image_overlap_percentage": 10
}

# Create experiment
pcp_experiment = PCPGenericExperiment.from_index(
    index_path=data_config.workspace_path / "index.yaml",
    init_config=pcp_init_config
)

# Configure backend
backend_config = pc.SnakemakeBackendConfig(
    use_opentelemetry=False,
    print_exec=True
)
exec_backend = pc.SnakemakeBackend(backend_config)

# Create pipeline
print("Creating pipeline...")
modules, pipeline = create_pcp_generic_pipeline(data_config, pcp_experiment)

# Run the pipeline
print("Running pipeline...")
exec_backend.run(
    pipeline=pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "complete_pipeline"
)

print("Pipeline complete!")
```

### Modifying Modules After Composition

Even after composition, individual modules can be modified:

```python
# Create pipeline
modules, pipeline = create_pcp_generic_pipeline(data_config, pcp_experiment)

# Find specific module to modify
segcheck_module = next(m for m in modules if m.module_id == "cp_segcheck_gen_cppipe")

# Modify parameter
segcheck_module.spec.inputs["nuclear_channel"].value = "Modified_DAPI"

# Recreate pipeline with modified modules
_, updated_pipeline = create_pcp_generic_pipeline(data_config, pcp_experiment, modules=modules)

# Execute modified pipeline
exec_backend.run(
    pipeline=updated_pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "modified_pipeline"
)
```

Composed pipelines offer several advantages over individual module execution:

1. **Dependency Management** - Automatic handling of module dependencies
2. **Parallelism** - Automatic parallel execution where possible
3. **Single Command** - Execute the entire workflow with one command
4. **Resource Optimization** - Better resource utilization across steps
5. **Unified Logging** - Consolidated logging and monitoring

## The Power of Automatic Generation

One of the most important aspects of the pipeline construction is its ability to generate complex execution plans automatically:

> "If anyone have written snake make files by hand, and if they see that, I can generate this 500 lines long, sneak make file automatically. I guess that's an aha moment at that point. Like, why this computer exists, because you can use this to, like, compile your thing into sneak me back."

This automatic generation of complex execution plans is a key value of the entire architecture:

> "This is not just, you know, some weird attraction or something that we want. Just we built it because we wanted to build it. It's there because it's, it's a very key piece. It's a central piece of like the entire system."

Using a composed pipeline offers significant advantages over CLI usage:

> "If I knocked out Canvas and conductor entirely deleted those files, I would still be able to do a lot with your current functionality in terms of being able to run high throughput screen level experiments through your pipeline, because I will, I mean, I can still do that just using cell profiler, but what I can now do on CLI is that using a using a notebook and using a JSON file where I can configure my experiment, right? I can read that experiment from this JSON file in my notebook. I can configure every module that I need to run, and then I can run them, and I can get my jobs."

The pipeline approach provides automation, structure, and reproducibility beyond what's possible with direct CLI usage.

## Conclusion

Pipeline construction and composition represent the highest level of abstraction in the Starry Night architecture. By leveraging Pipecraft for compute graph definition and providing a structured approach to composing complete workflows, Starry Night enables complex image processing pipelines to be defined, configured, and executed with clarity and flexibility.

The key architectural achievement is the separation between pipeline definition and execution, allowing the same pipeline to run on different backends while maintaining a consistent definition approach. This separation, combined with the powerful composition capabilities, enables the automatic generation of complex execution plans from high-level abstractions.

The pipeline construction capabilities bridge the gap between individual module execution and complete workflow automation, providing a powerful yet comprehensible system for scientific image processing.

**Next: [Execution System](07-08_execution_system.md)**
