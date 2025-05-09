# Workflow Implementation Guide

This guide provides step-by-step instructions for implementing new workflows in StarryNight.

## What is a Workflow?

In the context of StarryNight, a **workflow** refers to a specific scientific image processing sequence implemented using StarryNight modules. Workflows are flexible and can be implemented in different ways:

1. **Step-by-step implementation**: As seen in `exec_pcp_generic_pipe.py`, where modules are individually created and executed in sequence, allowing for inspection of intermediate results.

2. **Pipeline composition**: As seen in `exec_pcp_generic_full.py`, where modules are connected into a StarryNight pipeline that can be executed as a single unit, potentially with parallel operations.

Both approaches are valid ways to implement workflows, with the pipeline composition approach being more concise and efficient for production use, while the step-by-step approach provides more visibility and control for development and debugging.

## Implementation as Creation and Modification

In practice, implementing a workflow in StarryNight rarely means starting from scratch. Most researchers begin with an existing workflow (like those in our reference implementations) and modify it to suit their specific needs. This guide addresses both aspects of implementation:

- **Modifying existing workflows**: Making changes to established workflows, from simple parameter adjustments to significant restructuring
- **Creating new workflows**: Building workflows by combining existing modules in new ways or developing entirely new modules

The skills for both overlap significantly, and many researchers progress from making small modifications to creating entirely custom workflows as their expertise grows. Throughout this guide, we'll address both scenarios, recognizing that implementation typically involves elements of both creation and modification.

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

## Choosing an Implementation Approach

Both implementation approaches can create the same workflows, but they have different strengths that make them suitable for different scenarios:

### Step-by-Step Approach

**Best for development, debugging, and learning:**

- Provides maximum visibility into intermediate results
- Allows inspection of outputs between steps
- Simplifies debugging by isolating failures to specific modules
- Makes the data flow more explicit

**Example use case:** When implementing a new workflow for the first time or troubleshooting issues with specific modules

### Pipeline Composition Approach

**Best for production use and complex execution patterns:**

- More concise implementation with less boilerplate code
- Enables parallel execution of independent operations
- Provides a clearer view of the entire workflow structure
- Better represents dependencies between modules

**Example use case:** When implementing a proven workflow for production use or when optimizing performance with parallel execution

## Common Implementation Scenarios

The following scenarios apply to both modifying existing workflows and creating new ones. Whether you're adapting a reference implementation or building something new, these patterns will help you implement workflows effectively:

### Scenario 1: Simple Changes - CellProfiler Module Settings

As described in the "Simple Changes" section, you can modify CellProfiler pipelines without changing Python code. When working in this scenario:

1. Directly edit the CellProfiler pipeline (.cppipe) files
2. No Python workflow code changes are needed

For example, you can change module parameters or replace modules (such as switching from `IdentifyPrimaryObject` to `RunCellPose`) directly in the pipeline file. These changes will automatically be used the next time the workflow executes with no additional code changes required.


### Scenario 2: Moderate Changes - Experiment Configuration

As covered in the "Moderate Changes" section, this requires modifying the Python workflow code. For example, configuring different channels requires updating the experiment configuration in the `PCPGenericInitConfig` object:

```python
# Original experiment configuration with default channel mappings
pcp_exp_init = PCPGenericInitConfig(
    barcode_csv_path=barcode_csv_path,
    cp_acquisition_order=AcquisitionOrderType.SNAKE,
    cp_img_frame_type=ImageFrameType.ROUND,
    cp_img_overlap_pct=10,
    # Default channel mappings
    cp_nuclei_channel="DAPI",
    cp_cell_channel="PhalloAF750",
    cp_mito_channel="ZO1AF488",
    # SBS settings omitted for brevity
)

# Modified experiment configuration with different channel mappings
pcp_exp_init = PCPGenericInitConfig(
    barcode_csv_path=barcode_csv_path,
    cp_acquisition_order=AcquisitionOrderType.SNAKE,
    cp_img_frame_type=ImageFrameType.ROUND,
    cp_img_overlap_pct=10,
    # Updated channel mappings to match your dataset
    cp_nuclei_channel="Hoechst",    # Changed from DAPI
    cp_cell_channel="CellMask",     # Changed from PhalloAF750
    cp_mito_channel="MitoTracker",  # Changed from ZO1AF488
    # SBS settings omitted for brevity
)

# Initialize experiment with updated channel mappings
pcp_experiment = PCPGeneric.from_index(index_path, pcp_exp_init.model_dump())
```

After making these changes:

1. The LoadData module will automatically handle the new channel mappings when generating the LoadData CSV
2. When using automatically generated pipelines, they will adapt to include the channels with the new names
3. If using legacy pipelines, ensure they are designed to handle the differently named channels

The system is designed to flexibly adapt to channel configuration changes, and these modifications are isolated to the experiment configuration while affecting the entire workflow.

!!! note "Future Enhancement"
    This section will be updated when enhanced channel mapping capabilities are implemented. Currently, only specific channel mappings (nuclei, cell, mito) are configurable, but future versions will support more flexible mapping of any channel type.

### Scenario 3: Moderate Changes - Module Arrangement

Another moderate change involves modifying the arrangement of modules in the Python workflow code. Here we'll focus on the step-by-step implementation approach, while noting how these changes would translate to the pipeline composition approach.

#### Step-by-Step Implementation Approach

1. **Adding a module**:
      - Import the new module class
      - Create an instance using its `from_config()` method, connecting to outputs from preceding modules
        ```python
        from starrynight.modules.new_module import NewModule

        # Connect the new module to outputs from an existing module
        new_module = NewModule.from_config(
            data_config,
            experiment,
            input_path=existing_module.outputs["output_path"]
        )
        ```
      - Set up execution with `SnakeMakeBackend(module.pipe, backend_config, run_dir, mounts)`
      - Run the module with `run = exec_backend.run()` and `run.wait()`

2. **Removing a module**:
      - Remove the module import statement (if no longer needed)
      - Remove the module creation code (`module = ModuleClass.from_config(...)`)
      - Remove the execution code (`exec_backend = SnakeMakeBackend(...)`, `run = exec_backend.run()`, etc.)
      - Update any dependent modules that used this module's outputs:
        ```python
        # Before removal - module_b depends on module_a's output
        module_b = ModuleB.from_config(data_config, experiment, input_path=module_a.outputs["output_path"])

        # After removal - module_b needs an alternative input source
        module_b = ModuleB.from_config(data_config, experiment, input_path=alternative_input_path)
        ```

3. **Reordering modules**:
      - Move the entire module creation and execution block to the desired position in your code
      - Ensure data dependencies are respected (modules must be executed after any modules they depend on)
      - Update input/output connections if necessary:
        ```python
        # Original order: A → B → C
        module_a = ModuleA.from_config(data_config, experiment)
        # Execute module_a...

        module_b = ModuleB.from_config(data_config, experiment, input=module_a.outputs["output"])
        # Execute module_b...

        module_c = ModuleC.from_config(data_config, experiment, input=module_b.outputs["output"])
        # Execute module_c...

        # Reordered to: A → C → B (assuming C doesn't depend on B)
        module_a = ModuleA.from_config(data_config, experiment)
        # Execute module_a...

        module_c = ModuleC.from_config(data_config, experiment, input=module_a.outputs["output"])
        # Execute module_c...

        module_b = ModuleB.from_config(data_config, experiment, input=module_a.outputs["output"])
        # Execute module_b...
        ```


#### How This Translates to Pipeline Composition

In the pipeline composition approach, these same changes would be implemented differently. Here's a simplified example based on the pipeline composition approach used in `exec_pcp_generic_full.py`:

```python
# Pipeline composition showing module arrangement
def create_custom_pipeline(data_config, experiment):
    # Define all modules in one place
    module_list = [
        # Create modules with connections between them
        module_a := ModuleA.from_config(data_config, experiment),
        module_b := ModuleB.from_config(data_config, experiment),
        module_c := ModuleC.from_config(data_config, experiment,
                                       input_path=module_a.outputs["output_path"]),
        # Add a new module connected to existing ones
        module_d := NewModule.from_config(data_config, experiment,
                                         input_path=module_b.outputs["output_path"])
    ]

    # Define execution pattern (sequential and parallel components)
    return module_list, Seq([
        # Sequential execution of A and B
        Seq([module_a.pipe, module_b.pipe]),
        # Then parallel execution of C and D (both depend on previous modules)
        Parallel([module_c.pipe, module_d.pipe])
    ])
```

Changes in the pipeline composition approach involve:

- **Adding or removing modules**: Update both the module list and the pipeline structure that defines execution flow
- **Reordering modules**: Change the arrangement in the `Seq` or `Parallel` composition structures
- **Module connections**: Still configured through the `from_config()` method parameters, but execution order is defined by the pipeline structure

The step-by-step reference implementation demonstrates these patterns throughout, with each module being configured based on the outputs of previous modules, creating a connected workflow.

## Advanced Implementation: Creating New Modules

!!! note "Work in Progress"
    The detailed documentation for creating new modules is under development and will be added in a future update. This section will cover Advanced Level 1 changes including:

    - Creating module classes that follow the StarryNight patterns
    - Defining module specifications with proper inputs and outputs
    - Implementing the required methods like `uid()` and `from_config()`
    - Registering modules in the module registry
    - Best practices for module development and testing

    In the meantime, refer to the [Practical Integration](../../architecture/08_practical_integration.md) document for some guidance on module structure, and examine existing modules in the codebase as reference implementations.

## Advanced Implementation: Resource Configuration

!!! note "Work in Progress"
    The detailed documentation for resource configuration is under development and will be added in a future update. This feature provides ways to specify compute resources (CPU cores, memory, GPU) at the module level, allowing for more efficient execution of resource-intensive tasks.

    This section will be expanded when the resource configuration API is finalized.

## References

- **StarryNight Architecture**: For more detailed information on the layers and their interactions, see the [Architecture Overview](../../architecture/00_architecture_overview.md)
- **Practical Integration**: The [Practical Integration](../../architecture/08_practical_integration.md) document explains the `exec_pcp_generic_pipe.py` implementation in detail
- **Architecture Flow**: The [Architecture Flow in Action](../../architecture/09_architecture_flow_example.md) document shows how data flows through all architectural layers
- **Reference Implementations**: Two complementary implementations:
  - `starrynight/notebooks/pypct/exec_pcp_generic_pipe.py`: Step-by-step approach with individual module execution
  - `starrynight/notebooks/pypct/exec_pcp_generic_full.py`: Pipeline composition approach for concise implementation
- **Module Registry**: Central registry for modules in `starrynight/modules/registry.py`
- **Pipeline Composition**: Functions for creating complete pipelines in `starrynight/pipelines/`
