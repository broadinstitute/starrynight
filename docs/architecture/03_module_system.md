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

!!! note "Modules Don't Compute"

    Modules define computation but don't perform it. This separation of definition from execution enables backend-agnostic processing, allowing the same module to run on different platforms without changing its definition.

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
2. **SBS Modules** - For Sequencing By Synthesis workflows:
    - `sbs_illum_calc` - SBS illumination calculation modules
    - `sbs_illum_apply` - SBS illumination correction modules
    - `sbs_align` - SBS alignment modules
    - `sbs_preprocess` - SBS preprocessing modules
3. **Common Modules** - For general operations:
    - `gen_index` - Index generation modules
    - `gen_inv` - Inventory management modules
    - `analysis` - Analysis modules

## Module Implementation

A module is implemented as a Python class that inherits from `StarryNightModule`. Each module implementation follows a consistent structure with several key components:

1. **Unique Identifier** - A string property that uniquely identifies the module
2. **Spec Definition** - A property method that defines the module's specification using Bilayers
3. **`from_config` Method** - A class method for configuration from experiment and data configurations
4. **Compute Graph Generation** - A method that creates the Pipecraft pipeline defining the computation structure

This structure ensures that all modules provide the same capabilities, making them consistent and interchangeable at the architectural level.

### Example: Segmentation Check Module

Below is an example of a module that generates a CellProfiler pipeline for segmentation check. This example illustrates all the key components of a module implementation:

```python
class CPSegcheckGenCPPipeModule(StarrynightModule):
    """CP segmentation check generate cppipe module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "cp_segcheck_gen_cppipe"

    @staticmethod
    def _spec() -> str:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="load_data_path",
                    type=TypeEnum.files,
                    description="Path to the LoadData csv.",
                    optional=False,
                    path="path/to/the/loaddata",
                ),
                TypeInput(
                    name="workspace_path",
                    type=TypeEnum.file,
                    description="Workspace path.",
                    optional=True,
                    path=None,
                ),
                TypeInput(
                    name="nuclei_channel",
                    type=TypeEnum.textbox,
                    description="Channel to use for nuclei segmentation.",
                    optional=False,
                ),
                TypeInput(
                    name="cell_channel",
                    type=TypeEnum.textbox,
                    description="Channel to use for cell segmentation.",
                    optional=False,
                ),
            ],
            outputs=[
                TypeOutput(
                    name="cp_segcheck_cpipe",
                    type=TypeEnum.files,
                    description="Generated pre segcheck cppipe files",
                    optional=False,
                    path="random/path/to/cppipe_dir",
                ),
                TypeOutput(
                    name="cppipe_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting cellprofiler pipeline files",
                    optional=False,
                    path="http://karkinos:2720/?file=.%2FillumCPApplyOutput.py",
                ),
            ],
            parameters=[],
            display_only=[],
            results=[],
            exec_function=ExecFunction(
                name="",
                script="",
                module="",
                cli_command="",
            ),
            docker_image=None,
            algorithm_folder_name=None,
            citations=TypeCitations(
                algorithm=[
                    TypeAlgorithmFromCitation(
                        name="Starrynight CP segmentation check generate cppipe module",
                        description="This module generates cppipe files for cp segmentation check module.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        data: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
    ) -> Self:
        """Create module from experiment and data config."""
        if spec is None:
            spec = CPSegcheckGenCPPipeModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath(CP_SEGCHECK_CP_LOADDATA_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )

            spec.inputs[1].path = (
                data.workspace_path.joinpath(CP_SEGCHECK_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )

            spec.inputs[2].path = experiment.cp_config.nuclei_channel
            spec.inputs[3].path = experiment.cp_config.cell_channel

            spec.outputs[0].path = (
                data.workspace_path.joinpath(CP_SEGCHECK_CP_CPPIPE_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_cppipe(
            uid=CPSegcheckGenCPPipeModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(out_dir=data.storage_path.joinpath("index"))

        return CPSegcheckGenCPPipeModule(spec=spec, pipe=pipe, uow=uow)



```

This example illustrates several important aspects of module implementation:

1. **Module Identity** - The `uid()` method provides a unique identifier
2. **Module Specification** - The `_spec()` method defines inputs, outputs, and metadata
3. **Automatic Configuration** - The `from_config` method populates the specification based on standard configurations
4. **Compute Graph Creation** - The module uses the `create_pipe_gen_cppipe` function to generate a Pipecraft pipeline
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

## Bilayers Integration

Bilayers is an external schema system used to define module specifications. It provides a structured way to define inputs, outputs, and metadata that enables automatic UI generation and validation.

The module system uses Bilayers to create standardized definitions of:
- Input ports with types and validation rules
- Output ports with types and descriptions
- Documentation and metadata

This standardized approach ensures consistent interface definitions across modules and enables automatic UI generation from specifications.

## Pipecraft Integration

Pipecraft is the library that enables modules to define compute graphs - structured representations of operations and their execution flow. This integration is where StarryNight interfaces with the pipeline construction system.

### Core Pipecraft Components

Based on the actual codebase in `/pipecraft/src/pipecraft/`:

1. **Pipeline** - Abstract base class for pipelines with subclasses:
   - **Seq** - For sequential execution of operations
   - **Parallel** - For parallel execution with scatter-gather patterns

2. **Node** - Base class for operations with specialized types:
   - **Container** - For containerized operations
   - **PyFunction** - For Python function execution
   - **Scatter/Gather** - For parallel execution control

3. **Backend** - System for executing the pipeline:
   - **SnakemakeBackend** - Converts pipelines to Snakefiles
   - **AWSBatchBackend** - For cloud execution

### Creating Compute Graphs

Modules use Pipecraft's API to create compute graphs by:

1. Creating a `Pipeline` object
2. Defining execution contexts (sequential, parallel)
3. Adding container nodes with input/output mappings
4. Configuring container execution environments

```python
# Example of a simple compute graph definition
pipeline = pc.Pipeline()
with pipeline.sequential() as seq:
    seq.container(
        name="operation_name",
        inputs={"input1": "input/path"},
        outputs={"output1": "output/path"},
        container_config=pc.ContainerConfig(
            image="container/image:tag",
            cmd=["command", "arg1", "arg2"]
        )
    )
```

This separation between graph definition and execution is fundamental to StarryNight's architecture, enabling the same module to run on different execution backends.

## Module Usage

Modules are typically used in two different contexts: direct usage for individual operations and pipeline composition for complete workflows.

### Direct Module Usage

For individual module operations, modules can be created and executed directly:

```python
# Import necessary components
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
from starrynight.modules.cp_segcheck import CPSegcheckGenCPPipeModule
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
segcheck_module = CPSegcheckGenCPPipeModule.from_config(data_config, experiment)

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
