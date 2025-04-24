# StarryNight Pipeline Composition and Execution

## Overview

Pipeline composition is the final layer of abstraction in StarryNight, allowing multiple modules to be combined into complete workflows. This document explores how pipelines are composed, how modules are connected, and how complete pipelines are executed to process image data.

## Purpose

Pipeline composition serves several key purposes:

1. **Workflow Definition** - Creating end-to-end processing workflows
2. **Module Coordination** - Connecting modules in the correct sequence
3. **Parallel Execution** - Defining which operations can run in parallel
4. **Sequential Constraints** - Enforcing dependencies between operations
5. **Execution Preparation** - Preparing the complete pipeline for execution

As explained in the transcript:

> "So instead of now running individual modules, what we are doing here is really composing all the models together, right? So you know, we are saying that run all these steps in sequentially, so all the CP steps sequentially, and then all the SBS steps sequentially, but run these two sets in parallel, and then after this, run the analysis steps sequentially, right?"

## Pipeline Composition Function

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

## Module Creation and Configuration

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

## Building the Pipeline Structure

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

## Example from Transcript

The transcript describes a pipeline composition function:

> "If you go to pipelines here...we are looking at PCP generic.pi...instead of now running individual modules, what we are doing here is really composing all the models together, right? So you know, we are saying that run all these steps in sequentially, so all the CP steps sequentially, and then all the SBS steps sequentially, but run these two sets in parallel, and then after this, run the analysis steps sequentially, right?"

This shows how complex execution patterns can be defined.

## Returning Modules and Pipeline

The composition function returns both the configured modules and the composed pipeline:

```python
return modules, pipeline
```

This allows users to access both the individual modules (for inspection or modification) and the complete pipeline (for execution).

> "This is your, this is your pipecraft pipeline. Pipecraft pipeline... Now you might be asking, like, why, why you wanted? Because the module itself has a pipe craft pipeline inside it, yeah... this is, this is because you can individually inspect how these individual models are configured. You can then change it and then invoke this function again with the updated, updated spec."

## Using the Composed Pipeline

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

## Pipeline Visualization

While not shown in the transcript, composed pipelines can typically be visualized to show the complete workflow structure. This can be valuable for understanding complex pipelines.

## Comparison with Individual Module Execution

Composed pipelines offer several advantages over individual module execution:

1. **Dependency Management** - Automatic handling of module dependencies
2. **Parallelism** - Automatic parallel execution where possible
3. **Single Command** - Execute the entire workflow with one command
4. **Resource Optimization** - Better resource utilization across steps
5. **Unified Logging** - Consolidated logging and monitoring

## Example: Complete Pipeline Composition

Here's a more detailed example of pipeline composition:

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

## Modifying Modules After Composition

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

## Two Levels of Parallelism

The pipeline composition can express two levels of parallelism:

1. **Between Steps** - Running CP and SBS branches in parallel:
   > "There's parallelism between different steps. So certain steps can be run, you know, independently of each other. We have eight steps or nine steps, right? Some of them can be run independently. For example, like SBS part can be run independently of the self painting part, right, up until some point."

2. **Within Steps** - Parallelism within specific modules:
   > "But there's also parallelism in in the in single nodes as well, right? For example, you can run ILLUM apply parallely, right? You can use you can, you know you have multiple images. You can apply ILLUM on multiple images simultaneously, right?"

These levels are handled differently in the architecture.

## Pipeline Registry

Similar to experiments and modules, pipelines can be registered in a registry:

```python
from starrynight.pipelines.registry import register_pipeline

@register_pipeline("pcp_generic")
def create_pcp_generic_pipeline(data_config, experiment):
    """Create complete PCP generic pipeline."""
    # Implementation...
```

This allows pipelines to be looked up by name.

## Notebook Example for Pipeline Execution

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

## CLI vs. Pipeline Comparison

Using a composed pipeline offers significant advantages over CLI usage:

> "If I knocked out Canvas and conductor entirely deleted those files, I would still be able to do a lot with your current functionality in terms of being able to run high throughput screen level experiments through your pipeline, because I will, I mean, I can still do that just using cell profiler, but what I can now do on CLI is that using a using a notebook and using a JSON file where I can configure my experiment, right? I can read that experiment from this JSON file in my notebook. I can configure every module that I need to run, and then I can run them, and I can get my jobs."

The pipeline approach provides automation, structure, and reproducibility beyond what's possible with direct CLI usage.

## Snakemake as the Backend

The Snakemake backend handles the execution of composed pipelines:

> "So in theory, anything like any, anything that can run, sneak, make files across multiple cores, whatever multiple units can now make use of this."

This allows pipelines to run on various infrastructures that support Snakemake.

## Container Execution

All pipeline steps run in containers:

> "We're saying, run this container with this name, with this input and output paths, and with this container config, which says, Use this image and then run with this command line, command line that we constructed before."

This ensures reproducibility and isolation.

## Execution with Telemetry

For production environments, telemetry can be enabled:

> "For example, because we are running it in notebook, we are not using the open telemetry set up to export logs to a central server... because we are not using the centralized server to collect all the logs."

In production, telemetry would typically be enabled for centralized monitoring.

## Conclusion

Pipeline composition is the top layer of abstraction in StarryNight, allowing complex image processing workflows to be defined, configured, and executed. By combining modules into structured pipelines with both sequential and parallel execution paths, it enables sophisticated processing while maintaining flexibility and clarity.

The composition approach bridges the gap between individual module execution and complete workflow automation, providing a powerful yet comprehensible system for scientific image processing.
