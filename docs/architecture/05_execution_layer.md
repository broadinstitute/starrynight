# StarryNight Execution Layer

## Overview

The execution layer in StarryNight defines how modules and pipelines are executed in computing environments. This layer consists of two key components: the execution model, which handles how modules and pipelines are configured and executed in different contexts, and the Snakemake backend, which translates Pipecraft pipelines into concrete, reproducible workflows. Together, these components form the final layer in StarryNight's architecture, turning abstract pipeline definitions into actual running processes.

## Purpose

The execution layer serves several critical purposes in the StarryNight architecture:

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

The execution model in the StarryNight execution layer defines how modules and pipelines are run in different contexts, with a particular focus on the notebook workflow.

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

The execution system uses backend implementations in Pipecraft. Currently, StarryNight primarily uses the Snakemake backend, configured with options such as:

1. **Telemetry Settings** - Whether to use OpenTelemetry for logging
2. **Output Settings** - How to display execution information
3. **Resource Settings** - CPU, memory, and other resource limits

### Execution Artifacts

When a pipeline is executed, several artifacts are generated:

#### Compiled Workflow

The compiled workflow (e.g., Snakefile) contains the full definition of the operations to be performed. This file includes rules for each operation, input/output specifications, container configuration, and command-line instructions.

#### Execution Logs

The execution logs capture the entire execution process, including command outputs, errors, and runtime information. These logs provide a complete record of execution for troubleshooting and auditing.

#### Results

The results of the execution are stored in configured output locations, as defined in the module specifications.

### Module State Management

An important aspect of the notebook workflow is module state management. The notebook environment maintains module state during its execution, allowing for iterative development and inspection. This enables users to inspect module configurations, modify parameters, and re-run operations without restarting the entire workflow.

## Snakemake Backend

The Snakemake backend is StarryNight's primary execution engine, responsible for translating Pipecraft pipelines into Snakemake workflows and executing them.

[Snakemake](https://snakemake.readthedocs.io/) is a workflow management system that:

- Uses a Python-based language to define rules
- Manages dependencies between rules using input/output relationships
- Supports parallel execution of independent tasks
- Provides container integration (Docker, Singularity/Apptainer)
- Handles resource management and scheduling

### Backend Implementation in Pipecraft

The Snakemake backend is implemented in the Pipecraft package rather than in the StarryNight core package. This architectural decision:

- Keeps backend implementation details separate from the scientific image processing logic
- Allows for multiple backends to be developed without modifying the core package
- Maintains a clean separation between pipeline definition and execution

When StarryNight modules and pipelines are executed, they use the backend implementations from Pipecraft through a well-defined API.

### The "Aha Moment" of Automatic Generation

**Critical Point:** The Snakemake backend delivers one of the most impressive capabilities of the StarryNight system - the automatic generation of complex workflow files. This automatic generation of complex Snakefiles from high-level abstractions is a central architectural achievement that demonstrates the value of the entire system.

For developers who have written Snakemake files manually, seeing a complex 500-line Snakefile generated automatically from high-level module definitions provides an immediate understanding of the system's value. It exemplifies how the StarryNight architecture transforms simple, user-friendly abstractions into complex, reproducible workflows.

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

The compiled Snakefile defines what inputs each rule expects, what outputs it will create, which container to use, and the actual command to invoke inside that container.

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

## Container Execution Model

StarryNight uses containerization for reproducible algorithm execution. This is implemented through a structured approach in the PipeCraft package.

### Container Definition

The `Container` class in `pipecraft/node.py` defines execution environments with:
- `image`: Docker/Singularity image reference
- `cmd`: Command to run within the container
- `env`: Environment variables

Modules use this pattern to define containerized operations:

```python
# From starrynight/modules/cp_illum_calc/calc_cp.py
Container(
    name="cp_calc_illum_invoke_cp",
    input_paths={
        "cppipe_path": [...],
        "load_data_path": [...],
    },
    output_paths={
        "cp_illum_calc_dir": [...]
    },
    config=ContainerConfig(
        image="ghrc.io/leoank/starrynight:dev",
        cmd=["starrynight", "cp", "-p", spec.inputs[0].path, ...],
        env={},
    ),
)
```

### Backend Integration

The `SnakeMakeBackend` in `pipecraft/backend/snakemake.py` translates container specifications to Snakemake rules:
- Container images become Snakemake container directives
- Input/output paths define rule dependencies
- Commands define the shell execution

This is implemented in the Mako template at `pipecraft/backend/templates/snakemake.mako`:

```
rule ${container.name.replace(" ", "_").lower()}:
  input:
    # Input path definitions...
  output:
    # Output path definitions...
  container: "docker://${container.config.image}"
  shell:
    "${' '.join(container.config.cmd)}"
```

### Execution Flow

The execution process follows these steps:
1. Modules define containers with appropriate configurations
2. The pipeline connects containers in sequential or parallel arrangements
3. The backend compiles the pipeline to Snakemake rules
4. Snakemake handles container execution and dependency tracking
5. Results are stored at specified output paths

## Parallelism in Execution

The execution system handles two levels of parallelism:

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

This generates the Snakefile without running it, allowing for inspection and manual execution. Once generated, this Snakefile can be run directly using the Snakemake command-line tool, giving users flexibility in how they execute workflows.

### Logs and Monitoring

The Snakemake backend captures detailed logs of execution. These logs include command outputs, error messages, and execution status for each step in the pipeline. They are stored in the working directory and can be accessed for troubleshooting or monitoring.

When execution fails, several troubleshooting approaches are available:

1. Examine logs in the working directory
2. Check container execution details
3. Validate input configurations
4. Inspect the compiled workflow file

### Execution with Telemetry

For production environments, telemetry can be enabled to send execution information to a monitoring system. This is typically disabled for notebook environments but can be enabled for centralized monitoring in production deployments.

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

## Future Backends

The Snakemake backend demonstrates the power of the architecture by showing that compute graphs can be converted to executable Snakemake workflows. This separation of pipeline definition from execution enables the possibility of developing additional backends for different environments, such as:

1. Cloud-based execution (AWS, GCP, Azure)
2. HPC cluster execution
3. Kubernetes-based execution
4. Custom execution environments

This extensibility is a direct result of the architecture's separation of concerns, where pipelines are defined independently of how they are executed.

## Comparison with Other Approaches

The notebook workflow provides several advantages over direct CLI usage:

1. **State Persistence** - Module configurations are maintained in memory
2. **Parameter Inference** - Automatic configuration from experiments
3. **Containerization** - Automatic execution in containers
4. **Workflow Composition** - Easy combination of multiple steps

The execution through Snakemake also offers benefits compared to direct execution:

1. **Reproducibility** - Ensures consistent execution across environments
2. **Scalability** - Scales from laptops to HPC clusters
3. **Restart Capability** - Can resume from failures without redoing completed work
4. **Resource Management** - Can specify CPU, memory, and other resource requirements
5. **Integration** - Works well with containers and existing tools

## Conclusion

The execution system in StarryNight provides a powerful approach to running pipelines in a reproducible, containerized manner. By combining a flexible execution model with the Snakemake backend, it enables complex workflows to be executed consistently across different environments.

The automatic generation of detailed, executable Snakefiles from high-level abstractions is one of the most impressive achievements of the StarryNight architecture. This capability demonstrates the power of the separation between definition and execution in the system design, allowing complex workflows to be defined at a high level and automatically translated into executable form.

The execution system bridges the gap between abstract pipeline definitions and concrete execution, providing the final layer in StarryNight's architecture that turns conceptual workflows into running processes.

**Next: [Configuration Layer](06_configuration_layer.md)**
