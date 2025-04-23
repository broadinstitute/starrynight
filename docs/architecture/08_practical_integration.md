# Connecting the Layers: A Practical Walkthrough of the StarryNight Architecture

This document provides a concrete example of how StarryNight's architectural layers work together in practice by examining the `exec_pcp_generic_pipe.py` file. While the previous documents explain each architectural layer conceptually, this walkthrough shows how these components integrate in a real workflow.

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

For a detailed mapping between the [architecture overview's two-phase sequence diagrams](00_architecture_overview.md#data-and-control-flow) and this concrete implementation, see the [appendix](#appendix-detailed-architecture-flow-mapping) at the end of this document.

## Pipeline at a Glance

The PCP Generic pipeline processes optical pooled screening data through a series of steps:

1. Generate inventory and index
2. Calculate illumination correction (CP)
3. Apply illumination and align (CP)
4. Segmentation check (CP)
5. Calculate illumination correction (SBS)
6. Apply illumination and align (SBS)
7. Preprocess (SBS)
8. Analysis

Each step in this example follows a CellProfiler-specific three-phase pattern (see [Anatomy of a Pipeline Step](#anatomy-of-a-pipeline-step-lines-177-228) for details on this pattern):

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

!!!note "CellProfiler Integration Pattern"
    The three-phase pattern described below (Generate Load Data → Generate Pipeline File → Execute Pipeline) is specific to how StarryNight integrates with CellProfiler. This pattern isn't a requirement of the StarryNight architecture, but rather a practical approach for this particular integration. Other tools may use different patterns while still adhering to the module abstraction.

With the experiment configured, we can now examine one complete pipeline step (CP calculate illumination). Each step follows a consistent three-phase pattern:

### Phase 1: Generate Load Data

First, a module generates the LoadData CSV file that tells CellProfiler which images to process:

```python
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

Finally, a module runs the pipeline on the data:

```python
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

This module finds both the LoadData file and the pipeline file created in the previous phases, then executes the pipeline with CellProfiler inside a container.

**What developers should note:**

- Each step follows the same three-phase pattern across all pipeline steps
- Module names follow a consistent naming convention (Load → CPipe → Invoke)
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

While this document focuses on executing modules one by one, StarryNight provides a more elegant pipeline composition approach (focused on the Pipeline Composition Phase) through the `create_pcp_generic_pipeline` function:

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
    This section focuses on extending StarryNight with new **modules** rather than new algorithms. Modules provide standardized interfaces to existing algorithms, whether those algorithms are part of StarryNight's core or from external tools.

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

One powerful capability of StarryNight's architecture is the ability to integrate external tools without modifying core algorithms. For example, to integrate Cellpose:

```python
# Define a module that uses Cellpose's existing CLI
class CellposeSegmentationModule(StarrynightModule):
    @staticmethod
    def uid() -> str:
        return "cellpose_segmentation"

    @classmethod
    def from_config(cls, data_config: DataConfig, experiment: Experiment):
        # Create container configuration that calls Cellpose CLI directly
        container = Container(
            name="cellpose_segment",
            input_paths={
                "image_dir": [...],
            },
            output_paths={
                "segmentation_dir": [...]
            },
            config=ContainerConfig(
                # Use a container with Cellpose pre-installed
                image="cellpose/cellpose:latest",
                # Call Cellpose CLI directly
                cmd=["python", "-m", "cellpose", "--dir", "${inputs.image_dir}", ...],
                env={},
            ),
        )

        # Create compute graph with just this container
        compute_graph = ComputeGraph([container])

        # Create and return module instance
        return cls(compute_graph)
```

This approach allows StarryNight to leverage existing tools by:

- Directly using their CLI interfaces rather than reimplementing algorithms
- Wrapping them in StarryNight's module abstraction for consistent workflow integration
- Using containerization to ensure reproducibility and isolation
- Potentially using Bilayers specs directly, allowing integration with modules from other systems

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

## Appendix: Detailed Architecture Flow Mapping

The following appendix provides a detailed mapping between the [architecture overview's two-phase sequence diagrams](00_architecture_overview.md#data-and-control-flow) and concrete code implementation. This section traces a single pipeline step (CP illumination calculation) through the complete architecture flow, showing exactly how data transforms at each step.

### Pipeline Composition Phase

### Config→Module: Configuration flows into module

```python
# Configuration setup
data_config = DataConfig(
    dataset_path=dataset_path,
    storage_path=dataset_path,
    workspace_path=workspace_path,
)

pcp_exp_init = PCPGenericInitConfig(
    cp_nuclei_channel="DAPI",
    # other parameters...
)

# Configuration flows into module
cp_calc_illum_load_data_mod = CPCalcIllumGenLoadDataModule.from_config(
    data_config, pcp_experiment
)
```

**What happens**: Configuration parameters flow into module creation
**Input → Output**: Parameters (paths, channels) → Module instance

### Module→Module: Generate compute graphs

```python
# Inside from_config method (not visible in example)
# This happens within the module's initialization
compute_graph = ComputeGraph([container])
return cls(compute_graph)
```

**What happens**: Module internally generates compute graph with container specification
**Input → Output**: Configuration → Compute graph with inputs/outputs

### Module→Pipeline: Pass module specifications

```python
# Module pipe passed to backend
exec_backend = SnakeMakeBackend(
    cp_calc_illum_load_data_mod.pipe,
    backend_config,
    exec_runs / "run003",
    exec_mounts,
)
```

**What happens**: Module's compute graph becomes available to pipeline/execution
**Input → Output**: Module compute graph → Pipeline component

### Pipeline→Execution: Submit workflow

```python
# Alternative approach shows this more clearly
return module_list, Seq(
    [
        Parallel(
            [
                Seq([cp_illum_calc_loaddata.pipe, ...]),
                # other parallel sequences
            ]
        ),
        # sequential steps
    ]
)

# In step-by-step approach:
run = exec_backend.run()
```

**What happens**: Pipeline submits workflow for execution
**Input → Output**: Pipeline specification → Execution plan

### Execution→Execution: Translate to Snakemake rules

```python
# Inside SnakeMakeBackend.run() (not visible in example)
# Translates compute graph to Snakemake rules
```

**What happens**: Backend translates compute graph into Snakemake rules
**Input → Output**: Compute graph → Snakemake rules

### Execution→Runtime: Schedule container execution

This step transitions us from the Pipeline Composition Phase to the Runtime Execution Phase.

```python
# Container definition from modules/cp_illum_calc/calc_cp.py
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

**What happens**: Snakemake executes rules in container environment
**Input → Output**: Snakemake rule → Container execution

### Runtime Execution Phase

### Runtime→CLI→Algorithm: Command Execution Flow

When the container executes, the CLI layer bridges between runtime containers and algorithm functions:

```python
# Container definition invokes the starrynight CLI command
cmd=["starrynight", "cp", "-p", spec.inputs[0].path, "-l", spec.inputs[1].path,
     "-o", spec.outputs[0].path]
```

When this container executes:

1. The `starrynight` command invokes the main CLI entrypoint
2. The `cp` subcommand selects the specific command
3. The CLI parses arguments and validates paths
4. The CLI then calls the corresponding algorithm function:

```python
# Inside starrynight/cli/cp.py
@click.command("cp")
@click.option("-p", "--pipeline", required=True, type=click.Path(exists=True))
@click.option("-l", "--loaddata", required=True, type=click.Path(exists=True))
@click.option("-o", "--output-dir", required=True, type=click.Path())
def cp_command(pipeline, loaddata, output_dir):
    """Run CellProfiler on a pipeline with a loaddata file."""
    from starrynight.algorithms.cellprofiler import run_cellprofiler

    # Convert string paths to standardized path objects (simplified)
    pipeline_path = AnyPath(pipeline)
    loaddata_path = AnyPath(loaddata)
    output_path = AnyPath(output_dir)

    # CLI command translates parameters and calls algorithm function
    run_cellprofiler(
        pipeline_path=pipeline_path,
        loaddata_path=loaddata_path,
        output_dir=output_path
    )
```

This in turn calls the pure algorithm function:

```python
# Inside starrynight/algorithms/cellprofiler.py
def run_cellprofiler(pipeline_path, loaddata_path, output_dir):
    """Run CellProfiler with specified pipeline and load data."""
    # Prepare environment and input files
    prepare_input_files(loaddata_path)

    # Execute core CellProfiler functionality
    result = execute_cellprofiler_pipeline(pipeline_path, output_dir)

    # Post-process results if needed
    post_process_results(result, output_dir)

    return result
```

**What happens**: Container command invokes CLI, which parses arguments and calls algorithm
**Input → Output**: Container command line → CLI argument parsing → Algorithm function call → Processing results

This three-layer approach (Container→CLI→Algorithm) provides several benefits:
1. Algorithms remain pure functions without CLI or container dependencies
2. CLI provides standardized interfaces and path handling
3. Modules can compose different CLI commands into complex workflows
4. The same algorithm can be invoked from different contexts (container, direct CLI, notebooks)

The CLI layer is the essential bridge that allows containerized execution to access the underlying algorithm functionality while maintaining clean separation of concerns.

**What happens**: Algorithm function executes core image processing logic
**Input → Output**: Function parameters → Processed data

### Algorithm→CLI: Return results to CLI

```python
# Continues from previous code block
def cp_command(pipeline, loaddata, output_dir):
    # Call algorithm and get results
    result = run_cellprofiler(
        pipeline_path=pipeline,
        loaddata_path=loaddata,
        output_dir=output_dir
    )

    # CLI handles results (logging, exit code, etc.)
    if result.success:
        click.echo(f"CellProfiler execution successful. Output in {output_dir}")
        return 0
    else:
        click.echo(f"CellProfiler execution failed: {result.error}")
        return 1
```

**What happens**: Algorithm function returns results to CLI command
**Input → Output**: Algorithm result → CLI output/exit code

### CLI→Runtime: CLI process completes

```python
# Container execution completes when CLI process exits
# Exit code from CLI determines container success/failure
```

**What happens**: CLI process exits, container execution completes
**Input → Output**: CLI exit code → Container exit status

### Runtime→Storage: Write results

```python
# Container writes to output paths
output_paths={
    "cp_illum_calc_dir": [workspace_path / "cp_illum_calc"]
}
```

**What happens**: Container processes execute CLI commands that write results
**Input → Output**: Container processing → Files on disk

### Storage→Runtime: Read previous outputs

```python
# Next module reads previous outputs
# (Not directly visible but implied in dependencies)
cp_calc_illum_cppipe_mod = CPCalcIllumGenCPPipeModule.from_config(
    data_config, pcp_experiment
)
```

**What happens**: Next phase reads outputs from previous phase
**Input → Output**: Files from previous step → Input for next step

### Flow Patterns in Three-Phase Execution

Each three-phase pattern (LoadData → CPipe → Invoke) demonstrates the complete flow through all architecture layers. These phases map to the two architectural phases as follows:

**Pipeline Composition Phase steps in each CellProfiler phase:**
1. Config→Module: Configuration flows into module
2. Module→Module: Generate compute graphs 
3. Module→Pipeline: Pass module specifications
4. Pipeline→Execution: Submit workflow
5. Execution→Execution: Translate to Snakemake rules

**Runtime Execution Phase steps in each CellProfiler phase:**
6. Execution→Runtime: Schedule container execution
7. Runtime→CLI: Invoke CLI commands
8. CLI→Algorithm: Call algorithm functions
9. Algorithm→Storage: Write results

The three CellProfiler-specific phases each execute this full cycle but with different inputs/outputs:

1. **LoadData Phase**:
    - Pipeline Composition: Configuration flows into module through to Snakemake rules
    - Runtime Execution: Container executes, CLI generates LoadData CSV
    - Result: CSV file written to disk
2. **CPipe Phase**:
    - Pipeline Composition: Same flow but with new module
    - Runtime Execution: Container executes, reads LoadData CSV, CLI generates pipeline
    - Result: Pipeline file written to disk
3. **Invoke Phase**:
    - Pipeline Composition: Same flow but with new module
    - Runtime Execution: Container executes, reads both CSV and pipeline file, CLI invokes algorithm
    - Result: Processed data written to disk

When using the pipeline composition approach shown in the "Pipeline Composition (Alternative Approach)" section, this flow becomes more explicit since modules are composed in advance rather than executed one by one.

### CLI Layer as the Bridge Between Container and Algorithm

The CLI layer serves as a critical bridge between the containerized execution environment and the pure algorithm functions:

```python
# In container definition
cmd=["starrynight", "cp", "-p", "${inputs.cppipe_path}",
     "-l", "${inputs.load_data_path}",
     "-o", "${outputs.cp_illum_calc_dir}"]

# Inside CLI implementation (starrynight/cli/main.py)
@click.group()
def cli():
    """StarryNight CLI."""
    pass

cli.add_command(cp.cp_command, name="cp")
# Other commands...

# Inside algorithm module (starrynight/algorithms/cellprofiler.py)
def run_cellprofiler(pipeline_path, loaddata_path, output_dir):
    """
    Run CellProfiler with the specified pipeline and loaddata.

    This function encapsulates the core image processing logic.
    """
    # Algorithm implementation
```

**What happens**:
1. Container executes the `starrynight cp` command with inputs/outputs
2. CLI parses arguments and provides a standardized interface to algorithms
3. Algorithm functions contain pure implementation without CLI/container concerns

**Benefits of this approach**:
- **Separation of concerns**: Algorithms focus on core functionality without UI/execution details
- **Testability**: Pure algorithm functions can be tested independently from CLI/containers
- **Flexibility**: Same algorithms can be accessed through different interfaces (CLI, API, notebook)
- **Composability**: CLI commands can combine multiple algorithm functions in useful ways
- **Containerization**: CLI provides a standard entrypoint for container execution

This CLI layer pattern is consistent across all StarryNight modules, creating a clean separation between:
- **Algorithm layer**: Pure implementation of image processing functionality
- **CLI layer**: Command-line interfaces that parse arguments and call algorithms
- **Module layer**: Compute graph specifications that invoke CLI commands in containers

When extending StarryNight with new capabilities, maintaining this separation through well-defined CLI interfaces ensures that algorithms remain reusable across different execution contexts.
