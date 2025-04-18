# Starry Night Module System

## Table of Contents
- [Overview](#overview)
- [Purpose](#purpose)
- [Module Abstraction](#module-abstraction)
  - [The Dual Focus of Modules](#the-dual-focus-of-modules)
  - [Modules Don't Compute](#modules-dont-compute)
  - [Module Sets Structure](#module-sets-structure)
- [Module Implementation Structure](#module-implementation-structure)
  - [Example: Segmentation Check Module](#example-segmentation-check-module)
  - [Module Configuration](#module-configuration)
  - [Compute Graph Generation](#compute-graph-generation)
  - [Module Structure Components](#module-structure-components)
- [Bilayer Integration](#bilayer-integration)
  - [Bilayers Schema](#bilayers-schema)
  - [Example Specification](#example-specification)
  - [Documentation in Bilayers](#documentation-in-bilayers)
  - [Bilayers as an Interface Contract](#bilayers-as-an-interface-contract)
  - [Validation with Bilayers](#validation-with-bilayers)
  - [Example: Configuring from Spec](#example-configuring-from-spec)
- [User Interface Integration](#user-interface-integration)
- [Example: Complete Module with Bilayers Integration](#example-complete-module-with-bilayers-integration)
- [Creating New Modules](#creating-new-modules)
- [Conclusion](#conclusion)

## Overview

The module system in Starry Night provides a standardized abstraction layer that sits above the algorithm layer. Modules capture compute graphs (operations to be performed) and specifications (inputs and outputs) in a consistent way, allowing for composition, configuration, and execution by different backends. This module system integrates with the Bilayers schema system to define specifications for inputs, outputs, and documentation, enabling automatic UI generation, validation, and interoperability.

## Purpose

The module system serves several critical purposes in the Starry Night architecture:

1. **Standardization** - Provides a consistent interface across different algorithm types
2. **Compute Graph Definition** - Captures the operations to be performed without executing them
3. **Specification Management** - Defines inputs, outputs, and parameters in a structured way
4. **Backend Independence** - Allows execution by different runtime systems
5. **Composability** - Enables modules to be connected into complex pipelines
6. **Documentation** - Captures descriptions, citations, and usage information
7. **Validation** - Enables automated validation of inputs and outputs
8. **UI Generation** - Supports automatic creation of user interfaces

As explained in the architecture discussions:

> "Module abstractions in Starry Night are a way to describe the compute graph in, you know, using the Piper library so that it's kind of not making an assumption how it's going to get executed."

> "This spec is directly from bilayers, and this is how bilayers define its modules. So because bilayers is a separate project that's happening in similab, the goal of bilayers is to create these algorithm wrappers... the idea is, like you have different algorithms, you want to wrap it in a way that then you can generate certain interfaces automatically."

This abstraction layer adds significant flexibility compared to directly calling algorithms.

## Module Abstraction

### The Dual Focus of Modules

**Critical Point:** The module system has two key components that form its core purpose:

> "A module gives you, first of all, it gives you a spec. So what are the inputs and outputs of this module? It gives you a very keen way depending that, right? So that's the first thing module does. The second thing, it also gives you a compute graph for that particular module, right? For example, what completion needs to be done. You can describe that with the pipe draft library."

This dual focus - spec + compute graph - is the essence of the module abstraction and is the key to backend-agnostic execution.

### Modules Don't Compute

An essential characteristic of modules is that they don't perform the actual computation:

> "It doesn't perform any compute it just gives you the compute graph. So basically, these two things are there in the module, like encapsulated in the module. So first the spec and that there is the compute graph."

This separation of definition from execution is fundamental to the architecture.

### Module Sets Structure

Similar to the algorithm layer's organization into algorithm sets, the module layer is organized into module sets. Each module set typically contains:

1. **Load Data Module** - For generating data loading configurations
2. **Pipeline Generation Module** - For creating processing pipeline definitions
3. **Execution Module** - For running the processing on the data

These modules correspond to the functions in the associated algorithm set but add the layer of abstraction that enables the rest of the Starry Night architecture.

Common module sets in Starry Night include:

1. **CP Modules** - For Cell Painting workflows:
   - `cp_illum_calc` - Illumination calculation
   - `cp_illum_apply` - Illumination correction
   - `cp_pre_segcheck` - Pre-segmentation check
   - `cp_segcheck` - Segmentation check
   - `analysis` - Analysis operations

2. **SBS Modules** - For Sequencing By Synthesis workflows:
   - `sbs_illum_calc` - SBS illumination calculation
   - `sbs_illum_apply` - SBS illumination correction
   - `sbs_align` - SBS alignment
   - `sbs_preprocess` - SBS preprocessing

3. **Common Modules** - For general operations:
   - `gen_index` - Index generation
   - `gen_inv` - Inventory management

## Module Implementation Structure

A module is implemented as a Python class that inherits from `StarryNightModule`. Each module class typically includes:

1. **Unique Identifier** - A string that uniquely identifies the module
2. **Spec Definition** - Using Bilayers to define inputs and outputs
3. **from_config Method** - For configuration from experiment and data config
4. **Compute Graph Generation** - Methods that create the Pipecraft pipeline

From the architecture discussions:

> "Here we see we have certain things, but the important part is we have, we are creating a class that inherits the Starry Night module. Okay, right. So this is saying that this is a Starry Night module."

### Example: Segmentation Check Module

The `modules/cp_segcheck/segcheck_cppipe.py` file demonstrates a module implementation:

```python
class CpSegcheckGenCPipeModule(StarryNightModule):
    """
    Module for generating CellProfiler pipeline for segmentation check.
    """

    @property
    def module_id(self) -> str:
        """Unique identifier for this module."""
        return "cp_segcheck_gen_cppipe"

    @property
    def spec(self) -> bl.ModuleSpec:
        """Default specification for this module."""
        spec = bl.ModuleSpec(
            name="CP Segcheck Pipeline Generator",
            inputs={
                "load_data": bl.PortSpec(
                    type="file",
                    description="Load data CSV file"
                ),
                "workspace_path": bl.PortSpec(
                    type="directory",
                    description="Workspace directory"
                ),
                "nuclear_channel": bl.PortSpec(
                    type="string",
                    description="Nuclear stain channel name"
                ),
                "cell_channel": bl.PortSpec(
                    type="string",
                    description="Cell membrane channel name"
                )
            },
            outputs={
                "pipeline": bl.PortSpec(
                    type="file",
                    description="Generated CellProfiler pipeline"
                )
            }
        )
        return spec

    @classmethod
    def from_config(
        cls,
        data_config: DataConfig,
        experiment: Optional[ExperimentConfig] = None,
        spec: Optional[bl.ModuleSpec] = None
    ) -> "CpSegcheckGenCPipeModule":
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
        CpSegcheckGenCPipeModule
            Configured module instance
        """
        # Create default spec if none provided
        if spec is None:
            spec = cls().spec

            # Set up paths based on data config
            # Set up parameters based on experiment
            # ...

        # Create and return the module with populated spec
        return cls(spec=spec)

    def create_pipeline(self) -> pc.Pipeline:
        """
        Create the compute graph (Pipecraft pipeline) for this module.
        """
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

### Module Configuration

One key feature of modules is the ability to be configured from standard configurations:

> "So here I'm saying, okay, the input path, like, you know, we need the load data path that's already generated, you know, somewhere. So I'm automatically, because I know the workspace path from the data config, and I'm using the default location of the load data output from the, you know, from a previous module something, and I'm doing this for like, different inputs and also output, like, where to write the output and stuff like that."

This automatic configuration simplifies the use of modules by inferring paths and parameters from standard configurations.

### Compute Graph Generation

Modules generate compute graphs using the Pipecraft library:

> "So here we are saying, you know, we first constructed the CLI command that we would run inside the container, and then we define, okay, you know, there is [a container]..."

The compute graph defines what operations will be performed but does not execute them. This allows different backends to handle the actual execution.

### Module Structure Components

#### Specification (Spec)

The spec defines:
- Input ports with types, descriptions, and validation rules
- Output ports with types and descriptions
- Documentation, citations, and other metadata

#### Configuration Method

The `from_config` method:
- Creates default specifications based on standard configurations
- Allows custom specifications to override defaults
- Configures paths and parameters based on context

#### Pipeline Creation

The pipeline creation method:
- Constructs the CLI command to execute
- Defines container configuration
- Specifies inputs and outputs for the container
- Creates the compute graph using Pipecraft primitives

## Bilayer Integration

Starry Night modules use the Bilayers schema system to define specifications for inputs, outputs, and documentation. This integration is a critical part of the module system's standardization.

### Bilayers Schema

The Bilayers schema system defines how module specifications should be structured:

#### ModuleSpec

A `ModuleSpec` represents a complete module specification including:

- Name and identifier
- Input ports
- Output ports
- Documentation and citations
- Version information

#### PortSpec

Each input or output is defined with a `PortSpec` that includes:

- Type (file, directory, string, number, etc.)
- Description
- Default value (if applicable)
- Validation rules
- UI hints

### Example Specification

Here's an example of a Bilayers specification from `modules/cp_segcheck/segcheck_cppipe.py`:

```python
@property
def spec(self) -> bl.ModuleSpec:
    """Default specification for this module."""
    spec = bl.ModuleSpec(
        name="CP Segcheck Pipeline Generator",
        inputs={
            "load_data": bl.PortSpec(
                type="file",
                description="Load data CSV file"
            ),
            "workspace_path": bl.PortSpec(
                type="directory",
                description="Workspace directory"
            ),
            "nuclear_channel": bl.PortSpec(
                type="string",
                description="Nuclear stain channel name"
            ),
            "cell_channel": bl.PortSpec(
                type="string",
                description="Cell membrane channel name"
            )
        },
        outputs={
            "pipeline": bl.PortSpec(
                type="file",
                description="Generated CellProfiler pipeline"
            ),
            "notebook": bl.PortSpec(
                type="file",
                description="Jupyter notebook for visualization"
            )
        }
    )
    return spec
```

### Documentation in Bilayers

Bilayers supports rich documentation:

> "There are other things as well that we can define. For example, you know, citations and stuff. We can add documentation and all those things for each input. We can add documentation that can be then shown in the front end, part of it."

This documentation can be used by user interfaces to provide help and guidance.

### Bilayers as an Interface Contract

The Bilayers specification serves as a contract for how modules interact:

1. **For Module Developers** - Defines what the module must provide and expect
2. **For Pipeline Developers** - Defines how modules can be connected
3. **For UI Developers** - Defines what to display and how to collect input
4. **For Execution Engines** - Defines what to validate and how to provide data

### Validation with Bilayers

Bilayers provides validation capabilities:

1. **Type Checking** - Ensuring inputs match expected types
2. **Required Inputs** - Verifying all required inputs are provided
3. **Format Validation** - Checking that inputs meet format requirements

### Example: Configuring from Spec

The relationship between specification and configuration is demonstrated in the `from_config` method:

```python
@classmethod
def from_config(
    cls,
    data_config: DataConfig,
    experiment: Optional[ExperimentConfig] = None,
    spec: Optional[bl.ModuleSpec] = None
) -> "CpSegcheckGenCPipeModule":
    """Create a module instance from configuration."""
    # Create default spec if none provided
    if spec is None:
        spec = cls().spec

        # Configure inputs based on data_config
        spec.inputs["workspace_path"].value = data_config.workspace_path

        # Default load_data path based on workspace
        load_data_path = data_config.workspace_path / "load_data" / "segcheck_load_data.csv"
        spec.inputs["load_data"].value = load_data_path

        # Configure based on experiment if provided
        if experiment is not None:
            spec.inputs["nuclear_channel"].value = experiment.nuclear_channel
            spec.inputs["cell_channel"].value = experiment.cell_channel

        # Configure outputs
        pipeline_path = data_config.workspace_path / "pipelines" / "segcheck_pipeline.cppipe"
        spec.outputs["pipeline"].value = pipeline_path

    # Create and return module with the spec
    return cls(spec=spec)
```

## User Interface Integration

The Bilayers specification is particularly valuable for UI integration:

> "For example, here in the in the interface, you know, for anything, you have this inputs, right? And then we also show what the outputs are. So this is coming from the spec."

This allows user interfaces to be generated automatically from the module specifications.

An important capability is the bidirectional relationship between specifications and implementations:

1. **Spec → Implementation** - The specification configures how the module operates
2. **Implementation → Spec** - The implementation can update the specification with results

This bidirectional flow enables adaptability and feedback.

## Example: Complete Module with Bilayers Integration

Here's an extended example showing how Bilayers is integrated throughout a module implementation:

```python
import bilayers as bl
from starrynight.modules.base import StarryNightModule
from starrynight.config import DataConfig, ExperimentConfig
import pipecraft as pc
from typing import Optional

class IllumCalcLoadDataModule(StarryNightModule):
    """Module for generating illumination calculation load data."""

    @property
    def module_id(self) -> str:
        """Unique identifier for this module."""
        return "cp_illum_calc_load_data"

    @property
    def spec(self) -> bl.ModuleSpec:
        """Default specification for this module."""
        spec = bl.ModuleSpec(
            name="CP Illumination Calculation Load Data Generator",
            description="Generates load data for illumination calculation",
            version="1.0.0",
            inputs={
                "images_path": bl.PortSpec(
                    type="directory",
                    description="Path to raw images",
                    required=True
                ),
                "batch_id": bl.PortSpec(
                    type="string",
                    description="Batch identifier",
                    required=True
                ),
                "plate_id": bl.PortSpec(
                    type="string",
                    description="Plate identifier",
                    required=True
                ),
                "channels": bl.PortSpec(
                    type="array",
                    items={"type": "string"},
                    description="Channel names to process",
                    required=True
                )
            },
            outputs={
                "load_data": bl.PortSpec(
                    type="file",
                    description="Generated load data CSV file"
                )
            },
            citations=[
                {
                    "title": "CellProfiler: image analysis software for identifying and quantifying cell phenotypes",
                    "authors": "Carpenter AE, et al.",
                    "journal": "Genome Biology",
                    "year": 2006,
                    "url": "https://doi.org/10.1186/gb-2006-7-10-r100"
                }
            ]
        )
        return spec

    @classmethod
    def from_config(
        cls,
        data_config: DataConfig,
        experiment: Optional[ExperimentConfig] = None,
        spec: Optional[bl.ModuleSpec] = None
    ) -> "IllumCalcLoadDataModule":
        """Create module from configuration."""
        if spec is None:
            spec = cls().spec

            # Set input paths
            spec.inputs["images_path"].value = data_config.images_path

            # Set experiment-specific parameters
            if experiment is not None:
                spec.inputs["batch_id"].value = experiment.batch_id
                spec.inputs["plate_id"].value = experiment.plate_id
                spec.inputs["channels"].value = experiment.channels

            # Set output paths
            output_path = data_config.workspace_path / "load_data" / "illum_calc_load_data.csv"
            spec.outputs["load_data"].value = output_path

        return cls(spec=spec)

    def create_pipeline(self) -> pc.Pipeline:
        """Create compute graph for this module."""
        # Build CLI command from spec
        command = [
            "starrynight", "illum", "generate-load-data",
            "--images-path", str(self.spec.inputs["images_path"].value),
            "--output-path", str(self.spec.outputs["load_data"].value),
            "--batch-id", str(self.spec.inputs["batch_id"].value),
            "--plate-id", str(self.spec.inputs["plate_id"].value)
        ]

        # Add channels
        for channel in self.spec.inputs["channels"].value:
            command.extend(["--channel", channel])

        # Create pipeline with container
        pipeline = pc.Pipeline()
        with pipeline.sequential() as seq:
            seq.container(
                name="illum_calc_load_data_gen",
                inputs={
                    "images": str(self.spec.inputs["images_path"].value)
                },
                outputs={
                    "load_data": str(self.spec.outputs["load_data"].value)
                },
                container_config=pc.ContainerConfig(
                    image="cellprofiler/starrynight:latest",
                    command=command
                )
            )

        return pipeline
```

## Creating New Modules

To create a new module:

1. Create a new directory in the modules folder
2. Implement module classes for load data, pipeline generation, and execution
3. Define specifications using Bilayers
4. Implement from_config methods for automatic configuration
5. Create pipeline generation methods using Pipecraft
6. Register modules in the module registry

## Conclusion

The module system is a central architectural component of Starry Night, providing the critical bridge between low-level algorithms and high-level pipeline composition. By combining the module abstraction with Bilayers schema integration, Starry Night achieves:

1. **Standardized Interfaces** - Consistent patterns across all components
2. **Clear Separation of Concerns** - Specs are separate from implementation, and definition is separate from execution
3. **Flexible Configuration** - Modules can be automatically configured from experiment settings
4. **UI Integration** - Specifications support automatic interface generation
5. **Backend Independence** - The same module can be executed on different backends

As emphasized in the architecture discussions:

> "That's the power of the module system, because it's a track surveyed execution, right?"

This separation of specification from execution, combined with the rich schema capabilities of Bilayers, is what makes possible the sophisticated workflow capabilities of Starry Night while maintaining flexibility and clarity.

**Next: [Pipeline Construction](06-12_pipeline_construction.md)**
