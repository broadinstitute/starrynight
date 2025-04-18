# StarryNight Module Layer

## Overview

The module layer provides a standardized abstraction that bridges the algorithm layer (pure functions) and the pipeline layer (complex workflows). Its architectural significance lies in separating what should be done (specifications) from how it should be structured (compute graphs) and how it should be executed (backends).

Modules define both specifications and compute graphs without performing computation. This separation enables backend-agnostic execution (local, cloud) while maintaining a consistent interface for pipeline composition. The module layer integrates with Bilayers for specifications and Pipecraft for compute graphs, creating a powerful abstraction that enables containerized, reproducible execution.

## Purpose and Advantages

The module layer offers significant advantages over directly calling algorithms:

### Practical Benefits
- **Standardization** - Consistent interfaces across different algorithm types
- **Composability** - Modules can be connected into larger workflows
- **Containerization** - Built-in container specification for reproducibility
- **Documentation** - Structured approach to capturing metadata and citations

### Architectural Significance
- **Backend Independence** - Run the same module on different execution systems
- **Inspection** - Examine inputs, outputs, and operations before execution
- **Automated UI Generation** - Specifications support interface generation
- **Complex Workflow Creation** - Enables automatic generation of sophisticated execution plans

## The Dual Nature of Modules

The module layer's defining characteristic is its dual focus on specifications and compute graphs:

1. **Specification (Spec)** - Defines what a module does:
    - Input ports with types, descriptions, and validation rules
    - Output ports with types and descriptions
    - Documentation and metadata
    - Parameter constraints and defaults

2. **Compute Graph** - Defines how operations should be structured:
    - Container configurations
    - Command construction
    - Input/output relationships
    - Execution sequence

Crucially, modules define computation but don't perform it. This separation enables inspection and modification before execution, and allows the same module to run on different platforms without changing its definition.

### Module Sets Organization

Just as the algorithm layer is organized into algorithm sets, the module layer is organized into corresponding module sets. For each algorithm set, there is typically a matching module set that provides the same functionality with the added abstraction of the module layer.

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

This pattern directly mirrors the algorithm set structure covered in the [Algorithm Layer](01_algorithm_layer.md), but adds the standardized abstraction of the module layer.

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

A powerful feature of the module layer is automatic configuration through the `from_config` method. This enables modules to be configured with minimal manual input by inferring paths and parameters from standard configurations:

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

## Specifications with Bilayers

For the "specification" part of a module's dual nature, StarryNight uses Bilayers - an external schema system that standardizes how inputs, outputs, and metadata are defined.

The module layer uses Bilayers to create standardized definitions of:

- Input ports with types and validation rules
- Output ports with types and descriptions
- Documentation and metadata

This standardized approach ensures consistent interface definitions across modules and enables automatic UI generation from specifications.

## Compute Graphs with Pipecraft

For the "compute graph" part of a module's dual nature, StarryNight uses Pipecraft - a library that defines operations and their execution flow.

Modules use Pipecraft to:

- Define operations that should be executed (typically in containers)
- Specify input and output paths
- Structure execution (sequential or parallel)
- Configure container environments

A simple example of how a module creates a compute graph:

```python
# Create a pipeline with sequential execution
pipeline = pc.Pipeline()
with pipeline.sequential() as seq:
    seq.container(
        name="operation_name",
        inputs={"input_path": input_file_path},
        outputs={"output_path": output_file_path},
        container_config=pc.ContainerConfig(
            image="container/image:tag",
            cmd=command_to_execute
        )
    )
```

More detailed coverage of Pipecraft's capabilities and architecture is provided in the [Pipeline Construction](04_pipeline_construction.md) section.

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

## Relationship to Adjacent Layers

The module layer connects directly with two adjacent architectural layers:

1. **Algorithm/CLI Layer (below)** - Modules wrap algorithm functions and typically invoke them via CLI commands in containers
2. **Pipeline Layer (above)** - Modules provide compute graphs that are composed into complete pipelines

The module layer translates between pure functions and executable workflows by providing a standardized interface that both layers can interact with.

## Conclusion

The module layer's dual focus on specifications and compute graphs enables complex workflows to be defined simply and executed consistently across different environments. The next section, [Pipeline Layer](04_pipeline_layer.md), builds upon these abstractions to compose complete workflows from individual modules.
