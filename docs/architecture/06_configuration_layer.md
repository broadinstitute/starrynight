# StarryNight Configuration Layer

!!! Warning
    - This document contains bot-generated text and has not yet been reviewed by developers!

## Overview

The configuration layer in StarryNight consists of two interconnected systems: experiment configuration, which manages experiment-specific parameters and infers settings from data, and module configuration, which connects these parameters with module specifications. Together, these systems enable automatic setup of complex pipelines with minimal manual input, creating a bridge between user-provided parameters and the detailed configuration needed for pipeline execution.

## Purpose

The configuration layer in StarryNight serves several critical purposes:

1. **Parameter Management** - Collecting and organizing essential parameters
2. **Parameter Inference** - Determining settings automatically from data
3. **Standardization** - Providing consistent configuration across modules
4. **Extensibility** - Supporting different experiment types
5. **Module Configuration** - Simplifying the setup of pipeline modules
6. **Automatic Setup** - Configuring modules with minimal manual input
7. **Parameter Consistency** - Ensuring consistent parameters across pipeline steps
8. **Path Management** - Setting up standardized input and output paths

As explained in the architecture discussions:

> "...once we are done with indexing and inventory and indexing, then we move to like, you know what specific experiment I'm actually doing, right? So based on that, we we prepare certain conflicts."

> "So for example, in this, in this run, or in this notebook, we are doing PCP, generic... So here we are configuring the experiment once, right? So we are telling it, you know, where in all these things, where my my two channel is like, what matter channel is, what my cell channel is, what my new key channel is, and where my bar code, dot, CSV path is, what's the overlap percentage and things like that, right?"

## Experiment Configuration

Experiment configuration provides a systematic way to manage experiment-specific parameters and infer settings from data.

### Experiment Classes

Experiments are implemented as Python classes that inherit from a base experiment class:

```python
class PCPGenericExperiment(ExperimentBase):
    """
    Experiment configuration for generic Plate Cell Painting.
    """
    # Implementation...
```

The architecture discussions examine the `PCPGenericExperiment` class as an example.

### From Index Method

A critical method in experiment classes is `from_index`, which initializes the experiment from index data:

> "There is a function called from index on your experimental side of things... So you give it your index path and your experiment, this initial config, which cannot be guessed, and then it will guess everything else that's required in your, in your, you know, in a downstream pipeline..."

This method takes two main parameters:

1. **Index Path** - Path to the index file generated by indexing
2. **Initial Config** - User-provided parameters that cannot be inferred

```python
@classmethod
def from_index(cls, index_path: AnyPath, init_config: Dict[str, Any]) -> "PCPGenericExperiment":
    """
    Create experiment configuration from index and initial config.

    Parameters
    ----------
    index_path : AnyPath
        Path to the index file
    init_config : Dict[str, Any]
        Initial configuration parameters

    Returns
    -------
    PCPGenericExperiment
        Configured experiment instance
    """
    # Implementation...
```

### Initial Configuration

The initial configuration includes parameters that cannot be inferred from data:

```python
pcp_init_config = {
    "nuclear_channel": "DAPI",
    "cell_channel": "CellMask",
    "mito_channel": "MitoTracker",
    "barcode_csv_path": "/path/to/barcodes.csv",
    "image_overlap_percentage": 10
}
```

These parameters are experiment-specific and must be provided by the user.

### Parameter Inference

A key feature of experiment classes is their ability to infer parameters from data:

> "It will extract what a data set ID is. It will create a data frame for all the CP images, for SPS images, and then calculate how many images are per Well, for the cell painting things right? Because it knows it has the inventory. It can do queries against the inventory and then figure out, like for each well, how many images are there, right?"

Examples of inferred parameters:

1. **Images per Well** - Calculated from inventory data
2. **Channel Count** - Determined from image metadata
3. **Channel List** - Extracted from available images
4. **Dataset Structure** - Inferred from file organization

This inference reduces the manual configuration burden on users.

Here's a simplified example of parameter inference in the `from_index` method:

```python
@classmethod
def from_index(cls, index_path: AnyPath, init_config: Dict[str, Any]) -> "PCPGenericExperiment":
    # Load index
    index = load_yaml(index_path)

    # Create experiment instance
    experiment = cls()

    # Add user-provided parameters
    experiment.nuclear_channel = init_config["nuclear_channel"]
    experiment.cell_channel = init_config["cell_channel"]
    experiment.mito_channel = init_config["mito_channel"]
    experiment.barcode_csv_path = init_config["barcode_csv_path"]
    experiment.image_overlap_percentage = init_config["image_overlap_percentage"]

    # Infer parameters from index
    experiment.dataset_id = index["dataset_id"]

    # Create dataframes for CP and SBS images
    experiment.cp_images_df = create_cp_images_dataframe(index)
    experiment.sbs_images_df = create_sbs_images_dataframe(index)

    # Calculate derived parameters
    experiment.images_per_well = calculate_images_per_well(experiment.cp_images_df)
    experiment.cp_channels = extract_cp_channels(experiment.cp_images_df)
    experiment.cp_channel_count = len(experiment.cp_channels)
    experiment.sbs_channels = extract_sbs_channels(experiment.sbs_images_df)
    experiment.sbs_channel_count = len(experiment.sbs_channels)

    # More parameter inference...

    return experiment
```

### Using Experiment Configurations

Once configured, the experiment object is passed to modules when creating them:

```python
# Create a module with experiment configuration
illum_calc_module = CPIllumCalcLoadDataModule.from_config(
    data_config=data_config,
    experiment=pcp_experiment
)
```

The module then uses the experiment configuration to set its parameters:

> "So here, if you look at like, from config function, right, we are using lot of data config things right for them, where to read data from, where to write data from, where to write data to. But we're also like, you know, using the experiment and looking at like, what the nuclei channel is, what the cell channel is, and they were using that to construct our command and the entire pipeline."

### Different Experiment Types

The architecture supports different experiment types:

> "In this, in this run, or in this notebook, we are doing PCP, generic. That's what then you might give it. But you can imagine calling it, you know, PCP, I don't know the saber or something faster, slow to color chemistry, you know, whatever variants you want, right?"

Each experiment type can have its own class with specific parameter inference logic.

### Creating New Experiment Types

To create a new experiment type:

1. Create a new file in the experiments folder
2. Define a class that inherits from ExperimentBase
3. Implement the from_index method
4. Define parameter inference logic
5. Register the experiment class in the registry

As explained in the architecture discussions:

> "So you know, in future, if you want to extend this to different experiments. Here you do this, right? You create a new file, and then you create a new class and inherit from the experiment class, right? And the method you have to define is called from index."

### Experiment Registry

Experiments are registered in a registry to make them discoverable:

```python
from starrynight.experiments.registry import register_experiment

@register_experiment("pcp_generic")
class PCPGenericExperiment(ExperimentBase):
    """Experiment configuration for generic Plate Cell Painting."""
    # Implementation...
```

This allows experiments to be looked up by name.

## Module Configuration

Module configuration connects experiment parameters with module specifications, allowing modules to be automatically configured based on experiment settings and data configurations.

### from_config Method

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

### Data Configuration

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

### Experiment Integration

The experiment parameter provides experiment-specific information:

> "But we're also like, you know, using the experiment and looking at like, what the nuclei channel is, what the cell channel is, and they were using that to construct our command and the entire pipeline."

This allows modules to adapt to specific experiment requirements.

### Spec Parameter

The `spec` parameter allows custom specifications:

```python
# Create module with custom spec
custom_spec = create_custom_spec()
module = ModuleClass.from_config(data_config, experiment, spec=custom_spec)
```

If not provided, a default spec is created based on the data and experiment configurations.

### Implementation Pattern

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

## Configuration Flow Examples

### Example: Segmentation Check Module

The segmentation check module provides a good example of experiment integration:

> "So here, if you look at like, from config function, right, we are using lot of data config things right for them, where to read data from, where to write data from, where to write data to. But we're also like, you know, using the experiment and looking at like, what the nuclei channel is, what the cell channel is, and they were using that to construct our command and the entire pipeline."

This module requires experiment-specific channel information.

### Example: Illumination Calculation Module

The illumination calculation module demonstrates that not all modules require experiment parameters:

> "I guess this is not a good example, because we are not using any information from the experiment, because the only thing we need is where my data is, right?"

This highlights that some modules only use data configuration for paths, without experiment-specific parameters.

### Detailed Configuration Flow

Let's examine the detailed configuration flow for a module:

#### 1. Create Module Instance

```python
# In a notebook or script
segcheck_module = CPSegcheckGenCPipeModule.from_config(
    data_config=data_config,
    experiment=pcp_experiment
)
```

#### 2. from_config Implementation

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

#### 3. Create Pipeline

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

## Advanced Configuration Topics

### Updating Module Configuration

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

### Serialization and Deserialization

Experiment configurations can be serialized and deserialized:

```python
# Serialize experiment to JSON
experiment_json = pcp_experiment.to_json()

# Save to file
with open("experiment_config.json", "w") as f:
    f.write(experiment_json)

# Later, load from file
with open("experiment_config.json", "r") as f:
    experiment_json = f.read()

# Deserialize experiment
pcp_experiment = PCPGenericExperiment.from_json(experiment_json)
```

This allows experiment configurations to be saved and restored.

### Creating Custom Module Configurations

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

## Complete Examples

### Example: Complete Experiment Class

Here's a more complete example of an experiment class:

```python
@register_experiment("pcp_generic")
class PCPGenericExperiment(ExperimentBase):
    """
    Experiment configuration for generic Plate Cell Painting.
    """

    def __init__(self):
        """Initialize experiment configuration."""
        # User-provided parameters
        self.nuclear_channel = None
        self.cell_channel = None
        self.mito_channel = None
        self.barcode_csv_path = None
        self.image_overlap_percentage = None

        # Inferred parameters
        self.dataset_id = None
        self.cp_images_df = None
        self.sbs_images_df = None
        self.images_per_well = None
        self.cp_channels = None
        self.cp_channel_count = None
        self.sbs_channels = None
        self.sbs_channel_count = None
        # More parameters...

    @classmethod
    def from_index(cls, index_path: AnyPath, init_config: Dict[str, Any]) -> "PCPGenericExperiment":
        """Create experiment from index and initial config."""
        # Implementation...

        # Load index
        index = load_yaml(index_path)

        # Create experiment instance
        experiment = cls()

        # Set user-provided parameters
        experiment.nuclear_channel = init_config["nuclear_channel"]
        experiment.cell_channel = init_config["cell_channel"]
        experiment.mito_channel = init_config["mito_channel"]
        experiment.barcode_csv_path = init_config["barcode_csv_path"]
        experiment.image_overlap_percentage = init_config["image_overlap_percentage"]

        # Infer parameters from index
        # (implementation details...)

        return experiment

    def validate(self) -> bool:
        """Validate experiment configuration."""
        # Check required parameters
        if not self.nuclear_channel:
            raise ValueError("Nuclear channel must be specified")
        if not self.cell_channel:
            raise ValueError("Cell channel must be specified")

        # More validation...

        return True
```

### Example: Notebook Workflow

Here's how configuration fits into a typical notebook workflow:

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

## Comparison with Direct CLI Usage

The configuration approach differs significantly from CLI usage:

> "In the CLI, I would have basically not used many things that you have here, and lost a whole bunch of things but along the way. But essentially, if I had to replicate this, essentially, I would have specified the input, the output, and then just invoke the algorithm directly through the CLI."

The configuration system provides a richer, more automated approach with several benefits:

1. **Reduced Manual Configuration** - Many parameters are inferred automatically
2. **Consistency** - Parameters are defined once and used consistently
3. **Validation** - Parameters can be validated during inference
4. **Extensibility** - New experiment types can be added without changing modules
5. **Separation of Concerns** - Experiment logic is separate from module logic
6. **Reduced Boilerplate** - Minimal code required to set up modules
7. **Discoverability** - Clear pattern for how modules are configured
8. **Flexibility** - Custom specs can override defaults when needed

## Conclusion

The experiment and module configuration systems in StarryNight provide a powerful approach to managing parameters, inferring settings from data, and automatically configuring modules. By separating experiment-specific logic from module implementation and providing standardized configuration patterns, they enable flexibility, extensibility, and consistency across the pipeline system.

Together, these configuration systems form a critical bridge between user input and pipeline execution, reducing manual configuration burden while maintaining flexibility for different experiment types and module implementations. They exemplify the architecture's focus on separation of concerns, allowing each component to focus on its specific role while working together to create a cohesive system.

**Next: [Architecture for Biologists](07_architecture_for_biologists.md)**
