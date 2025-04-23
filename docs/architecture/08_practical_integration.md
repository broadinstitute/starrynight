# Connecting the Layers: A Practical Walkthrough of the StarryNight Architecture

This document provides a concrete example of how StarryNight's architectural layers work together in practice by examining the `exec_pcp_generic_pipe.py` file. While the previous documents explain each architectural layer conceptually, this walkthrough shows how these components integrate in a real workflow.

!!!note "Pedagogical Approach"
    This document deliberately uses the step-by-step implementation in `exec_pcp_generic_pipe.py` to clearly demonstrate individual components and their interactions. For production use, the more concise pattern in `exec_pcp_generic_full.py` (which composes all modules at once using the `create_pcp_generic_pipeline` function) is typically preferred.

## Why This Example Matters

The `exec_pcp_generic_pipe.py` file demonstrates:

1. How modules connect to form a complete pipeline
2. How configuration flows through the system
3. How the execution layer runs workflows
4. The patterns you'll encounter when extending StarryNight

By understanding this example, you'll be able to navigate the codebase more effectively and implement your own solutions.

## Pipeline at a Glance

The PCP Generic pipeline processes cell painting data through a series of steps:

1. Generate inventory and index
2. Calculate illumination correction (CP)
3. Apply illumination correction (CP)
4. Segmentation check (CP)
5. Calculate illumination correction (SBS)
6. Apply illumination correction (SBS)
7. Preprocess (SBS)
8. Analysis

Each step follows a consistent pattern that reflects the module layer's organization:
- Generate load data (configuration data for CellProfiler)
- Generate pipeline file (CellProfiler pipeline definition)
- Execute the pipeline (running CellProfiler)

## Configuration Setup (Lines 19-120)

The first section establishes three key configurations:

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

- `DataConfig` defines input/output paths for the entire pipeline
- `SnakeMakeBackend` provides the execution environment
- These configurations will be reused across all modules

## Pipeline Initialization (Lines 121-169)

Before running algorithm-specific modules, the pipeline needs two foundational components:

1. **Inventory** - Catalogs available data files
2. **Index** - Builds a queryable index of experimental data

```python
# Generate inventory
gen_inv_mod = GenInvModule.from_config(data_config)
exec_backend = SnakeMakeBackend(
    gen_inv_mod.pipe, backend_config, exec_runs / "run001", exec_mounts
)
run = exec_backend.run()
run.wait()

# Generate index
gen_ind_mod = GenIndexModule.from_config(data_config)
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

## Experiment Configuration (Lines 128-147)

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
    sbs_nuclei_channel="DAPI",
    sbs_cell_channel="PhalloAF750",
    sbs_mito_channel="ZO1AF488",
)
pcp_experiment = PCPGeneric.from_index(index_path, pcp_exp_init.model_dump())
```

**What developers should note:**

- `PCPGenericInitConfig` is a Pydantic model that validates experiment parameters
- Channel names (DAPI, PhalloAF750, etc.) configure which image channels to use for specific purposes
- Acquisition settings (SNAKE, ROUND) define how the microscope captured the images
- The `from_index` method loads data from the index and configures the experiment
- This configuration will drive all subsequent module behavior without requiring repetitive parameter specification

## Anatomy of a Pipeline Step (Lines 177-228)

Let's examine one complete step (CP calculate illumination):

```python
# 1. Generate load data
cp_calc_illum_load_data_mod = CPCalcIllumGenLoadDataModule.from_config(
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

# 2. Generate pipeline file
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

# 3. Execute pipeline
cp_calc_illum_invoke_mod = CPCalcIllumInvokeCPModule.from_config(
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

**What developers should note:**

- Each step follows the same three-phase pattern
- Module names follow a consistent naming convention
- The same configuration is used across phases
- Each module is independently executable
- Results from earlier phases are found automatically by later phases

## Architecture in Action

Looking at this example, we can see how all the architecture layers work together:

1. **Algorithm Layer**: Contains pure functions that implement image processing operations, which are called by CLI commands
2. **CLI Layer**: Provides command-line tools that modules invoke in containerized environments
3. **Module Layer**: Defines standardized components (like `CPCalcIllumInvokeCPModule`) with specifications and compute graphs that invoke CLI commands
4. **Pipeline Layer**: In this example, we're executing modules one by one, but they can be composed into a complete pipeline as seen in `create_pcp_generic_pipeline`
5. **Execution Layer**: `SnakeMakeBackend` translates module compute graphs into Snakemake rules and executes them in containers
6. **Configuration Layer**: `DataConfig` and experiment configuration drive behavior across all layers

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

This registry enables:
- Runtime discovery of available modules
- Dynamic instantiation based on configuration
- Integration with experiment classes
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
        cmd=["starrynight", "cp", "-p", spec.inputs[0].path, ...],
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

While this document focuses on executing modules one by one, StarryNight provides a more elegant composition approach through the `create_pcp_generic_pipeline` function:

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

When implementing your own algorithms or modules, follow these patterns:

1. **Module Structure**: Separate your functionality into three phases:
   - Data preparation (load_data)
   - Pipeline generation (cppipe)
   - Execution (invoke)

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

1. Find the module implementations in `modules/`
2. Update the module's `.from_config()` method to handle new configurations
3. Modify the container configuration and CLI command construction
4. Update the pipeline composition function if needed

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
