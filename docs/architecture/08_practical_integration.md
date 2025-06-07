# Practical Integration: Connecting the StarryNight Architecture Layers

This document provides a concrete example of how StarryNight's architectural layers work together in practice by examining `exec_pcp_generic_pipe.py`, an example pipeline implementation file that demonstrates the PCP Generic workflow. While the [architecture overview](00_architecture_overview.md) and individual layer documents ([Algorithm](01_algorithm_layer.md), [CLI](02_cli_layer.md), [Module](03_module_layer.md), [Pipeline](04_pipeline_layer.md), [Execution](05_execution_layer.md), [Configuration](06_configuration_layer.md)) explain each architectural layer conceptually, this walkthrough shows how these components integrate in a real workflow.

!!!note "Pedagogical Approach"
    This document deliberately uses the step-by-step implementation in `exec_pcp_generic_pipe.py` to clearly demonstrate individual components and their interactions. This approach:

    - Allows researchers to inspect intermediate results between pipeline stages
    - Matches biological research workflows where verification at each stage is crucial
    - Provides clearer visibility into how components operate independently

    For production use, the more concise pattern in `exec_pcp_generic_full.py` (which composes all modules at once using the `create_pcp_generic_pipeline` function) is typically preferred.

## Why This Example Matters

The `exec_pcp_generic_pipe.py` file demonstrates:

1. How configuration parameters flow from experiment setup to module execution
2. How modules encapsulate different functional steps in the pipeline
3. How the execution layer transforms abstract workflows into concrete container invocations
4. How StarryNight's layered architecture enables reproducible scientific workflows

This example serves as a practical bridge between the conceptual architecture and its real-world implementation. By understanding this workflow, you'll gain insights into:

- How to extend the system with your own modules and algorithms
- The rationale behind StarryNight's design decisions
- Patterns for creating maintainable, containerized scientific pipelines

For a detailed mapping between the [architecture overview's two-phase sequence diagrams](00_architecture_overview.md#data-and-control-flow) and this concrete implementation, see the [Architecture Flow in Action](09_architecture_flow_example.md) document.

## Pipeline at a Glance

The PCP Generic pipeline processes optical pooled screening data through a series of steps:

1. Generate inventory and index
2. Calculate illumination correction (CP-Cell Painting images)
3. Apply illumination and segment (CP)
4. Segmentation check (CP)
5. Calculate illumination correction (SBS-Sequencing by Synthesis images)
6. Apply illumination and align (SBS)
7. Preprocess (SBS)
8. Analysis

Each of the eight pipeline steps follows a CellProfiler-specific three-phase pattern (see [Anatomy of a Pipeline Step](#anatomy-of-a-pipeline-step) for details on this pattern):

- Generate load data (configuration data for CellProfiler)
- Generate pipeline file (CellProfiler pipeline definition)
- Execute the pipeline (running CellProfiler)

## Configuration Setup

The first section establishes two key configurations:

```python
# Data configuration (Configuration Layer)
data_config = DataConfig(
    dataset_path=dataset_path,
    storage_path=dataset_path,
    workspace_path=workspace_path,
)

# Execution engine config (Execution Layer)
backend_config = SnakeMakeConfig(
    use_fluent_bit=False, print_exec=True, background=False
)
```

**What developers should note:**

- `DataConfig` is a Python class that defines input/output paths for the entire pipeline
- `SnakeMakeBackend` provides the execution environment
- These configurations will be reused across all modules
- The actual experiment configuration (as a Python object) is created later after building the index

## Pipeline Initialization

Before running algorithm-specific modules, the pipeline needs two foundational components:

1. **Inventory** - Catalogs available data files
2. **Index** - Builds a queryable index of experimental data

```python
# Generate inventory
gen_inv_mod = GenInvModule(data_config)
exec_backend = SnakeMakeBackend(
    gen_inv_mod.pipe, backend_config, exec_runs / "run001", exec_mounts
)
run = exec_backend.run()
run.wait()

# Generate index
gen_ind_mod = GenIndexModule(data_config)
exec_backend = SnakeMakeBackend(
    gen_ind_mod.pipe, backend_config, exec_runs / "run002", exec_mounts
)
run = exec_backend.run()
run.wait()
```

**What developers should note:**

- The `from_config()` pattern is consistent across modules
- Each module produces a "pipe" that's executed by the backend
- The experiment is initialized from the index using type-validated configuration

## Experiment Configuration

After building the index, the notebook configures the experiment using `PCPGenericInitConfig`:

```python
index_path = workspace_path / "index/index.parquet"
pcp_exp_init = PCPGenericInitConfig(
    barcode_csv_path=Path(),
    cp_acquisition_order=AcquisitionOrderType.SNAKE,
    cp_img_frame_type=ImageFrameType.ROUND,
    cp_img_overlap_pct=10,
    sbs_acquisition_order=AcquisitionOrderType.SNAKE,
    sbs_img_frame_type=ImageFrameType.ROUND,
    sbs_img_overlap_pct=10,
    cp_nuclei_channel="DAPI",
    cp_cell_channel="PhalloAF750",
    cp_mito_channel="ZO1AF488",
    cp_custom_channel_map={
        "DAPI": "DNA",
        "ZO1AF488": "ZO1",
        "PhalloAF750": "Phalloidin",
    },
    sbs_nuclei_channel="DAPI",
    sbs_cell_channel="PhalloAF750",
    sbs_mito_channel="ZO1AF488",
    sbs_custom_channel_map={
        "DAPI": "DNA",
        "A": "A",
        "T": "T",
        "G": "G",
        "C": "C",
    },
)
pcp_experiment = PCPGeneric.from_index(index_path, pcp_exp_init.model_dump())
```

**What developers should note:**

- `PCPGenericInitConfig` is a [Pydantic](https://docs.pydantic.dev/) model that validates experiment parameters
- Channel names (DAPI, PhalloAF750, etc.) configure which image channels to use for specific purposes
- Custom channel mappings (`cp_custom_channel_map`, `sbs_custom_channel_map`) translate microscope channel names to semantic biological names used in analysis pipelines
- Acquisition settings (SNAKE, ROUND) define how the microscope captured the images
- The `from_index` method loads data from the index and configures the experiment
- This configuration will drive all subsequent module behavior without requiring repetitive parameter specification

## Anatomy of a Pipeline Step

!!!note "CellProfiler Integration Pattern"
    The three-phase pattern described below (Generate Load Data → Generate Pipeline File → Execute Pipeline) is specific to how StarryNight integrates with CellProfiler. This pattern isn't a requirement of the StarryNight architecture, but rather a practical approach for this particular integration. Other tools may use different patterns while still adhering to the module abstraction.

With the experiment configured, we can now examine one complete pipeline step (CP calculate illumination). Each step follows a consistent three-phase pattern:

### Phase 1: Generate Load Data

First, a module generates the LoadData CSV file that tells CellProfiler which images to process:

```python
cp_calc_illum_load_data_mod = CPCalcIllumGenLoadDataModule(
    data_config, pcp_experiment
)
exec_backend = SnakeMakeBackend(
    cp_calc_illum_load_data_mod.pipe,
    backend_config,
    exec_runs / "run003",
    exec_mounts,
)
run = exec_backend.run()
run.wait()
```

Notice how the experiment configuration (`pcp_experiment`) is passed to the module, allowing it to access parameters like channel names that were defined earlier.

### Phase 2: Generate Pipeline File

Next, a module creates the CellProfiler pipeline definition (.cppipe file):

```python
cp_calc_illum_cppipe_mod = CPCalcIllumGenCPPipeModule.from_config(
    data_config, pcp_experiment
)
exec_backend = SnakeMakeBackend(
    cp_calc_illum_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run004",
    exec_mounts,
)
run = exec_backend.run()
run.wait()
```

This module automatically finds the LoadData file created in the previous phase and uses it to configure the pipeline.

### Phase 3: Execute Pipeline

Finally, a module runs the pipeline on the data (note that module names use "Invoke" but we refer to this as the "Execute" phase for clarity):

```python
cp_calc_illum_invoke_mod = CPCalcIllumInvokeCPModule(
    data_config, pcp_experiment
)
exec_backend = SnakeMakeBackend(
    cp_calc_illum_invoke_mod.pipe,
    backend_config,
    exec_runs / "run005",
    exec_mounts,
)
run = exec_backend.run()
run.wait()
```

This module finds both the LoadData file and the pipeline file created in the previous phases, then executes the pipeline with CellProfiler inside a container.

**What developers should note:**

- Each step follows the same three-phase pattern across all pipeline steps
- Module names follow a consistent naming convention (LoadData → CPipe → Invoke), though we refer to the third phase as "Execute" for clarity
- The same configuration (`data_config` and `pcp_experiment`) is used across all phases
- Each module is independently executable but automatically finds outputs from previous phases
- This pattern repeats for all eight pipeline steps, with variations in parameter specifics

## Architecture in Action

Looking at this example, we can see how all the architecture layers work together across the two main phases:

### Pipeline Composition Phase
1. **Configuration Layer**: `DataConfig` and experiment configuration drive behavior across all layers
2. **Module Layer**: Defines standardized components (like `CPCalcIllumInvokeCPModule`) with specifications and compute graphs
3. **Pipeline Layer**: In this example, we're executing modules one by one, but they can be composed into a complete pipeline as seen in `create_pcp_generic_pipeline`
4. **Execution Layer (design time)**: `SnakeMakeBackend` translates module compute graphs into Snakemake rules

### Runtime Execution Phase
5. **Execution Layer (runtime)**: Schedules container execution based on Snakemake rules
6. **Container Runtime**: Executes commands in isolated environments
7. **CLI Layer**: Provides command-line tools that parse arguments and call algorithms
8. **Algorithm Layer**: Contains pure functions that implement image processing operations

## Module Registry and Discovery

StarryNight uses a registry mechanism to organize and discover available modules. In the Module Registry (implemented in `starrynight/modules/registry.py`), each module is registered with a unique identifier:

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

!!!note "Integration with Broader System"
    The registry is not used in this example, but it serves as a critical integration point with other StarryNight components:

    - Enables **Conductor** to discover and invoke available modules dynamically
    - Allows **Canvas** to present available modules in its user interface
    - Provides extension hooks for integrating new capabilities without modifying core code

This registry enables:

- Runtime discovery of available modules
- Dynamic instantiation based on configuration
- Integration with experiment classes (like `PCPGeneric` that define workflow-specific configurations)
- Extension with new module types

When creating new modules, you must register them in this registry to make them discoverable within the system.

## Container Execution Model

Modules define containerized operations that are executed by the backend. The container configuration is defined as part of the module's compute graph:

```python
# From starrynight/modules/cp_illum_calc/calc_cp.py
Container(
    name="cp_calc_illum_invoke_cp",
    input_paths={
        "cppipe_path": [...],
        "load_data_path": [...],
    },
    output_paths={
        "cp_illum_calc_dir": [...]
    },
    config=ContainerConfig(
        image="ghrc.io/leoank/starrynight:dev",
        cmd=["starrynight", "cp", "-p", spec.inputs["cppipe_path"].value, ...],
        env={},
    ),
)
```

When executed:

1. The `SnakeMakeBackend` translates this container definition into a Snakemake rule
2. Snakemake executes the rule in the specified container
3. The CLI command runs inside the container, calling the underlying algorithm functions
4. Results are stored at the specified output paths

This containerization ensures reproducibility and isolation of each pipeline step.

## Pipeline Composition (Alternative Approach)

While this document focuses on executing modules one by one for clarity, StarryNight also supports composing all modules at once through the `create_pcp_generic_pipeline` function:

```python
# From starrynight/src/starrynight/pipelines/pcp_generic.py
def create_pcp_generic_pipeline(
    data: DataConfig,
    experiment: Experiment | None = None,
) -> tuple[list[StarrynightModule], Pipeline]:
    # Create all modules in one place
    module_list = [
        # cp modules
        cp_illum_calc_loaddata := init_module(CPCalcIllumGenLoadDataModule),
        cp_illum_calc_cpipe := init_module(CPCalcIllumGenCPPipeModule),
        cp_illum_calc_cp := init_module(CPCalcIllumInvokeCPModule),
        # More modules...
    ]

    # Compose modules into a pipeline with parallel execution
    return module_list, Seq(
        [
            Parallel(
                [
                    Seq([cp_illum_calc_loaddata.pipe, cp_illum_calc_cpipe.pipe, ...]),
                    Seq([sbs_illum_calc_loaddata.pipe, sbs_illum_calc_cpipe.pipe, ...]),
                ]
            ),
            analysis_loaddata.pipe,
            analysis_cpipe.pipe,
            analysis_cp.pipe,
        ]
    )
```

This approach enables complex parallel execution patterns, where CP and SBS processing can run simultaneously, with analysis running after both complete.

## Extension Patterns

When implementing your own modules, follow these patterns:

!!!note "Module vs. Algorithm Extension"
    This section focuses on extending StarryNight with new **modules** rather than new algorithms. Modules provide standardized interfaces to existing algorithms, whether those algorithms are part of StarryNight's core or from external tools. To add your own algorithms to StarryNight, see the ["Adding a New Algorithm"](#adding-a-new-algorithm) section below.

1. **Module Structure**: Consider your module's specific requirements:
      - For CellProfiler integrations, use the three-phase pattern shown earlier
      - For other tools, design appropriate module structures based on tool requirements
      - Ensure your modules have clear inputs, outputs, and containerized execution specifications
2. **Registry Integration**: Define a unique ID and register your module in the registry:
   ```python
   @staticmethod
   def uid() -> str:
       """Return module unique id."""
       return "your_module_unique_id"

   # Then add to MODULE_REGISTRY in registry.py
   ```

3. **Configuration**: Extend existing configuration classes or create new ones using Pydantic models

4. **Container Definition**: Define how your module should run in containers using the Container class

### External Tool Integration Without Algorithm Changes

One powerful capability of StarryNight's architecture is the ability to integrate external tools without modifying core algorithms:

```python
# Simplified example based on actual codebase patterns
class ExternalToolModule(StarrynightModule):
    @property
    def uid(self) -> str:
        return "external_tool_module"

    def _spec(self) -> SpecContainer:
        # Default specification
        return ExternalToolSpec()

    def _create_pipe(self) -> Pipeline:
        return Seq(
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

This approach allows StarryNight to leverage existing tools by:

- Directly using their CLI interfaces rather than reimplementing algorithms
- Wrapping them in StarryNight's module abstraction for consistent workflow integration
- Using containerization to ensure reproducibility and isolation
- Potentially using [Bilayers](https://github.com/bilayer-containers/bilayers) specifications directly (the external schema system StarryNight uses for module specifications), enabling integration with other Bilayers-compatible tools

## Common Development Tasks

Here are examples of common tasks and how to approach them:

### Adding a New Algorithm

1. Implement the algorithm functions in `algorithms/`
2. Create CLI commands that expose the algorithm in `cli/`
3. Create modules (load_data, cppipe, invoke) in a new directory under `modules/`
4. Register your modules in the `MODULE_REGISTRY`
5. Extend experiment configuration to include your algorithm's parameters
6. Update pipeline composition functions to include your modules

### Modifying an Existing Pipeline

To modify how a pipeline works, you typically need to:

1. **For changing module behavior**: Find the relevant module implementations in `modules/`
   - Update the module's `.from_config()` method to handle new configurations
   - Modify the container configuration and CLI command construction
2. **For changing pipeline structure**: Update the pipeline composition function (e.g., in `pipelines/pcp_generic.py`)
   - Add or remove modules from the composition
   - Change the execution order or parallelization strategy

## Debugging and Troubleshooting

When working with pipelines:

1. Check run logs using `run.print_log()`
2. Examine workspace output files after each step
3. Inspect the generated Snakefile in the working directory
4. The modular design lets you run steps individually to isolate issues
5. Use `.wait()` to ensure previous steps complete before continuing

## Key Takeaways

1. StarryNight follows a consistent, modular pattern for pipeline components
2. Modules invoke CLI commands in containers rather than directly implementing algorithms
3. The module registry enables discovery and composition of standardized components
4. Container execution ensures reproducibility and isolation
5. Pipeline composition enables complex parallel execution patterns
6. Configuration flows from top-level settings to specific module behavior

By understanding this concrete example, you now have a practical view of how StarryNight's architecture functions as an integrated system, from algorithms through CLI commands, modules, pipelines, and execution.

## Looking Deeper: Architecture Flow Details

For a detailed, code-level mapping between the architecture's sequence diagrams and this concrete implementation, see [Architecture Flow in Action](09_architecture_flow_example.md). This companion document:

- Traces a single pipeline step through all architectural layers
- Shows exactly how data transforms at each step
- Explains the relationship between the Pipeline Composition and Runtime Execution phases
- Provides concrete code examples for each step in the flow

The detailed flow examples will help you understand precisely how StarryNight's layered architecture translates into actual implementation code.
