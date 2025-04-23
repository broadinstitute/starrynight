# Connecting the Layers: A Practical Walkthrough of the StarryNight Architecture

This document provides a concrete example of how StarryNight's architectural layers work together in practice by examining the `exec_pcp_generic_pipe.py` file. While the previous documents explain each architectural layer conceptually, this walkthrough shows how these components integrate in a real workflow.

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

Each step follows a consistent pattern:
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

1. **Algorithm Layer**: `CPCalcIllumInvokeCPModule` implements the illumination calculation algorithm
2. **Module Layer**: Each module handles a specific phase (load_data, cppipe, cp)
3. **Pipeline Layer**: `pcp_experiment` defines the pipeline configuration and sequence
4. **Execution Layer**: `SnakeMakeBackend` executes each pipeline step
5. **Configuration Layer**: `DataConfig` and experiment configuration drive behavior

## Extension Patterns

When implementing your own algorithms or modules, follow these patterns:

1. **Module Structure**: Separate your functionality into three phases:
   - Data preparation (load_data)
   - Pipeline generation (cppipe)
   - Execution (invoke)

2. **Configuration**: Extend existing configuration classes or create new ones using Pydantic models

3. **Pipeline Integration**: Register your modules with the appropriate experiment classes

## Common Development Tasks

Here are examples of common tasks and how to approach them:

### Adding a New Algorithm

1. Create modules (load_data, cppipe, invoke) in a new directory under `modules/`
2. Implement the algorithm in `algorithms/`
3. Extend experiment configuration to include your algorithm's parameters
4. Register your modules with experiments that should use them

### Modifying an Existing Pipeline

1. Find the module implementations in `modules/`
2. Update the module's `.from_config()` method to handle new configurations
3. Modify the pipeline generation or execution as needed

## Debugging and Troubleshooting

When working with pipelines:

1. Check run logs using `run.print_log()`
2. Examine workspace output files after each step
3. The modular design lets you run steps individually to isolate issues
4. Use `.wait()` to ensure previous steps complete before continuing

## Key Takeaways

1. StarryNight follows a consistent, modular pattern for pipeline components
2. Configuration flows from top-level settings to specific module behavior
3. The execution layer abstracts away the details of running each pipeline step
4. Adding new capabilities follows established patterns with clear extension points

By understanding this concrete example, you now have a practical view of how StarryNight's architecture functions as an integrated system.
