# StarryNight Pipeline Layer

## Overview

The pipeline layer in StarryNight combines two critical aspects: Pipecraft integration for defining compute graphs and pipeline composition for building complete workflows. This layer represents the highest level of abstraction in the StarryNight architecture, sitting above the module layer and below the execution layer.

The pipeline layer enables the creation, composition, and preparation of complex image processing workflows by connecting modules into complete pipelines with well-defined execution patterns. It establishes a clear separation between pipeline definition (what should be done and how it's structured) and execution (how it's actually run), which is a fundamental architectural principle of StarryNight.

## Purpose

The pipeline layer serves several key purposes in the StarryNight architecture:

1. **Compute Graph Definition** - Creating structured representations of computational tasks
2. **Container Configuration** - Specifying container settings for isolated execution
3. **Pipeline Composition** - Combining operations into cohesive workflows
4. **Backend Independence** - Separating pipeline definition from execution
5. **Parallelism Specification** - Defining which operations can run in parallel
6. **Workflow Definition** - Creating end-to-end processing workflows
7. **Module Coordination** - Connecting modules in the correct sequence
8. **Execution Preparation** - Preparing the complete pipeline for execution

These capabilities enable the creation of complex, reproducible workflows for scientific image processing while maintaining a clean separation between definition and execution.

## Pipecraft Integration

### Pipecraft as a Foundation

Pipecraft is a library that enables the creation of composable pipeline graphs in StarryNight. It provides primitives for defining computational operations, containers, and their connections, allowing modules to generate executable compute graphs without being tied to specific execution backends.

Pipecraft serves as the technical foundation for pipeline construction in StarryNight, providing:

1. A standardized framework for defining computational operations
2. Clear abstractions for organizing operations (sequential, parallel)
3. Container definitions independent of execution technology
4. Input/output relationship specifications for pipeline steps

### Pipecraft as a Separate Package

Pipecraft is a separate package within the StarryNight monorepo that provides the foundational pipeline construction capabilities. While most modules and algorithms live in the StarryNight core package, the pipeline construction functionality is implemented in Pipecraft, which:

- Provides a generic pipeline definition framework
- Is developed independently but within the same repository
- Implements a backend-agnostic approach to pipeline execution
- Could potentially be used by other systems beyond StarryNight

This separation allows for focused development of pipeline construction capabilities while maintaining integration with the broader StarryNight framework.

### Pipecraft's Dual Role

Pipecraft serves two essential functions in the StarryNight architecture:

1. **Pipeline Definition**: Creating compute graphs that represent operations and their relationships
2. **Execution Backend Support**: Providing backends to execute the defined compute graphs

This dual capability - both defining compute graphs AND providing execution backends - makes Pipecraft the central technical component that enables the separation between definition and execution, which is fundamental to the entire system.

In the StarryNight architecture, Pipecraft integration happens inside modules. The module layer uses Bilayers to create specifications, and then interfaces with Pipecraft to define how those specifications should be executed as compute graphs. This marks the transition from specification (what needs to be done) to implementation (how to do it).

### Core Pipecraft Concepts

#### Pipeline

A `Pipeline` is the root object that represents the complete compute graph:

```python
pipeline = pc.Pipeline()
```

This object serves as the container for all operations and their relationships.

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

These blocks can be nested to create complex execution patterns with multiple layers of sequential and parallel operations.

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

A critical aspect of Pipecraft integration is container specification. This standardizes how containers should be executed, with specific images, commands, and environment variables. This containerization provides isolation and reproducibility.

The container specification is runtime-agnostic. It defines what should be run in a container but leaves the specifics of how to execute that container to the execution backend. This abstraction allows the same pipeline to run with different container technologies (Docker, Singularity/Apptainer) depending on the execution environment.

### Simple vs. Complex Pipelines

For single-module operations, pipelines are simple and may contain just one node. This might seem redundant, but since compute graphs are composable, even simple operations follow the same pattern to enable later integration into more complex pipelines.

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

Pipeline composition is the final layer of abstraction in StarryNight, allowing multiple modules to be combined into complete workflows.

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

Each module is created and configured based on data and experiment configurations. This approach ensures that all modules have the necessary information to function correctly within the pipeline.

### Building the Pipeline Structure

After creating modules, the function constructs the pipeline structure using Pipecraft's sequential and parallel blocks:

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

This structure defines both sequencing and parallelism in the pipeline. Note how modules are not directly added to the pipeline; instead, their pipeline properties are added using `add_pipeline()`. This ensures that each module's compute graph is properly integrated into the overall pipeline.

The composition function returns both the configured modules and the composed pipeline:

```python
return modules, pipeline
```

This allows users to access both the individual modules (for inspection or modification) and the complete pipeline (for execution).

Returning both the modules and the pipeline enables advanced usage patterns where modules can be individually inspected or modified, and then the pipeline can be recreated with the updated modules. This is particularly valuable for interactive development in notebook environments.

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

This structure allows for expressing complex workflows with appropriate dependencies and execution patterns.

## Expressing Parallelism

The pipeline layer handles parallelism at multiple levels, allowing for efficient execution of complex workflows.

### Between Steps Parallelism

The pipeline composition can express parallelism between different steps. For example, Cell Painting and Sequencing By Synthesis processing can run independently until they reach a point where they need to be combined for analysis.

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

There's also parallelism within specific steps. For instance, illumination correction can be applied to multiple images simultaneously.

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

This approach maximizes efficiency by processing independent items concurrently.

### Unit of Work API

An experimental API for expressing finer-grained parallelism within operations is being developed. This "unit of work" API aims to express more detailed parallelism within operations, allowing for better resource utilization in complex workflows. However, this API is still under development and not yet widely used in production workflows.

## Pipeline Execution

Once a pipeline is composed, it can be executed using a backend:

```python
# Create pipeline
modules, pipeline = create_pcp_generic_pipeline(data_config, pcp_experiment)

# Configure backend
backend_config = pc.SnakemakeBackendConfig(
    use_opentelemetry=False,
    print_exec=True
)
exec_backend = pc.SnakemakeBackend(backend_config)

# Execute pipeline
exec_backend.run(
    pipeline=pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "complete_pipeline"
)
```

This executes the entire workflow in a single operation. The Snakemake backend, which is the primary execution backend in StarryNight, translates the Pipecraft pipeline into a Snakemake workflow and executes it. This process is covered in detail in the [Execution Layer](05_execution_layer.md) section.

All pipeline steps run in containers, ensuring reproducibility and isolation. The Snakemake backend handles the execution of composed pipelines across various infrastructures that support Snakemake.

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

This capability to modify modules and then recreate the pipeline highlights the flexibility and power of the StarryNight architecture.

## The Power of Automatic Generation

One of the most significant benefits of the pipeline construction approach is its ability to generate complex execution plans automatically. The pipeline layer can generate sophisticated Snakemake workflows with hundreds of rules from a high-level pipeline definition.

This automatic generation of complex execution plans is a key value of the entire architecture. It transforms abstract pipeline definitions into concrete, executable workflows without requiring manual creation of complex execution plans.

Using a composed pipeline offers significant advantages over CLI usage:

1. **Dependency Management** - Automatic handling of module dependencies
2. **Parallelism** - Automatic parallel execution where possible
3. **Single Command** - Execute the entire workflow with one command
4. **Resource Optimization** - Better resource utilization across steps
5. **Unified Logging** - Consolidated logging and monitoring
6. **Reproducibility** - Containerized execution ensures consistency
7. **Scalability** - Works from laptops to high-performance computing environments

The pipeline approach provides automation, structure, and reproducibility beyond what's possible with direct CLI usage.

## Relationship to Adjacent Layers

The pipeline layer builds directly on the module layer below it and connects to the execution layer above it:

1. **Module Layer (Below)** - The pipeline layer composes modules defined in the module layer, using their compute graphs as building blocks for larger workflows.

2. **Execution Layer (Above)** - The pipeline layer creates pipeline definitions that are executed by the execution layer, which translates them into specific execution technologies (like Snakemake).

This positioning makes the pipeline layer a critical bridge between individual module abstractions and concrete execution plans.

## Conclusion

Pipeline construction and composition represent the highest level of abstraction in the StarryNight architecture. By leveraging Pipecraft for compute graph definition and providing a structured approach to composing complete workflows, StarryNight enables complex image processing pipelines to be defined, configured, and executed with clarity and flexibility.

The key architectural achievement is the separation between pipeline definition and execution, allowing the same pipeline to run on different backends while maintaining a consistent definition approach. This separation, combined with the powerful composition capabilities, enables the automatic generation of complex execution plans from high-level abstractions.

The pipeline construction capabilities bridge the gap between individual module execution and complete workflow automation, providing a powerful yet comprehensible system for scientific image processing.

**Next: [Execution Layer](05_execution_layer.md)**
