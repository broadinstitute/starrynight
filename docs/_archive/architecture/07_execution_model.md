# StarryNight Execution Model

## Overview

The execution model in StarryNight defines how modules and pipelines are run in different contexts. This document focuses on the notebook workflow for configuring and executing StarryNight pipelines, examining how modules are instantiated, configured, and executed using backend systems.

## Purpose

The execution model serves several key purposes:

1. **Configuration** - Setting up modules with appropriate parameters
2. **Instantiation** - Creating configured module instances
3. **Backend Selection** - Choosing appropriate execution backends
4. **Execution Control** - Initiating and monitoring pipeline execution
5. **Result Management** - Handling outputs and logs

As shown in the notebook examples, this provides a flexible way to work with StarryNight components.

## Notebook Workflow

The typical notebook workflow includes these key steps:

### 1. Import Components

```python
# Import necessary modules
from starrynight.modules.inventory import GenInvModule
from starrynight.modules.index import GenIndexModule
from starrynight.modules.cp_illum_calc import CPIllumCalcGenLoadDataModule, CPIllumCalcGenCPipeModule
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
import pipecraft as pc
```

### 2. Configure Data Paths

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

### 3. Configure Backend

```python
# Configure Snakemake backend
backend_config = pc.SnakemakeBackendConfig(
    use_opentelemetry=False,  # Disable telemetry for notebook
    print_exec=True           # Print execution details
)

# Create backend instance
exec_backend = pc.SnakemakeBackend(backend_config)
```

### 4. Configure and Run Index/Inventory Modules

```python
# Create and run index module
gen_index_mod = GenIndexModule.from_config(data_config)
exec_backend.run(
    gen_index_mod.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "index"
)

# Create and run inventory module
gen_inv_mod = GenInvModule.from_config(data_config)
exec_backend.run(
    gen_inv_mod.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "inventory"
)
```

### 5. Configure Experiment

```python
# Set up experiment parameters
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
```

### 6. Configure and Run Pipeline Modules

```python
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

## Execution Backends

The execution is handled by backend implementations:

> "We also import the back end, execution back end from the pipecraft library. So here we are using sneak make back end. So we are configuring the snake make back end here..."

Currently, StarryNight primarily uses the Snakemake backend.

### Backend Configuration

The backend is configured with options such as:

1. **Telemetry Settings** - Whether to use OpenTelemetry for logging
2. **Output Settings** - How to display execution information
3. **Resource Settings** - CPU, memory, and other resource limits

### Running Pipelines

The backend's `run` method executes pipelines:

```python
exec_backend.run(
    pipeline=module.pipeline,
    config=backend_config,
    working_dir=working_dir
)
```

This method:
1. Compiles the pipeline to the backend format (e.g., Snakefile)
2. Executes the compiled workflow
3. Monitors execution and collects results

## Execution Artifacts

When a pipeline is executed, several artifacts are generated:

### Compiled Workflow

> "First of all, it generates the snake file, and it you can see, you know, what is generating..."

The compiled workflow (e.g., Snakefile) contains the full definition of the operations to be performed.

### Execution Logs

> "The second is, we also have all the logs here that you can go back and see, you know what happened during the execution, and this will keep all the logs Right, right?"

These logs capture the execution process, errors, and outputs.

### Results

The results of the execution are stored in configured output locations, as defined in the module specifications.

## Compilation Without Execution

You can also compile without executing:

> "Okay, so if I just run this compile step, so exec back end, dot compile, it'll generate a sneak make file."

This allows inspection and manual execution if desired.

## Module State Management

An important aspect of the notebook workflow is module state management:

> "Here in the notebook, as long as you have the kernel running, you have the state of all the modules, right, okay, not just storing any user sessions. I mean, it's up to the user, how your user wants to manage the session right?"

The notebook maintains module state during its execution, allowing for iterative development and inspection.

## Comparing with Direct CLI Usage

The notebook workflow provides several advantages over direct CLI usage:

1. **State Persistence** - Module configurations are maintained in memory
2. **Parameter Inference** - Automatic configuration from experiments
3. **Containerization** - Automatic execution in containers
4. **Workflow Composition** - Easy combination of multiple steps

As noted in the transcript:

> "Contrast that with how I would have done it using a CLI. In the CLI, I would have basically not used many things that you have here, and lost a whole bunch of things but along the way."

## Complete Pipeline Example

Here's an example of running a complete pipeline:

```python
# Import pipeline function
from starrynight.pipelines.pcp_generic import create_pcp_generic_pipeline

# Create pipeline
modules, pipeline = create_pcp_generic_pipeline(data_config, pcp_experiment)

# Run pipeline
exec_backend.run(
    pipeline=pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "complete_pipeline"
)
```

This creates and runs a pipeline composed of multiple modules.

## Execution Environment

The execution environment plays a critical role:

> "So, so we are only defending the container here. It's up to the execution engine how the execution engine wants to run it. For example, Snake make tries to run this as a singularity container or apptainer or something."

The backend determines how containers are executed, providing flexibility across different environments.

## Handling Execution Failures

When execution fails, several troubleshooting approaches are available:

1. Examine logs in the working directory
2. Check container execution details
3. Validate input configurations
4. Inspect the compiled workflow file

## Unit of Work and Parallelism

The execution model also considers parallelism:

> "There's two level parallelism, right? There's parallelism between different steps. So certain steps can be run, you know, independently of each other... But there's also parallelism in in the in single nodes as well, right?"

The backend needs to handle both forms of parallelism.

## Example Notebook

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

## Notebook vs Other Contexts

The execution model differs across contexts:

> "The CLI or the algorithms are, right? For example, if you think about algorithm, right, because it's in Python, you know, you can use the CLI, or you can import the function and run it, right?... With modules. We are trying to..."

The notebook provides a middle ground between direct CLI usage and full UI integration, offering programmatic access with state management.

## Conclusion

The execution model in StarryNight provides a flexible approach to configuring and running pipelines, particularly in notebook contexts. By separating the concerns of configuration, pipeline definition, and execution, it enables powerful workflows while maintaining flexibility across different execution environments.

This model bridges the gap between low-level algorithms and high-level UI integration, providing a powerful programmatic interface for working with complex image processing pipelines.
