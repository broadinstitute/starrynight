# StarryNight Module System

## Overview

The module system in StarryNight provides a standardized abstraction layer that sits above the algorithm and CLI layers. Modules define both specifications (what should be done) and compute graphs (how it should be structured) without actually performing the computation. This separation enables backend-agnostic execution and forms the foundation for pipeline composition.

The module system integrates with the Bilayers schema system to define specifications for inputs, outputs, and parameters, while using Pipecraft to define computation structures. This combination enables automatic UI generation, validation, and interoperability with different execution backends.

## Purpose

The module system serves several critical purposes in the StarryNight architecture:

1. **Standardization** - Provides a consistent interface across different algorithm types
2. **Compute Graph Definition** - Captures the operations to be performed without executing them
3. **Specification Management** - Defines inputs, outputs, and parameters in a structured way
4. **Backend Independence** - Allows execution by different runtime systems
5. **Composability** - Enables modules to be connected into complex pipelines
6. **Documentation** - Captures descriptions, citations, and usage information
7. **Validation** - Enables automated validation of inputs and outputs
8. **Container Integration** - Specifies containerized execution environments

The module system is the core architectural layer that bridges the gap between the pure Python functions in the algorithm layer and the composable pipelines that enable complex workflows. By providing consistent abstractions, it allows the same operations to be defined once but executed in various contexts (local, cloud, etc.).

## The Dual Nature of Modules

The module system's central architectural feature is its dual focus, which defines both what a module does and how it should be structured:

1. **Specification (Spec)** - Defines what the module does:
    - Input ports with types, descriptions, and validation rules
    - Output ports with types and descriptions
    - Documentation and metadata
    - Parameter constraints and defaults
2. **Compute Graph** - Defines how the operation should be structured:
    - Container configurations
    - Command construction
    - Input/output relationships
    - Execution sequence

This dual focus enables modules to describe both their interface requirements and execution structure without implementing the actual computation.

### Modules Don't Compute

A critical characteristic of modules is that they don't perform the actual computation:

1. **Definition Only** - Modules define what should be done and how it should be structured
2. **Execution Delegation** - Actual execution is handled by separate backend systems
3. **Inspection Capability** - Modules can be examined and modified before execution

This separation of definition from execution is fundamental to the StarryNight architecture and enables backend-agnostic processing. It allows the same module to potentially run on multiple execution platforms without changing its definition.

### Module Sets Organization

Just as the algorithm layer is organized into algorithm sets, the module layer is organized into corresponding module sets. For each algorithm set, there is typically a matching module set that provides the same functionality with the added abstraction layer.

Each module set typically follows a consistent pattern with three types of modules:

1. **Load Data Modules** - Generate data loading configurations
    - Define which images to process
    - Create CSV files for CellProfiler to locate images
    - Organize data by batch, plate, well, and site
2. **Pipeline Generation Modules** - Create processing pipeline definitions
    - Generate CellProfiler pipeline files
    - Configure pipeline parameters based on experiment settings
    - Define processing operations
3. **Execution Modules** - Execute the pipeline on prepared data
    - Run pipelines with appropriate parallelism
    - Manage resource allocation
    - Organize outputs according to experimental structure

This pattern directly mirrors the algorithm set structure covered in the [Algorithm Layer](01_algorithm_layer.md), but adds the standardized module abstraction layer.

Common module sets include:

1. **CP Modules** - For Cell Painting workflows:
    - `cp_illum_calc` - Illumination calculation modules
    - `cp_illum_apply` - Illumination correction modules
    - `cp_segcheck` - Segmentation check modules
    - `analysis` - Analysis modules
2. **SBS Modules** - For Sequencing By Synthesis workflows:
    - `sbs_illum_calc` - SBS illumination calculation modules
    - `sbs_illum_apply` - SBS illumination correction modules
    - `sbs_align` - SBS alignment modules
    - `sbs_preprocess` - SBS preprocessing modules
3. **Common Modules** - For general operations:
    - `gen_index` - Index generation modules
    - `gen_inv` - Inventory management modules

## Module Implementation

A module is implemented as a Python class that inherits from `StarryNightModule`. Each module implementation follows a consistent structure with several key components:

1. **Unique Identifier** - A string property that uniquely identifies the module
2. **Spec Definition** - A property method that defines the module's specification using Bilayers
3. **from_config Method** - A class method for configuration from experiment and data configurations
4. **Compute Graph Generation** - A method that creates the Pipecraft pipeline defining the computation structure

This structure ensures that all modules provide the same capabilities, making them consistent and interchangeable at the architectural level.

### Example: Segmentation Check Module

Below is an example of a module that generates a CellProfiler pipeline for segmentation check. This example illustrates all the key components of a module implementation:

```python
class CpSegcheckGenCPipeModule(StarryNightModule):
    """Module for generating CellProfiler pipeline for segmentation check."""

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

            # Configure default paths based on data_config
            load_data_path = data_config.workspace_path / "load_data" / "segcheck_load_data.csv"
            spec.inputs["load_data"].value = load_data_path
            spec.inputs["workspace_path"].value = data_config.workspace_path

            # Configure experiment-specific parameters
            if experiment is not None:
                spec.inputs["nuclear_channel"].value = experiment.nuclear_channel
                spec.inputs["cell_channel"].value = experiment.cell_channel

            # Configure output paths
            pipeline_path = data_config.workspace_path / "pipelines" / "segcheck_pipeline.cppipe"
            spec.outputs["pipeline"].value = pipeline_path

        # Create and return the module with populated spec
        return cls(spec=spec)

    def create_pipeline(self) -> pc.Pipeline:
        """Create the compute graph (Pipecraft pipeline) for this module."""
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

This example illustrates several important aspects of module implementation:

1. **Module Identity** - The `module_id` property provides a unique identifier
2. **Module Specification** - The `spec` property defines inputs, outputs, and metadata
3. **Automatic Configuration** - The `from_config` method populates the specification based on standard configurations
4. **Compute Graph Creation** - The `create_pipeline` method generates a Pipecraft pipeline that defines the computation structure
5. **CLI Command Construction** - The module constructs a CLI command that will be executed in a container
6. **Container Specification** - The module defines the container image and execution environment

### Module Configuration

A powerful feature of the module system is automatic configuration through the `from_config` method. This enables modules to be configured with minimal manual input by inferring paths and parameters from standard configurations:

1. **Data Configuration** - Provides workspace paths, image paths, and scratch directories
2. **Experiment Configuration** - Provides experiment-specific parameters like channel names, algorithms, and thresholds
3. **Default Path Inference** - Creates conventional file paths based on workspace structure

This automatic configuration approach has several advantages:

- **Consistency** - Ensures consistent file organization across projects
- **Reduced Configuration** - Minimizes parameters that users need to specify
- **Standardization** - Enforces standard naming and path conventions
- **Modularity** - Allows modules to be swapped without changing their configuration

The `from_config` method bridges the gap between user-provided parameters and the detailed configuration required for execution.

### Compute Graph Generation with Pipecraft

The `create_pipeline` method is where modules generate their compute graphs using the Pipecraft library. This method defines the structure of the computation without actually executing it:

1. **CLI Command Construction** - The module builds a command-line invocation of the underlying algorithm
2. **Container Configuration** - Specifies the container image, environment, and resource requirements
3. **Input/Output Mapping** - Defines how inputs and outputs are mapped to the container filesystem
4. **Execution Structure** - Specifies the execution sequence (sequential, parallel, etc.)

The compute graph provides a complete definition of how the operation should be executed, but remains independent of any specific execution technology. This separation allows the same module to be executed on different backends (local, cluster, cloud) without modification.

## Bilayers Integration for Specifications

The module system uses the Bilayers schema system to define specifications. Bilayers is an external library that provides a structured way to define module interfaces, enabling automatic UI generation, validation, and standardization.

### Bilayers Schema Components

1. **ModuleSpec** - The top-level specification container:
    - Module name and description
    - Input ports dictionary
    - Output ports dictionary
    - Documentation and citations
    - Version information
2. **PortSpec** - Specification for individual input or output ports:
    - Type information (file, directory, string, number, etc.)
    - Description for documentation
    - Validation rules
    - Default values
    - UI hints and constraints

### Benefits of Bilayers Integration

The Bilayers integration provides several key benefits:

1. **Standardization** - Common specification format across all modules
2. **Interface Generation** - Enables automatic UI creation from specifications
3. **Validation** - Built-in validation of inputs and outputs
4. **Documentation** - Structured approach to documenting module interfaces
5. **Extensibility** - Can be extended with new types and validation rules

## Pipecraft Integration

Pipecraft is a library that enables modules to define compute graphs - the structured representation of what operations should be performed and how they should be executed. This integration is where StarryNight interfaces with the pipeline construction system.

### Pipecraft Components

1. **Pipeline** - The root object representing the complete compute graph
2. **Sequential Blocks** - Define operations that must run in sequence
3. **Parallel Blocks** - Define operations that can run simultaneously
4. **Container Nodes** - Represent containerized operations
5. **ContainerConfig** - Define container execution environments

### Pipecraft's Role

Pipecraft plays a dual role in the StarryNight architecture:

1. **Compute Graph Definition** - Enables modules to define their computation structure
2. **Backend Preparation** - Provides the foundation for converting compute graphs to executable form

This dual capability is what enables the separation between definition and execution, which is fundamental to the entire system.

### Creating Compute Graphs

A module's `create_pipeline` method uses Pipecraft to create a compute graph:

```python
def create_pipeline(self) -> pc.Pipeline:
    """Create compute graph for this module."""
    # Build CLI command
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

### Key Aspects of Pipecraft Integration

1. **CLI Command Construction** - Most modules construct CLI commands that invoke the underlying algorithm functions
2. **Container Specification** - Modules define the container image and environment for execution
3. **Input/Output Mapping** - Modules map specification ports to container filesystem paths
4. **Execution Structure** - Modules define sequential or parallel execution contexts

The integration with Pipecraft enables modules to be both composable (they can be connected into larger pipelines) and backend-agnostic (they can run on different execution systems).

## Module Usage

Modules are typically used in two different contexts: direct usage for individual operations and pipeline composition for complete workflows.

### Direct Module Usage

For individual module operations, modules can be created and executed directly:

```python
# Import necessary components
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
from starrynight.modules.cp_segcheck import CpSegcheckGenCPipeModule
import pipecraft as pc

# Create configurations
data_config = DataConfig(
    workspace_path="/path/to/workspace",
    images_path="/path/to/images",
    scratch_path="/path/to/scratch"
)

experiment = PCPGenericExperiment.from_index(
    index_path=data_config.workspace_path / "index.yaml",
    init_config={
        "nuclear_channel": "DAPI",
        "cell_channel": "CellMask"
    }
)

# Create module
segcheck_module = CpSegcheckGenCPipeModule.from_config(data_config, experiment)

# Configure backend
backend = pc.SnakemakeBackend()

# Execute module
backend.run(
    pipeline=segcheck_module.create_pipeline(),
    working_dir=data_config.scratch_path / "segcheck_run"
)
```

### Pipeline Composition

For complex workflows, modules are typically composed into pipelines:

```python
# Create modules
modules = []
modules.append(GenIndexModule.from_config(data_config))
modules.append(GenInvModule.from_config(data_config))
modules.append(CPIllumCalcGenLoadDataModule.from_config(data_config, experiment))
modules.append(CPIllumCalcGenCPipeModule.from_config(data_config, experiment))
modules.append(CPIllumCalcRunModule.from_config(data_config, experiment))

# Create pipeline
pipeline = pc.Pipeline()
with pipeline.sequential() as seq:
    for module in modules:
        seq.add_pipeline(module.create_pipeline())

# Execute pipeline
backend.run(
    pipeline=pipeline,
    working_dir=data_config.scratch_path / "complete_run"
)
```

In pipeline composition, modules are created and configured individually, but their compute graphs are combined into a larger structure that defines the complete workflow. This approach is discussed in detail in [Pipeline Construction](04_pipeline_construction.md).

## Creating New Modules

Creating a new module set involves implementing classes for each stage of processing:

1. **Plan the Module Set**:
   - Identify the algorithm set to wrap
   - Determine inputs, outputs, and parameters
   - Design the module structure (typically load data, pipeline generation, and execution)

2. **Create Module Classes**:
   - Implement subclasses of `StarryNightModule` for each stage
   - Define unique identifiers and specifications
   - Implement `from_config` methods
   - Create pipeline generation methods

3. **Define Specifications**:
   - Use Bilayers to define inputs, outputs, and parameters
   - Document parameters with clear descriptions
   - Define validation rules

4. **Implement Pipeline Creation**:
   - Use Pipecraft to define compute graphs
   - Specify container configurations
   - Map inputs and outputs properly

5. **Test the Modules**:
   - Test individual modules
   - Test automatic configuration
   - Test pipeline integration

## Advantages of the Module System

The module system offers significant advantages over directly calling algorithms:

1. **Standardization** - Common interface across different operations
2. **Abstraction** - Hide implementation details behind consistent interfaces
3. **Composability** - Connect modules into larger workflows
4. **Backend Independence** - Run the same module on different execution systems
5. **Configuration** - Automatic configuration from experiment settings
6. **Inspection** - Examine inputs, outputs, and operations before execution
7. **Containerization** - Built-in container specification for reproducibility

These advantages enable StarryNight to handle complex scientific image processing workflows with clarity and flexibility.

## The Architectural Achievement

The module system sits at the center of the StarryNight architecture, providing the critical bridge between low-level algorithms and high-level pipeline composition. Its key architectural achievement is the clear separation between:

1. **What should be done** - Defined by specifications
2. **How it should be structured** - Defined by compute graphs
3. **How it should be executed** - Delegated to execution backends

This separation enables the automatic generation of complex execution plans from simple abstractions. By defining operations once at the module level, StarryNight can execute them in various contexts (notebooks, CLI, UI) and on different infrastructures (local, cloud) without changing their definition.

## Relationship to Adjacent Layers

The module system connects directly with two adjacent architectural layers:

1. **Algorithm/CLI Layer (below)** - Modules wrap algorithm functions and typically invoke them via CLI commands in containers
2. **Pipeline Construction Layer (above)** - Modules provide compute graphs that are composed into complete pipelines

This position in the architecture makes the module system the critical translation layer between pure functions and executable workflows.

## Conclusion

The module system provides a powerful abstraction that enables backend-agnostic execution through its dual focus on specifications and compute graphs. By standardizing the interfaces between components and providing a structured approach to configuration, StarryNight achieves a clear separation of concerns that makes complex image processing workflows both manageable and extensible.

The next section, [Pipeline Construction](04_pipeline_construction.md), builds upon the module system to create complete workflows by composing multiple modules into executable pipelines.
