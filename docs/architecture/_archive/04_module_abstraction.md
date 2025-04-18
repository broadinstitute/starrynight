# Starry Night Module Abstraction

## Overview

The module system in Starry Night provides a standardized abstraction layer that sits above the algorithm layer. Modules capture compute graphs (operations to be performed) and specifications (inputs and outputs) in a consistent way, allowing for composition, configuration, and execution by different backends.

## Purpose

The module abstraction serves several critical purposes:

1. **Standardization** - Provides a consistent interface across different algorithm types
2. **Compute Graph Definition** - Captures the operations to be performed without executing them
3. **Specification Management** - Defines inputs, outputs, and parameters in a structured way
4. **Backend Independence** - Allows execution by different runtime systems
5. **Composability** - Enables modules to be connected into complex pipelines

As explained in the transcript:

> "Module abstractions in Starry Night are a way to describe the compute graph in, you know, using the Piper library so that it's kind of not making an assumption how it's going to get executed."

This abstraction layer adds significant flexibility compared to directly calling algorithms.

## The Dual Focus of Modules

**Critical Point:** The module system has two key components that form its core purpose:

> "A module gives you, first of all, it gives you a spec. So what are the inputs and outputs of this module? It gives you a very keen way depending that, right? So that's the first thing module does. The second thing, it also gives you a compute graph for that particular module, right? For example, what completion needs to be done. You can describe that with the pipe draft library."

This dual focus - spec + compute graph - is the essence of the module abstraction and is the key to backend-agnostic execution.

## Modules Don't Compute

An essential characteristic of modules is that they don't perform the actual computation:

> "It doesn't perform any compute it just gives you the compute graph. So basically, these two things are there in the module, like encapsulated in the module. So first the spec and that there is the compute graph."

This separation of definition from execution is fundamental to the architecture.

## Module Sets Structure

Similar to the algorithm layer's organization into algorithm sets, the module layer is organized into module sets. Each module set typically contains:

1. **Load Data Module** - For generating data loading configurations
2. **Pipeline Generation Module** - For creating processing pipeline definitions
3. **Execution Module** - For running the processing on the data

These modules correspond to the functions in the associated algorithm set but add the layer of abstraction that enables the rest of the Starry Night architecture.

## Module Implementation Structure

A module is implemented as a Python class that inherits from `StarryNightModule`. Each module class typically includes:

1. **Unique Identifier** - A string that uniquely identifies the module
2. **Spec Definition** - Using Bilayers to define inputs and outputs
3. **from_config Method** - For configuration from experiment and data config
4. **Compute Graph Generation** - Methods that create the Pipecraft pipeline

From the transcript:

> "Here we see we have certain things, but the important part is we have, we are creating a class that inherits the Starry Night module. Okay, right. So this is saying that this is a Starry Night module."

## Example: Segmentation Check Module

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

## Module Configuration

One key feature of modules is the ability to be configured from standard configurations:

> "So here I'm saying, okay, the input path, like, you know, we need the load data path that's already generated, you know, somewhere. So I'm automatically, because I know the workspace path from the data config, and I'm using the default location of the load data output from the, you know, from a previous module something, and I'm doing this for like, different inputs and also output, like, where to write the output and stuff like that."

This automatic configuration simplifies the use of modules by inferring paths and parameters from standard configurations.

## Compute Graph Generation

Modules generate compute graphs using the Pipecraft library:

> "So here we are saying, you know, we first constructed the CLI command that we would run inside the container, and then we define, okay, you know, there is [a container]..."

The compute graph defines what operations will be performed but does not execute them. This allows different backends to handle the actual execution.

## Module Structure Components

### Specification (Spec)

The spec defines:
- Input ports with types, descriptions, and validation rules
- Output ports with types and descriptions
- Documentation, citations, and other metadata

### Configuration Method

The `from_config` method:
- Creates default specifications based on standard configurations
- Allows custom specifications to override defaults
- Configures paths and parameters based on context

### Pipeline Creation

The pipeline creation method:
- Constructs the CLI command to execute
- Defines container configuration
- Specifies inputs and outputs for the container
- Creates the compute graph using Pipecraft primitives

## Module Sets

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

## Relationship to Pipecraft

Modules generate Pipecraft pipelines to define their compute graphs:

> "Here we are using the our pipecraft primitives, right? So given all the inputs and outputs, we construct the CLI, you know, CLI commands that we need. And then we are defining a container inside a sequential run."

This is the point where Starry Night interfaces with Pipecraft to define executable operations.

## The Power of the Module System

The central value of the module system is abstracted execution:

> "That's the power of the module system, because it's a track surveyed execution, right?"

By separating specification and compute graph definition from execution, modules enable backend-agnostic processing. This is the architectural achievement that makes the rest of the system possible.

## Pipecraft's Dual Role

Pipecraft serves two critical functions in this architecture:

> "Pipe craft is used for two things. One is, you can just create the compute graph with an additional view. It also provides the back end to execute the computer."

This dual capability - creating compute graphs and executing them - is fundamental to how modules work in Starry Night.

## Why Use Modules?

Modules offer significant advantages over directly calling algorithms:

1. **Standardization** - Common interface across different operations
2. **Abstraction** - Hide implementation details behind consistent interfaces
3. **Composability** - Can be connected into larger workflows
4. **Backend Independence** - Same module can run on different execution systems
5. **Configuration** - Automatic configuration from experiment settings
6. **Inspection** - Can examine inputs, outputs, and operations before execution

As explained in the transcript:

> "...if you need, like, some certain you need a standardized way to create this interface, right? For example, for all the algorithms, you have different input scenarios, different recordings. So that's why you need a standardized, you know, certain abstraction."

## Creating New Modules

To create a new module:

1. Create a new directory in the modules folder
2. Implement module classes for load data, pipeline generation, and execution
3. Define specifications using Bilayers
4. Implement from_config methods for automatic configuration
5. Create pipeline generation methods using Pipecraft
6. Register modules in the module registry

## Conclusion

The module abstraction layer is a critical part of the Starry Night architecture, providing the bridge between low-level algorithms and high-level pipeline composition. By standardizing interfaces, capturing compute graphs, and enabling configuration, modules enable the flexibility and power of the complete system.

As emphasized in the architecture discussions, the module system's focus on specs and compute graphs, with its clean separation from execution, is what makes possible the sophisticated workflow capabilities of Starry Night while maintaining flexibility and clarity.
