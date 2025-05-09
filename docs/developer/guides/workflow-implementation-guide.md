# Workflow Implementation Guide

This guide provides step-by-step instructions for implementing new workflows in StarryNight.

## What is a Workflow?

In the context of StarryNight, a **workflow** refers to a specific scientific image processing sequence implemented using StarryNight modules. Workflows are flexible and can be implemented in different ways:

1. **Step-by-step implementation**: As seen in `exec_pcp_generic_pipe.py`, where modules are individually created and executed in sequence, allowing for inspection of intermediate results.

2. **Pipeline composition**: As seen in `exec_pcp_generic_full.py`, where modules are connected into a StarryNight pipeline that can be executed as a single unit, potentially with parallel operations.

Both approaches are valid ways to implement workflows, with the pipeline composition approach being more concise and efficient for production use, while the step-by-step approach provides more visibility and control for development and debugging.

## Understanding Workflow Flexibility

StarryNight is designed with flexibility in mind, allowing researchers to create and modify workflows at different levels of complexity. Depending on your needs, you can:

### Simple Changes (No Code Required)

These changes involve internal modifications to CellProfiler pipelines that are wrapped by StarryNight modules, without requiring any Python code changes:

- **Change CellProfiler Modules**: Replace one CellProfiler module with another inside a pipeline file (e.g., switching from `IdentifyPrimaryObject` to `RunCellPose` for segmentation)
- **Adjust Module Parameters**: Modify thresholds, filters, or measurement settings within the CellProfiler pipeline file

### Moderate Changes (Python Workflow Code)

These changes involve modifying the Python workflow code to adjust how modules are configured and connected:

- **Experiment Configuration Updates**: Modify channel mappings, experiment parameters, and module inputs in the workflow Python script
- **Module Input/Output Connections**: Change how modules' outputs are connected to other modules' inputs in the workflow code
- **Pipeline Composition**: Alter the order and arrangement of modules in the pipeline definition

### Advanced Changes (Code Required)

Advanced changes can be divided into two levels of complexity:

#### Advanced Level 1 (Module Development)

This guide covers these changes, which involve extending the system while working within the existing architecture:

- **Add New Modules**: Create entirely new modules for custom processing steps
- **Implement Custom Resource Configurations**: Specify compute resources at the task level for performance optimization
- **Integrate External Tools**: Connect new external processing tools while maintaining the module interface pattern

#### Advanced Level 2 (Core Architecture Development)

These changes are beyond the scope of this workflow implementation guide, as they involve modifying the core architecture itself:

- **Modify Execution Engine**: Change how StarryNight executes workflows
- **Implement New Backends**: Add support for new execution environments
- **Create New Pipeline Patterns**: Develop new ways to compose and orchestrate pipelines
- **Develop Algorithm Libraries**: Build new algorithm foundations that integrate with the core system

## Reference Implementations

Throughout this guide, we'll reference two complementary practical implementations that demonstrate different approaches to workflow creation:

1. **Step-by-step approach**: `starrynight/notebooks/pypct/exec_pcp_generic_pipe.py` - Implements each module individually with explicit execution of each step, providing maximum visibility and control

2. **Pipeline composition approach**: `starrynight/notebooks/pypct/exec_pcp_generic_full.py` - Implements the same workflow using the pipeline composition pattern for a more concise implementation

Both implementations are explained in detail in the [Practical Integration](../../architecture/08_practical_integration.md) architecture document.

The step-by-step implementation demonstrates the complete PCP Generic pipeline workflow with the following steps:

1. Generate inventory and index
2. Calculate illumination correction (CP)
3. Apply illumination and align (CP)
4. Segmentation check (CP)
5. Calculate illumination correction (SBS)
6. Apply illumination and align (SBS)
7. Preprocess (SBS)
8. Analysis

Each step follows a consistent three-phase pattern for CellProfiler integration:

- Generate load data (configuration data for CellProfiler)
- Generate pipeline file (CellProfiler pipeline definition)
- Execute the pipeline (running CellProfiler)

Rather than duplicating all the code examples here, we'll focus on explaining the key concepts and scenarios for implementing and modifying workflows, with references to the existing examples where appropriate.

## Key Workflow Components

Workflows in StarryNight are built from several key components that work together:

### Data Configuration
The `DataConfig` object defines paths for input data, storage, and workspace. It configures where the pipeline will look for input data and where it will store outputs and intermediate files. This configuration is used throughout the pipeline.

### Execution Backend
The execution backend (typically `SnakeMakeBackend`) handles running the pipeline. It translates module definitions into executable operations and manages their execution, including scheduling, parallelization, and resource allocation.

### Experiment Configuration
The experiment configuration contains metadata about your dataset and processing settings, including:

- Acquisition settings (order, frame type, overlap percentage)
- Channel mappings (which microscope channels correspond to nucleus, cell, and mitochondria)
- Other experiment-specific parameters

This configuration drives all subsequent module behavior without requiring repetitive parameter specification.

### Modules
Modules are the building blocks of workflows. Each module:

- Is configured via its `from_config()` method
- Produces a "pipe" that's executed by the backend
- Has defined inputs and outputs
- May require outputs from previous modules
- Is executed in a containerized environment

## Example Workflow Implementations

Looking at the reference implementations, we can see both simple and complex workflows in action:

### Simple Workflow Pattern

The simplest workflow pattern involves:

1. Setting up basic configurations (data, execution, experiment)
2. Creating modules one by one using their `from_config()` methods
3. Executing each module in sequence, waiting for completion before continuing

Each module in the PCP Generic pipeline follows a three-phase pattern specific to CellProfiler integration:

1. Generate LoadData - Creates configuration data for CellProfiler
2. Generate Pipeline - Creates the CellProfiler pipeline definition
3. Execute Pipeline - Runs CellProfiler with the generated files

### Complex Workflow Pattern

For more complex workflows, the `exec_pcp_generic_full.py` example demonstrates pipeline composition capabilities through the `create_pcp_generic_pipeline` function, which is particularly helpful when dealing with complex workflows:

- Creates all modules in one place
- Composes them into a pipeline with parallel execution
- Enables complex execution patterns (parallel processing of independent steps)
- Provides a more concise implementation for production use

## Common Workflow Modification Scenarios

### Scenario 1: Change CellProfiler Module Settings

If you want to replace one CellProfiler module with another (for example, switching from CellProfiler's `IdentifyPrimaryObject` to `RunCellPose` for segmentation):

#### Using a custom CellProfiler pipeline

  - Create your custom CellProfiler pipeline file with the different module
  - Skip the pipeline generation step in the workflow
  - Pass your custom pipeline file directly to the invoke module

In the reference implementation, you would modify the segmentation step (Step 3: CP segcheck) by:

  - Running the LoadData generation phase for CP segcheck
  - Skipping the CPPipe generation phase
  - Creating your own custom CellProfiler pipeline file
  - Modifying the invoke phase to use your custom pipeline

### Scenario 2: Add New Channel

Adding a new channel requires updating the experiment configuration in the `PCPGenericInitConfig` object in the experiment configuration section of the reference implementation:

1. Update the experiment configuration with the new channel mapping
2. The LoadData module will automatically handle the new channel when generating the LoadData CSV
3. When using automatically generated pipelines, they will adapt to include the new channel
4. If using legacy pipelines, ensure they are designed to handle the additional channel

The system is designed to flexibly adapt to different numbers of channels, and the changes are isolated to the experiment configuration.

### Scenario 3: Add/Remove/Reorder Modules

To change the arrangement of modules in a workflow:

1. **Adding a module**:
      - Import the new module class
      - Create an instance using its `from_config()` method
      - Connect its inputs to outputs from preceding modules
      - Add it to your pipeline composition
2. **Removing a module**:
      - Simply omit it from your pipeline composition
      - Ensure any dependent modules are either removed or reconfigured
3. **Reordering modules**:
      - Change the order in your pipeline composition
      - Update input/output connections to maintain data flow
4. **Creating modules with interconnected inputs/outputs**:
      - Access a module's outputs via its `outputs` dictionary
      - Pass these as parameters when configuring dependent modules
      - Example: `module_b = ModuleB.from_config(data_config, experiment, input_path=module_a.outputs["output_path"])`

The reference implementation demonstrates these patterns throughout, with each module being configured based on the outputs of previous modules, creating a connected workflow.

## Creating New Modules

To create a new module for your workflow:

```python
from starrynight.modules.base import StarrynightModule
from starrynight.modules.specs import SpecContainer, TypeInput, TypeOutput, TypeEnum
from starrynight.config import DataConfig
from starrynight.experiments import Experiment

class YourModuleClass(StarrynightModule):
    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "your_module_unique_id"

    @staticmethod
    def _spec() -> SpecContainer:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="input_path",
                    type=TypeEnum.files,
                    description="Path to input files",
                    optional=False,
                ),
            ],
            outputs=[
                TypeOutput(
                    name="output_path",
                    type=TypeEnum.files,
                    description="Path for output files",
                    optional=False,
                ),
            ],
        )

    @classmethod
    def from_config(cls, data_config: DataConfig, experiment: Experiment, spec=None):
        """Create module from configuration."""
        # Use default spec if none provided
        if spec is None:
            spec = cls._spec()

        # Update paths based on data config
        spec.update_paths(data_config)

        # Define the pipeline
        pipe = create_your_module_pipe(spec, data_config, experiment)

        # Create and return module instance
        return cls(spec, pipe, [])

# Register your module in the registry
# In starrynight/modules/registry.py:
MODULE_REGISTRY: dict[str, StarrynightModule] = {
    # Existing modules...
    YourModuleClass.uid(): YourModuleClass,
}
```

## Resource Configuration

Resource configuration for modules is in development. The approach uses a "unit of work" concept:

```python
# Future API for resource configuration (work in progress)
class YourModuleWithResources(StarrynightModule):
    # ... other methods ...

    @classmethod
    def from_config(cls, data_config: DataConfig, experiment: Experiment, spec=None):
        # ... setup code ...

        # Define the pipeline with resource requirements
        pipe = create_your_module_pipe(
            spec,
            data_config,
            experiment,
            resources={
                "cpu": 2,       # 2 CPU cores
                "memory": 4096,  # 4 GB RAM
                "gpu": 0,       # No GPU
            }
        )

        # ... rest of the method ...
```

The executor will use these resource hints to make scheduling decisions, but the end user doesn't need to manage resources directly.

## References

- **StarryNight Architecture**: For more detailed information on the layers and their interactions, see the [Architecture Overview](../../architecture/00_architecture_overview.md)
- **Practical Integration**: The [Practical Integration](../../architecture/08_practical_integration.md) document explains the `exec_pcp_generic_pipe.py` implementation in detail
- **Architecture Flow**: The [Architecture Flow in Action](../../architecture/09_architecture_flow_example.md) document shows how data flows through all architectural layers
- **Reference Implementations**: Two complementary implementations:
  - `starrynight/notebooks/pypct/exec_pcp_generic_pipe.py`: Step-by-step approach with individual module execution
  - `starrynight/notebooks/pypct/exec_pcp_generic_full.py`: Pipeline composition approach for concise implementation
- **Module Registry**: Central registry for modules in `starrynight/modules/registry.py`
- **Pipeline Composition**: Functions for creating complete pipelines in `starrynight/pipelines/`
