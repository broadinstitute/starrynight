# Architecture Flow in Action: Detailed Code Examples

This document provides concrete code examples showing how data flows through StarryNight's architectural layers. It complements the [Architecture Overview](00_architecture_overview.md#data-and-control-flow) by mapping the abstract sequence diagrams to actual code implementation, and builds on the foundational concepts from the [Practical Integration](08_practical_integration.md) walkthrough.

## Purpose of This Document

While the architecture overview explains the conceptual flow and the practical integration document shows the overall structure of a pipeline, this document:

1. **Maps Diagrams to Code**: Shows exactly how each arrow in the sequence diagrams maps to concrete code
2. **Demonstrates Transformations**: Illustrates how data transforms at each step between layers
3. **Provides Implementation Details**: Goes deeper into the technical implementation of each layer
4. **Shows Two-Phase Flow**: Demonstrates how the Pipeline Composition and Runtime Execution phases work in practice

By studying this document, you'll gain a precise understanding of how StarryNight's architectural components interact in a real implementation.

## Tracing a Single Pipeline Step

We'll trace a single pipeline step (CP illumination calculation) through the complete architecture flow, showing exactly how data transforms at each step between layers.

## Pipeline Composition Phase

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

## Runtime Execution Phase

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

## Flow Patterns in Three-Phase Execution

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

When using the pipeline composition approach shown in the "Pipeline Composition (Alternative Approach)" section in the [Practical Integration](08_practical_integration.md) document, this flow becomes more explicit since modules are composed in advance rather than executed one by one.

## CLI Layer as the Bridge Between Container and Algorithm

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