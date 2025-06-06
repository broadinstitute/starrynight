# StarryNight Module Layer

## Overview

The module layer provides a standardized abstraction that bridges the CLI layer (command-line interfaces) and the pipeline layer (complex workflows). Its architectural significance lies in separating what should be done (specifications) from how it should be structured (compute graphs) and how it should be executed (backends).

Modules define both specifications and compute graphs without performing computation. This separation enables backend-agnostic execution (local, cloud) while maintaining a consistent interface for pipeline composition. The module layer integrates with Bilayers for specifications and Pipecraft for compute graphs, creating a powerful abstraction that enables containerized, reproducible execution. Importantly, modules don't directly call algorithm functions but instead invoke CLI commands that in turn execute the underlying algorithms.

## Purpose and Advantages

The module layer offers significant advantages over directly using CLI commands:

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

Just as the CLI layer is organized into command groups that map to algorithm sets, the module layer is organized into corresponding module sets. For each CLI command group, there is typically a matching module set that provides the same functionality with the added abstraction of the module layer.

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

This pattern mirrors the organization of algorithms and CLI commands, but adds the standardized abstraction and container orchestration capabilities of the module layer.

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

    @property
    def uid(self) -> str:
        """Return module unique id."""
        return "cp_segcheck_gen_cppipe"

    def _spec(self) -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs={
                "loaddata_path": TypeInput(
                    name="Cellprofiler LoadData csvs",
                    type=TypeEnum.dir,
                    description="Path to the LoadData csv.",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_SEGCHECK_CP_LOADDATA_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "workspace_path": TypeInput(
                    name="Workspace",
                    type=TypeEnum.dir,
                    description="Workspace path.",
                    optional=True,
                    value=self.data_config.workspace_path.joinpath(
                        CP_SEGCHECK_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "nuclei_channel": TypeInput(
                    name="Nuclei channel",
                    type=TypeEnum.textbox,
                    description="Channel to use for nuclei segmentation.",
                    optional=False,
                    value=self.experiment.cp_config.nuclei_channel,
                ),
                "cell_channel": TypeInput(
                    name="Cell channel",
                    type=TypeEnum.textbox,
                    description="Channel to use for cell segmentation.",
                    optional=False,
                    value=self.experiment.cp_config.cell_channel,
                ),
                "use_legacy": TypeInput(
                    name="Use legacy pipeline",
                    type=TypeEnum.boolean,
                    description="Flag for using legacy pipeline.",
                    optional=True,
                    value=False,
                ),
            },
            outputs={
                "cppipe_path": TypeOutput(
                    name="Cellprofiler pipeline",
                    type=TypeEnum.file,
                    description="Generated pre segcheck cppipe files",
                    optional=False,
                    value=self.data_config.workspace_path.joinpath(
                        CP_SEGCHECK_CP_CPPIPE_OUT_PATH_SUFFIX
                    )
                    .resolve()
                    .__str__(),
                ),
                "notebook_path": TypeOutput(
                    name="QC notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting cellprofiler pipeline files",
                    optional=False,
                ),
            },
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

    def _create_uow(self) -> list[UnitOfWork]:
        """Create units of work for Generate Index step.

        Returns
        -------
        list[UnitOfWork]
            List of unit of work.

        """
        return []

    def _create_pipe(self) -> Pipeline:
        """Create pipeline for generating cpipe.

        Returns
        -------
        Pipeline
            Pipeline instance.

        """
        spec = self.spec
        cmd = [
            "starrynight",
            "segcheck",
            "cppipe",
            "-l",
            spec.inputs["loaddata_path"].value,
            "-o",
            spec.outputs["cppipe_path"].value,
            "-w",
            spec.inputs["workspace_path"].value,
            "-n",
            spec.inputs["nuclei_channel"].value,
            "-c",
            spec.inputs["cell_channel"].value,
        ]

        if spec.inputs["use_legacy"].value is True:
            cmd += [
                "--use_legacy",
            ]
        gen_load_data_pipe = Seq(
            [
                Container(
                    name=self.uid,
                    input_paths={
                        "loaddata_path": [spec.inputs["loaddata_path"].value]
                    },
                    output_paths={
                        "cppipe_path": [spec.outputs["cppipe_path"].value]
                    },
                    config=ContainerConfig(
                        image="ghrc.io/leoank/starrynight:dev",
                        cmd=cmd,
                        env={},
                    ),
                ),
            ]
        )
        return gen_load_data_pipe
```

This example illustrates several important aspects of module implementation:

1. **Module Identity** - The `uid()` method provides a unique identifier
2. **Module Specification** - The `_spec()` method defines inputs, outputs, and metadata and also set default values.
4. **Compute Graph Creation** - The module uses the `_create_pipe` function to generate a Pipecraft pipeline
5. **CLI Command Construction** - The module constructs a CLI command that will be executed in a container
6. **Container Specification** - The module defines the container image and execution environment

### Module Configuration

A powerful feature of the module layer is automatic configuration. This enables modules to be configured with minimal manual input by inferring paths and parameters from standard configurations:

1. **Data Configuration** - Provides workspace paths, image paths, and scratch directories
2. **Experiment Configuration** - Provides experiment-specific parameters like channel names, algorithms, and thresholds
3. **Default Path Inference** - Creates conventional file paths based on workspace structure

This automatic configuration approach has several advantages:

- **Consistency** - Ensures consistent file organization across projects
- **Reduced Configuration** - Minimizes parameters that users need to specify
- **Standardization** - Enforces standard naming and path conventions
- **Modularity** - Allows modules to be swapped without changing their configuration

### Compute Graph Generation with Pipecraft

The `_create_pipe` method is where modules generate their compute graphs using the Pipecraft library. This method defines the structure of the computation without actually executing it:

1. **CLI Command Construction** - The module builds a command-line invocation of the underlying algorithm
2. **Container Configuration** - Specifies the container image, environment, and resource requirements
3. **Input/Output Mapping** - Defines how inputs and outputs are mapped to the container filesystem
4. **Execution Structure** - Specifies the execution sequence (sequential, parallel, etc.)

The compute graph provides a complete definition of how the operation should be executed, but remains independent of any specific execution technology. This separation allows the same module to be executed on different backends (local, cluster, cloud) without modification.

## Specifications with Bilayers

For the "specification" part of a module's dual nature, StarryNight uses Bilayers - an external schema system that standardizes how inputs, outputs, and metadata are defined.

### What is Bilayers?

Bilayers is an open-source specification and framework designed to make bioimage analysis algorithms accessible through auto-generated user interfaces. It bridges the gap between algorithm developers and biologists by providing:

- A standardized YAML-based configuration format for describing algorithm interfaces
- Automatic generation of web interfaces (Gradio) and Jupyter notebooks from these configurations
- A consistent way to package algorithms in Docker containers with their interfaces
- A schema validation system based on LinkML to ensure configurations are correct

The Bilayers project enables algorithm developers to write a single configuration file that describes their tool's inputs, outputs, and parameters, and automatically get user-friendly interfaces without writing UI code.

### How StarryNight Integrates Bilayers

StarryNight leverages the Bilayers specification system to standardize its module interfaces. The integration works through several mechanisms:

1. **Schema Download and Synchronization**: StarryNight maintains a local copy of the Bilayers validation schema, which is automatically downloaded from the Bilayers repository:
   ```python
   # From starrynight/modules/common.py
   VALIDATE_SCHEMA_URL = "https://raw.githubusercontent.com/bilayer-containers/bilayers/master/tests/test_config/validate_schema.yaml"
   ```

2. **Pydantic Model Generation**: The Bilayers LinkML schema is converted into Pydantic models that StarryNight uses for runtime validation:
   ```python
   def update_module_schema() -> None:
       """Download and update the module schema from bilayers."""
       schema_yaml = Path(__file__).parent.joinpath("validate_schema.yaml")
       schema_path = Path(__file__).parent.joinpath("schema.py")
       # Download schema and generate Pydantic models
   ```

3. **SpecContainer Integration**: Each StarryNight module defines its specification using the `SpecContainer` class, which is derived from the Bilayers schema. This ensures compatibility with the broader Bilayers ecosystem.

### The Bilayers Specification Structure

The module layer uses Bilayers to create standardized definitions of:

- **Input Specifications**:
  - Type definitions (image, file, directory, array, measurement)
  - Validation rules and constraints
  - Default values and optional flags
  - Descriptions for documentation
  - CLI tag mappings for command generation

- **Output Specifications**:
  - Output types and formats
  - File naming patterns
  - Directory structures
  - Relationships to inputs

- **Parameter Definitions**:
  - UI element types (checkbox, integer, float, dropdown, textbox)
  - Value constraints and defaults
  - Grouping for beginner/advanced modes
  - Help text and documentation

- **Algorithm Metadata**:
  - Citations and references
  - Docker image specifications
  - License information
  - Algorithm descriptions

### Example: How a Module Uses Bilayers

When a StarryNight module implements its `_spec()` method, it returns a `SpecContainer` that follows the Bilayers schema:

```python
def _spec(self) -> SpecContainer:
    return SpecContainer(
        inputs={
            "input_image": TypeInput(
                name="input_image",
                type=TypeEnum.image,
                description="Input microscopy image",
                cli_tag="-i",
                optional=False,
            )
        },
        outputs={
            "processed_image": TypeOutput(
                name="processed_image",
                type=TypeEnum.image,
                description="Processed output image",
            )
        },
        parameters=[
            # Bilayers-compliant parameter definitions
        ],
        citations=TypeCitations(
            algorithm=[
                TypeAlgorithmFromCitation(
                    name="Algorithm Name",
                    description="Algorithm description",
                )
            ]
        ),
    )
```

### Benefits of Using Bilayers

1. **Standardization**: All modules follow the same specification format, making them predictable and easy to understand.

2. **Interoperability**: Because StarryNight uses the Bilayers specification, there's potential for:
   - Importing Bilayers-compatible tools from other projects
   - Exporting StarryNight modules for use in other Bilayers-compatible systems
   - Leveraging the broader Bilayers ecosystem of tools and interfaces

3. **Automatic UI Generation**: While StarryNight doesn't currently generate Gradio or Jupyter interfaces from these specs, the Bilayers-compliant specifications make this possible in the future.

4. **Validation**: The LinkML-based schema provides robust validation of module specifications, catching configuration errors early.

5. **Documentation**: The structured format ensures that all modules have consistent documentation for their inputs, outputs, and parameters.

This standardized approach ensures consistent interface definitions across modules and enables potential future features like automatic UI generation from specifications.

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
pipeline = Seq(
    Container(
        name="external_tool",
        input_paths={
            "some_input": [...],
        },
        output_paths={
            "some_output": [...]
        },
        config=ContainerConfig(
            image="externaltoolimage",
            cmd=["externaltool"],
            env={},
        ),
    )
)
```

More detailed coverage of Pipecraft's capabilities and architecture is provided in the [Pipeline Layer](04_pipeline_layer.md) section.

## Module Usage

Modules are typically used in two different contexts: direct usage for individual operations and pipeline composition for complete workflows.

### Direct Module Usage

For individual module operations, modules can be created and executed directly:

```python
# Import necessary components
from starrynight.config import DataConfig
from starrynight.experiments.pcp_generic import PCPGenericExperiment
from starrynight.modules.cp_segcheck import CPSegcheckGenCPPipeModule
from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig

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
segcheck_module = CPSegcheckGenCPPipeModule(data_config, experiment)

# Configure backend
backend_config = SnakeMakeConfig(
    use_fluent_bit=False, print_exec=True, background=False
)

# Create backend
exec_backend = SnakeMakeBackend(
    segcheck_module.pipe, backend_config, exec_runs / "run001", exec_mounts
)

# Execute module
run = exec_backend.run()
run.wait()
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
pipeline = Seq(modules)

# Execute pipeline
exec_backend = SnakeMakeBackend(
    pipeline, backend_config, exec_runs / "run001", exec_mounts
)
run = exec_backend.run()
run.wait()
```

In pipeline composition, modules are created and configured individually, but their compute graphs are combined into a larger structure that defines the complete workflow. This approach is discussed in detail in [Pipeline Layer](04_pipeline_layer.md).

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

1. **CLI Layer (below)** - Modules invoke CLI commands in containers rather than directly calling algorithm functions
2. **Pipeline Layer (above)** - Modules provide compute graphs that are composed into complete pipelines

The module layer translates between CLI commands and complex workflows by providing a standardized interface and containerization approach for executing CLI commands in a pipeline context.

## Module Registry Mechanism

StarryNight uses registry mechanisms to organize and discover available modules throughout the system. The module registry serves as a central catalog of all available modules, making it easy to:

1. Discover available modules by name or type
2. Instantiate modules programmatically
3. Integrate modules into pipelines
4. Extend the system with new modules

### Registry Implementation

The registry is implemented in `starrynight/modules/registry.py` as a Python dictionary mapping unique module identifiers to module classes:

```python
MODULE_REGISTRY: dict[str, StarrynightModule] = {
    # Generate inventory and index for the project
    GenInvModule.uid(): GenInvModule,
    GenIndexModule.uid(): GenIndexModule,
    # CP illum calc
    CPCalcIllumGenLoadDataModule.uid(): CPCalcIllumGenLoadDataModule,
    CPCalcIllumGenCPPipeModule.uid(): CPCalcIllumGenCPPipeModule,
    CPCalcIllumInvokeCPModule.uid(): CPCalcIllumInvokeCPModule,
    # Additional modules...
}
```

Each module defines its unique identifier through a static `uid()` method, which returns a string that serves as the module's registry key.

### Registering New Modules

To add a new module to the system:

1. Implement the module class following the module pattern
2. Define a unique ID through the `uid()` static method
3. Add the module to the `MODULE_REGISTRY` dictionary

The registry pattern makes it easy to extend StarryNight with new module types while maintaining a clean, discoverable architecture.

### Registry Usage

The module registry is used in several contexts:

1. **Pipeline Composition** - Finding modules to include in a pipeline
2. **Experiment Configuration** - Determining which modules to use for an experiment type
3. **Module Discovery** - Listing available modules for user interfaces
4. **Dynamic Loading** - Loading modules at runtime based on configuration

Similar registry mechanisms exist for experiments (`experiments/registry.py`) and pipelines (`pipelines/registry.py`), creating a unified approach to component discovery across the system.

## Conclusion

The module layer's dual focus on specifications and compute graphs enables complex workflows to be defined simply and executed consistently across different environments. The registry mechanism provides a flexible way to organize and discover modules, facilitating extension and integration. The next section, [Pipeline Layer](04_pipeline_layer.md), builds upon these abstractions to compose complete workflows from individual modules.
