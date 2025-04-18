# StarryNight Module Configuration

## Overview

Module configuration in StarryNight connects experiment parameters with module specifications, allowing modules to be automatically configured based on experiment settings and data configurations. This document explores how modules use configurations from experiments and data to set up their inputs, outputs, and operational parameters.

## Purpose

Module configuration serves several key purposes:

1. **Automatic Setup** - Configuring modules with minimal manual input
2. **Parameter Consistency** - Ensuring consistent parameters across pipeline steps
3. **Path Management** - Setting up standardized input and output paths
4. **Experiment Integration** - Using experiment-specific parameters
5. **Default Generation** - Creating sensible defaults when possible

As explained in the transcript:

> "So for example, in this, in this run, or in this notebook, we are doing PCP, generic... So here we are configuring the experiment once, right? So we are telling it, you know, where in all these things, where my my two channel is like, what matter channel is, what my cell channel is, what my new key channel is, and where my bar code, dot, CSV path is, what's the overlap percentage and things like that, right?"

## from_config Method

The primary method for module configuration is `from_config`:

```python
@classmethod
def from_config(
    cls,
    data_config: DataConfig,
    experiment: Optional[ExperimentConfig] = None,
    spec: Optional[bl.ModuleSpec] = None
) -> "ModuleClass":
    """
    Create a module instance from configuration.

    Parameters
    ----------
    data_config: DataConfig
        Data configuration with paths
    experiment: ExperimentConfig, optional
        Experiment configuration with parameters
    spec: bl.ModuleSpec, optional
        Custom specification if not using default

    Returns
    -------
    ModuleClass
        Configured module instance
    """
    # Implementation...
```

This method creates a configured module based on the provided configurations.

## Data Configuration

The `DataConfig` object provides essential path information:

```python
data_config = DataConfig(
    workspace_path="/path/to/workspace",
    images_path="/path/to/images",
    scratch_path="/path/to/scratch"
)
```

These paths are used to locate inputs and set up outputs:

> "Here we are using lot of data config things right for them, where to read data from, where to write data from, where to write data to."

## Experiment Integration

The experiment parameter provides experiment-specific information:

> "But we're also like, you know, using the experiment and looking at like, what the nuclei channel is, what the cell channel is, and they were using that to construct our command and the entire pipeline."

This allows modules to adapt to specific experiment requirements.

## Spec Parameter

The `spec` parameter allows custom specifications:

```python
# Create module with custom spec
custom_spec = create_custom_spec()
module = ModuleClass.from_config(data_config, experiment, spec=custom_spec)
```

If not provided, a default spec is created based on the data and experiment configurations.

## Implementation Pattern

The typical implementation of `from_config` follows this pattern:

1. Create default spec if none provided
2. Configure inputs based on data_config
3. Configure parameters based on experiment (if provided)
4. Configure outputs based on data_config
5. Create and return module with configured spec

```python
@classmethod
def from_config(cls, data_config, experiment=None, spec=None):
    # Create default spec if none provided
    if spec is None:
        spec = cls().spec

        # Configure inputs from data_config
        spec.inputs["workspace_path"].value = data_config.workspace_path

        # Configure based on experiment if provided
        if experiment is not None:
            spec.inputs["nuclear_channel"].value = experiment.nuclear_channel
            spec.inputs["cell_channel"].value = experiment.cell_channel

        # Configure outputs
        output_path = data_config.workspace_path / "results" / "output.csv"
        spec.outputs["results"].value = output_path

    # Create and return module
    return cls(spec=spec)
```

## Example: Illumination Calculation Module

The transcript examines the illumination calculation module:

> "I guess this is not a good example, because we are not using any information from the experiment, because the only thing we need is where my data is, right?"

This highlights that not all modules use experiment parameters, but all use data configuration for paths.

## Example: Segmentation Check Module

The segmentation check module provides a better example of experiment integration:

> "So here, if you look at like, from config function, right, we are using lot of data config things right for them, where to read data from, where to write data from, where to write data to. But we're also like, you know, using the experiment and looking at like, what the nuclei channel is, what the cell channel is, and they were using that to construct our command and the entire pipeline."

This module requires experiment-specific channel information.

## Detailed Configuration Flow

Let's examine the detailed configuration flow for a module:

### 1. Create Module Instance

```python
# In a notebook or script
segcheck_module = CPSegcheckGenCPipeModule.from_config(
    data_config=data_config,
    experiment=pcp_experiment
)
```

### 2. from_config Implementation

```python
@classmethod
def from_config(cls, data_config, experiment=None, spec=None):
    if spec is None:
        spec = cls().spec

        # Configure workspace path
        spec.inputs["workspace_path"].value = data_config.workspace_path

        # Configure load data path
        load_data_path = data_config.workspace_path / "load_data" / "segcheck_load_data.csv"
        spec.inputs["load_data"].value = load_data_path

        # Configure channels from experiment
        if experiment is not None:
            spec.inputs["nuclear_channel"].value = experiment.nuclear_channel
            spec.inputs["cell_channel"].value = experiment.cell_channel

        # Configure output pipeline path
        pipeline_path = data_config.workspace_path / "pipelines" / "segcheck_pipeline.cppipe"
        spec.outputs["pipeline"].value = pipeline_path

        # Configure output notebook path
        notebook_path = data_config.workspace_path / "notebooks" / "segcheck_visualization.ipynb"
        spec.outputs["notebook"].value = notebook_path

    return cls(spec=spec)
```

### 3. Create Pipeline

The configured module then uses this information to create its pipeline:

```python
def create_pipeline(self):
    # Construct CLI command using spec values
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

## Path Handling Patterns

Modules follow consistent patterns for handling paths:

1. **Input Data** - Typically under `data_config.images_path`
2. **Intermediate Data** - Under `data_config.workspace_path` with subdirectories:
   - `load_data/` - For load data files
   - `pipelines/` - For pipeline files
   - `results/` - For processing results
3. **Execution Data** - Under `data_config.scratch_path / "runs" / module_name`

## Common Module Sets and Their Configuration

Different module sets have different configuration patterns:

### CP Modules (Cell Painting)

CP modules typically require:
- Nuclear channel
- Cell channel
- Other specific channels (e.g., Mito channel)
- Paths to Cell Painting images

### SBS Modules (Sequencing By Synthesis)

SBS modules typically require:
- Barcode information
- Image overlap percentage
- Paths to SBS images

### Common Modules (Index, Inventory)

These modules typically only require:
- Data configuration for paths
- No experiment-specific parameters

## Updating Module Configuration

Module configurations can be updated after creation:

```python
# Create module with default configuration
module = CPSegcheckGenCPipeModule.from_config(data_config, experiment)

# Update a parameter
module.spec.inputs["nuclear_channel"].value = "New_DAPI_Channel"

# Regenerate the pipeline
updated_pipeline = module.create_pipeline()
```

This allows for dynamic reconfiguration.

## Benefits of Automated Configuration

The automated configuration approach offers several benefits:

1. **Reduced Boilerplate** - Minimal code required to set up modules
2. **Consistency** - Parameters are configured consistently across modules
3. **Discoverability** - Clear pattern for how modules are configured
4. **Flexibility** - Custom specs can override defaults when needed
5. **Separation of Concerns** - Configuration logic is separate from execution logic

## Example: Notebook Workflow

Here's how module configuration fits into a typical notebook workflow:

```python
# Import necessary components
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
from starrynight.modules.cp_segcheck import CPSegcheckGenLoadDataModule, CPSegcheckGenCPipeModule
import pipecraft as pc

# Set up paths
workspace_path = "/path/to/workspace"
images_path = "/path/to/images"
scratch_path = "/path/to/scratch"

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
    "barcode_csv_path": "/path/to/barcodes.csv",
    "image_overlap_percentage": 10
}

# Create experiment
pcp_experiment = PCPGenericExperiment.from_index(
    index_path=data_config.workspace_path / "index.yaml",
    init_config=pcp_init_config
)

# Create modules with configuration
load_data_module = CPSegcheckGenLoadDataModule.from_config(
    data_config=data_config,
    experiment=pcp_experiment
)

pipeline_module = CPSegcheckGenCPipeModule.from_config(
    data_config=data_config,
    experiment=pcp_experiment
)

# Configure backend
backend_config = pc.SnakemakeBackendConfig(
    use_opentelemetry=False,
    print_exec=True
)
exec_backend = pc.SnakemakeBackend(backend_config)

# Run modules
exec_backend.run(
    load_data_module.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "segcheck_load_data"
)

exec_backend.run(
    pipeline_module.pipeline,
    config=backend_config,
    working_dir=data_config.scratch_path / "runs" / "segcheck_pipeline"
)
```

## CLI vs. Module Configuration

The module configuration approach differs significantly from CLI usage:

> "In the CLI, I would have basically not used many things that you have here, and lost a whole bunch of things but along the way. But essentially, if I had to replicate this, essentially, I would have specified the input, the output, and then just invoke the algorithm directly through the CLI."

Module configuration provides a richer, more automated approach.

## Creating Custom Module Configurations

To create custom module configurations:

1. Create a ModuleSpec with the desired inputs and outputs
2. Set values for all input parameters
3. Set paths for all output parameters
4. Create the module with the custom spec

```python
# Create custom spec
spec = bl.ModuleSpec(
    name="Custom CP Segcheck Pipeline Generator",
    inputs={
        "load_data": bl.PortSpec(type="file", value="/path/to/custom/load_data.csv"),
        "workspace_path": bl.PortSpec(type="directory", value="/path/to/custom/workspace"),
        "nuclear_channel": bl.PortSpec(type="string", value="CustomDAPI"),
        "cell_channel": bl.PortSpec(type="string", value="CustomCellMask")
    },
    outputs={
        "pipeline": bl.PortSpec(type="file", value="/path/to/custom/pipeline.cppipe")
    }
)

# Create module with custom spec
module = CPSegcheckGenCPipeModule.from_config(
    data_config=data_config,
    experiment=None,  # Not needed since spec is fully configured
    spec=spec
)
```

## Conclusion

Module configuration in StarryNight provides a powerful mechanism for automatically setting up modules based on experiment and data configurations. By standardizing the configuration process through the `from_config` method, it enables consistent, flexible, and maintainable pipeline creation.

The configuration approach bridges the gap between high-level experiment parameters and the detailed settings needed for individual modules, simplifying the creation of complex image processing pipelines.
