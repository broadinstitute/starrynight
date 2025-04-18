# Starry Night Execution System

## Overview

The execution system in Starry Night defines how modules and pipelines are executed in computing environments. This system consists of two key components: the execution model, which handles how modules and pipelines are configured and executed in different contexts, and the Snakemake backend, which translates Pipecraft pipelines into concrete, reproducible workflows. Together, these components form the final layer in Starry Night's architecture, turning abstract pipeline definitions into actual running processes.

## Purpose

The execution system serves several critical purposes in the Starry Night architecture:

1. **Configuration** - Setting up modules with appropriate parameters
2. **Instantiation** - Creating configured module instances
3. **Backend Selection** - Choosing appropriate execution backends
4. **Execution Control** - Initiating and monitoring pipeline execution
5. **Result Management** - Handling outputs and logs
6. **Workflow Translation** - Converting Pipecraft pipelines to executable format
7. **Dependency Management** - Handling dependencies between pipeline steps
8. **Container Execution** - Managing execution of containerized operations
9. **Parallel Processing** - Controlling parallel execution of independent steps

This system provides the connection between abstract pipeline definitions and concrete execution in computing environments.

## Execution Model

The execution model in Starry Night defines how modules and pipelines are run in different contexts, with a particular focus on the notebook workflow.

### Notebook Workflow

The typical notebook workflow includes these key steps:

#### 1. Import Components

```python
# Import necessary modules
from starrynight.modules.inventory import GenInvModule
from starrynight.modules.index import GenIndexModule
from starrynight.modules.cp_illum_calc import CPIllumCalcGenLoadDataModule, CPIllumCalcGenCPipeModule
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
import pipecraft as pc
```

#### 2. Configure Data Paths

```python
# Set up data paths
workspace_path = "/path/to/workspace"
images_path = "/path/to/images"
scratch_path = "/path/to/scratch"

# Create data config
data_config = DataConfig(
    workspace_path=workspace_path,
    images_path=images_path,
    scratch_path=scratch_path
)
```

#### 3. Configure Backend

```python
# Configure Snakemake backend
backend_config = pc.SnakemakeBackendConfig(
    use_opentelemetry=False,  # Disable telemetry for notebook
    print_exec=True           # Print execution details
)

# Create backend instance
exec_backend = pc.SnakemakeBackend(backend_config)
```

### Module Configuration and Execution

The execution model handles how modules are configured and run:

```python
# Create and run index module
gen_index_mod = GenIndexModule.from_config(data_config)
exec_backend.run(
    gen_index_mod.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "index"
)

# Configure experiment
pcp_init_config = {
    "nuclear_channel": "DAPI",
    "cell_channel": "CellMask",
    "mito_channel": "MitoTracker",
    "barcode_csv_path": "/path/to/barcodes.csv",
    "image_overlap_percentage": 10
}

# Create configured experiment
pcp_experiment = PCPGenericExperiment.from_index(
    index_path=data_config.workspace_path / "index.yaml",
    init_config=pcp_init_config
)

# Create and run pipeline module
illum_load_data_mod = CPIllumCalcGenLoadDataModule.from_config(
    data_config=data_config,
    experiment=pcp_experiment
)

exec_backend.run(
    illum_load_data_mod.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "illum_load_data"
)
```

### Backend Selection

The execution is handled by backend implementations:

> "We also import the back end, execution back end from the pipecraft library. So here we are using sneak make back end. So we are configuring the snake make back end here..."

Currently, Starry Night primarily uses the Snakemake backend. The backend is configured with options such as:

1. **Telemetry Settings** - Whether to use OpenTelemetry for logging
2. **Output Settings** - How to display execution information
3. **Resource Settings** - CPU, memory, and other resource limits

### Execution Artifacts

When a pipeline is executed, several artifacts are generated:

#### Compiled Workflow

> "First of all, it generates the snake file, and it you can see, you know, what is generating..."

The compiled workflow (e.g., Snakefile) contains the full definition of the operations to be performed.

#### Execution Logs

> "The second is, we also have all the logs here that you can go back and see, you know what happened during the execution, and this will keep all the logs Right, right?"

These logs capture the execution process, errors, and outputs.

#### Results

The results of the execution are stored in configured output locations, as defined in the module specifications.

### Module State Management

An important aspect of the notebook workflow is module state management:

> "Here in the notebook, as long as you have the kernel running, you have the state of all the modules, right, okay, not just storing any user sessions. I mean, it's up to the user, how your user wants to manage the session right?"

The notebook maintains module state during its execution, allowing for iterative development and inspection.

## Snakemake Backend

The Snakemake backend is Starry Night's primary execution engine, responsible for translating Pipecraft pipelines into Snakemake workflows and executing them.

[Snakemake](https://snakemake.readthedocs.io/) is a workflow management system that:

- Uses a Python-based language to define rules
- Manages dependencies between rules using input/output relationships
- Supports parallel execution of independent tasks
- Provides container integration (Docker, Singularity/Apptainer)
- Handles resource management and scheduling

### The "Aha Moment" of Automatic Generation

**Critical Point:** The Snakemake backend delivers one of the most impressive capabilities of the Starry Night system - the automatic generation of complex workflow files:

> "If anyone have written snake make files by hand, and if they see that, I can generate this 500 lines long, sneak make file automatically. I guess that's an aha moment at that point. Like, why this computer exists, because you can use this to, like, compile your thing into sneak me back."

This automatic generation of complex Snakefiles from high-level abstractions is a central architectural achievement that demonstrates the value of the entire system.

### Generated Snakefile Structure

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

As shown in the architecture discussions:

> "I guess, if you are just running a single module, you will basically see one of, you know, rule all that's gonna depend on one of the rules that you have to invoke. This is all, again, very specific to how snake make works, but it says, like, what inputs it expects, what outputs it's gonna create, what container it's gonna use, and then what's the actual commands gonna invoke inside that container."

### Rule Structure

Each rule in the Snakefile represents a computational step and includes:

1. **Rule Name** - Identifier for the operation
2. **Inputs** - Files or directories required for the operation
3. **Outputs** - Files or directories produced by the operation
4. **Container** - Container image to use for execution
5. **Shell Command** - Command to execute inside the container

### Complex Workflow Example

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

The execution system handles container execution through the backend:

> "So, so we are only defending the container here. It's up to the execution engine how the execution engine wants to run it. For example, Snake make tries to run this as a singularity container or apptainer or something. They have their own thing. You can force it to run or use Docker, maybe."

This abstraction allows the same pipeline to run with different container technologies based on the environment.

All pipeline steps run in containers:

> "We're saying, run this container with this name, with this input and output paths, and with this container config, which says, Use this image and then run with this command line, command line that we constructed before."

This ensures reproducibility and isolation.

The container specification includes:
- The container image to use
- The command to run inside the container
- Input and output paths
- Environment variables if needed

## Parallelism in Execution

The execution system handles two levels of parallelism:

> "There's two level parallelism, right? There's parallelism between different steps. So certain steps can be run, you know, independently of each other... But there's also parallelism in in the in single nodes as well, right?"

### Rule-level Parallelism

Snakemake automatically handles rule-level parallelism based on the dependency graph:

- Independent rules can run in parallel
- Rules that depend on the outputs of other rules wait for those rules to complete
- The order of execution is determined by the input/output dependencies, not by the order in the file

### Task-level Parallelism

For rules that process multiple similar items:

- Multiple instances of the same rule can run in parallel
- Each instance processes a different input/output combination
- This is particularly useful for operations like applying illumination correction to multiple images

The level of parallelism can be controlled with Snakemake parameters:

```bash
snakemake --cores 4  # Run with 4 CPU cores
```

## Advanced Features

### Compiling Without Executing

You can compile a pipeline without executing it:

```python
exec_backend.compile(
    pipeline=module.pipeline,
    config=backend_config,
    working_dir=working_dir
)
```

This generates the Snakefile without running it, allowing for inspection and manual execution.

> "Okay, so if I just run this compile step, so exec back end, dot compile, it'll generate a sneak make file."

This allows inspection and manual execution if desired.

Once a Snakefile is generated, it can be run directly:

> "Got it, and this is something I can actually just run using sneak, Nick, yeah, directly on my command line, and it will run the command inside the container that is specified in the snake make file."

This provides flexibility for users who want to work directly with Snakemake.

### Logs and Monitoring

The Snakemake backend captures detailed logs:

> "We also have all the logs here that you can go back and see, you know what happened during the execution, and this will keep all the logs Right, right? And again, it's aware, so you can configure it the way you want. But if you're running it locally, you still have all the things right."

These logs are essential for troubleshooting and monitoring.

When execution fails, several troubleshooting approaches are available:

1. Examine logs in the working directory
2. Check container execution details
3. Validate input configurations
4. Inspect the compiled workflow file

### Execution with Telemetry

For production environments, telemetry can be enabled:

> "For example, because we are running it in notebook, we are not using the open telemetry set up to export logs to a central server... because we are not using the centralized server to collect all the logs."

In production, telemetry would typically be enabled for centralized monitoring.

## Complete Examples

### Example Notebook

Here's a complete notebook example integrating these concepts:

```python
# Import necessary components
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
from starrynight.modules.inventory import GenInvModule
from starrynight.modules.index import GenIndexModule
from starrynight.pipelines.pcp_generic import create_pcp_generic_pipeline
import pipecraft as pc
import os
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

# Configure backend
backend_config = pc.SnakemakeBackendConfig(
    use_opentelemetry=False,
    print_exec=True
)
exec_backend = pc.SnakemakeBackend(backend_config)

# Run indexing and inventory
print("Running indexing...")
gen_index_mod = GenIndexModule.from_config(data_config)
exec_backend.run(
    gen_index_mod.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "index"
)

print("Running inventory...")
gen_inv_mod = GenInvModule.from_config(data_config)
exec_backend.run(
    gen_inv_mod.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "inventory"
)

# Configure experiment
pcp_init_config = {
    "nuclear_channel": "DAPI",
    "cell_channel": "CellMask",
    "mito_channel": "MitoTracker",
    "barcode_csv_path": str(workspace_path / "barcodes.csv"),
    "image_overlap_percentage": 10
}

pcp_experiment = PCPGenericExperiment.from_index(
    index_path=data_config.workspace_path / "index.yaml",
    init_config=pcp_init_config
)

# Create complete pipeline
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

### Example: Generated Snakefile

Here's an excerpt from an actual generated Snakefile:

```python
# This file was generated by Starry Night

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

## Future Backends

The Snakemake backend demonstrates the power of the architecture:

> "Now, now this is the point where you can say that, okay, now if you buy into this idea, or, like, if you're comfortable with this idea, where, first of all, we have demonstrated proof that, you know, we can now take this computer graph and then convert it to snake wave file that we can run. So it's not a far festival idea from here on, that we can take this computer off and then write a back end that can execute it on AWS with whatever needs you want."

This shows how the architecture can be extended to support different execution environments in the future, such as:

1. Cloud-based execution (AWS, GCP, Azure)
2. HPC cluster execution
3. Kubernetes-based execution
4. Custom execution environments

## Comparison with Other Approaches

The notebook workflow provides several advantages over direct CLI usage:

1. **State Persistence** - Module configurations are maintained in memory
2. **Parameter Inference** - Automatic configuration from experiments
3. **Containerization** - Automatic execution in containers
4. **Workflow Composition** - Easy combination of multiple steps

As noted in the architecture discussions:

> "Contrast that with how I would have done it using a CLI. In the CLI, I would have basically not used many things that you have here, and lost a whole bunch of things but along the way."

The execution through Snakemake also offers benefits compared to direct execution:

1. **Reproducibility** - Ensures consistent execution across environments
2. **Scalability** - Scales from laptops to HPC clusters
3. **Restart Capability** - Can resume from failures without redoing completed work
4. **Resource Management** - Can specify CPU, memory, and other resource requirements
5. **Integration** - Works well with containers and existing tools

## Conclusion

The execution system in Starry Night provides a powerful approach to running pipelines in a reproducible, containerized manner. By combining a flexible execution model with the Snakemake backend, it enables complex workflows to be executed consistently across different environments.

The automatic generation of detailed, executable Snakefiles from high-level abstractions is one of the most impressive achievements of the Starry Night architecture. As emphasized in the architecture discussions:

> "If anyone have written snake make files by hand, and if they see that, I can generate this 500 lines long, sneak make file automatically. I guess that's an aha moment at that point."

This capability demonstrates the power of the separation between definition and execution in the system design, allowing complex workflows to be defined at a high level and automatically translated into executable form.

The execution system bridges the gap between abstract pipeline definitions and concrete execution, providing the final layer in Starry Night's architecture that turns conceptual workflows into running processes.

**Next: [Experiment Configuration](09-11_experiment_configuration.md)**
