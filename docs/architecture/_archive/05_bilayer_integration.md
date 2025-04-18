# StarryNight Bilayer Integration

## Overview

StarryNight modules use the Bilayers schema system to define specifications for inputs, outputs, and documentation. This integration provides a standardized way to describe what modules do, what they require, and what they produce, enabling automatic UI generation, validation, and interoperability.

## Purpose

The Bilayers integration serves several key purposes in StarryNight:

1. **Standardized Specifications** - Define inputs and outputs consistently across modules
2. **Documentation** - Capture descriptions, citations, and usage information
3. **Validation** - Enable automated validation of inputs and outputs
4. **UI Generation** - Support automatic creation of user interfaces
5. **Configuration** - Structure configuration information in a standard format

As explained in the transcript:

> "This spec is directly from bilayers, and this is how bilayers define its modules. So because bilayers is a separate project that's happening in similab, the goal of bilayers is to create these algorithm wrappers... the idea is, like you have different algorithms, you want to wrap it in a way that then you can generate certain interfaces automatically."

## Bilayers Schema

The Bilayers schema system defines how module specifications should be structured:

### ModuleSpec

A `ModuleSpec` represents a complete module specification including:

- Name and identifier
- Input ports
- Output ports
- Documentation and citations
- Version information

### PortSpec

Each input or output is defined with a `PortSpec` that includes:

- Type (file, directory, string, number, etc.)
- Description
- Default value (if applicable)
- Validation rules
- UI hints

## Example Specification

The `modules/cp_segcheck/segcheck_cppipe.py` file demonstrates Bilayers integration:

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

## Documentation in Bilayers

Bilayers supports rich documentation:

> "There are other things as well that we can define. For example, you know, citations and stuff. We can add documentation and all those things for each input. We can add documentation that can be then shown in the front end, part of it."

This documentation can be used by user interfaces to provide help and guidance.

## Bilayers as an Interface Contract

The Bilayers specification serves as a contract for how modules interact:

1. **For Module Developers** - Defines what the module must provide and expect
2. **For Pipeline Developers** - Defines how modules can be connected
3. **For UI Developers** - Defines what to display and how to collect input
4. **For Execution Engines** - Defines what to validate and how to provide data

## Updating Specifications

An important feature of the Bilayers integration is the ability to update specifications:

> "If you update the spec, yeah, there's another call to this from config method that will with the updated spec, update the pipelines internals, specifically, in this case, the input and output."

This allows runtime changes to module configuration while maintaining consistency.

## Validation with Bilayers

Bilayers provides validation capabilities:

1. **Type Checking** - Ensuring inputs match expected types
2. **Required Inputs** - Verifying all required inputs are provided
3. **Format Validation** - Checking that inputs meet format requirements

## Example: Configuring from Spec

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

## The Value of Standardization

The Bilayers integration provides significant value through standardization:

> "So this is the so that's why we need a kind of model abstraction. Okay, okay, so, so that's, that's what's happening in the modules. I guess if you now to go here and look back..."

By standardizing how modules are defined, StarryNight gains flexibility, composability, and user interface capabilities.

## User Interface Integration

The Bilayers specification is particularly valuable for UI integration:

> "For example, here in the in the interface, you know, for anything, you have this inputs, right? And then we also show what the outputs are. So this is coming from the spec."

This allows user interfaces to be generated automatically from the module specifications.

## Bidirectional Updates

An important capability is the bidirectional relationship between specifications and implementations:

1. **Spec → Implementation** - The specification configures how the module operates
2. **Implementation → Spec** - The implementation can update the specification with results

This bidirectional flow enables adaptability and feedback.

## Bilayers' Evolution

The Bilayers schema system is evolving:

> "And again, because this is again, a moving target, so to speak, that barrier spec is changing as we are figuring out, like what other things are needed."

This highlights the ongoing development of the specification system.

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

## Creating Custom Specifications

When creating new modules, developers must define appropriate specifications:

1. Identify required inputs
2. Define appropriate types
3. Document inputs and outputs
4. Specify validation requirements
5. Add metadata like citations

## Conclusion

The Bilayers integration provides StarryNight with a powerful schema system for defining, documenting, and validating module specifications. This standardization is essential for the module abstraction layer and enables higher-level capabilities like pipeline composition and UI generation.

As the Bilayers system continues to evolve, the specification capabilities of StarryNight will expand, enabling more sophisticated validation, documentation, and interface generation.
