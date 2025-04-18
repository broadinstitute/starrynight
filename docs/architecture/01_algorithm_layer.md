# StarryNight Algorithm Layer

!!! bug


## Overview

The algorithm layer forms the foundation of the StarryNight framework. Algorithms are pure Python functions that implement specific image processing operations and pipeline generation capabilities without dependencies on higher-level StarryNight components.

This document explains the structure and organization of the algorithm layer.

!!! note "CellProfiler Context"
    While many examples in this document reference CellProfiler-specific functions, the algorithm layer design extends beyond CellProfiler. The architecture supports various algorithm types including indexing, inventory management, and other non-CellProfiler operations as detailed in the "Beyond CellProfiler" section.

## Purpose

Algorithms in StarryNight serve several essential purposes:

1. **Image Processing Logic** - Implementing the core computational steps
2. **Pipeline Generation** - Creating CellProfiler pipeline files programmatically
3. **LoadData Creation** - Generating CSV files that tell CellProfiler how to load images
4. **Pipeline Execution** - Running processing steps on prepared data

By separating these functions from higher-level concerns like UI, execution environment, and workflow composition, the algorithm layer maintains simplicity and testability.

## CellProfiler LoadData Files

CellProfiler's LoadData module uses CSV files to specify which images to process and how to organize them. These CSV files (referred to as "LoadData files" throughout this document) typically contain:

1. **Metadata columns** - Information about the images (batch, plate, well, site, cycle)
2. **FileName columns** - Names of image files for each channel
3. **PathName columns** - Directories containing the image files
4. **Frame columns** - Which frame in a multi-frame file to use for each channel

LoadData files are a critical input to CellProfiler pipelines, as they define which images will be processed. Many algorithm functions in StarryNight are dedicated to generating these LoadData files for different processing stages.

## Complete Independence

**Critical Point:** The most important characteristic of the algorithm layer is its complete independence from the rest of the system.

This independence means:

- Algorithms can be tested in isolation
- They have no dependencies on StarryNight modules, pipelines, or execution engines
- They can be used directly or through any of the higher-level abstractions
- Changes to higher layers don't affect the algorithm implementations

## Algorithm Sets Structure

Algorithms are organized into "algorithm sets" -- groups of related functions that collectively handle a specific pipeline stage.

### Common Pattern

Most algorithm sets follow a consistent pattern with three key function types:

1. **LoadData Generation** - Functions that create CellProfiler LoadData CSV files
    - Typically named `gen_<algorithm>_load_data_by_batch_plate()`
    - Specifies paths, file patterns, and data organization
2. **Pipeline Generation** - Functions that create processing pipeline definitions
    - Typically named `gen_<algorithm>_cppipe_by_batch_plate()`
    - Programmatically builds CellProfiler pipelines with appropriate modules
3. **Execution** - Functions that run the pipeline on the loaded data
    - Often using `run_cp_parallel()` or similar functions
    - Handles execution, monitoring, and result collection

This pattern provides a clear separation of concerns even within the algorithm layer itself.

### Common Across Algorithm Sets

While each algorithm set handles different processing stages, they share common characteristics:

1. **Input/Output Pattern** - Each algorithm expects specific inputs and produces well-defined outputs
2. **Parameter Handling** - Consistent parameter passing and validation
3. **Path Handling** - Using standard approaches for file paths
4. **Error Handling** - Consistent approaches to error conditions

## Implementation Patterns

Algorithms employ several recurring implementation patterns:

### Sample Data Inference

A common implementation pattern is inferring parameters from sample data. For example, when generating CellProfiler pipelines, functions often:

1. Read a sample LoadData file
2. Extract channel names, cycle counts, and other metadata
3. Use this information to configure the pipeline appropriately

This approach allows algorithms to adapt to different experimental contexts without requiring all parameters to be specified explicitly.

### Path Handling

Algorithms handle various path types using the `cloudpathlib` library's `AnyPath` class, which provides a consistent interface for:

- Local file paths
- Cloud storage paths (S3, etc.)
- Relative and absolute paths

This abstraction enables algorithms to work with data regardless of its location.

### Processing Organization

Algorithms typically organize processing by Batch, Plate, Well, and Site. This hierarchical organization matches the physical structure of biological experiments.

## Beyond CellProfiler

While many algorithm sets focus on CellProfiler integration, others serve different purposes:

- **Indexing** - Creating indexes of available data
- **Inventory** - Managing metadata about available data
- **Quality Control** - Analyzing results for quality issues
- **Feature Selection** - Identifying informative features
- **Data Visualization** - Creating visualizations of results

These non-CellProfiler algorithm sets use the same architectural principles but may not follow the three-part pattern of LoadData generation, pipeline generation, and execution.

## Algorithm Complexity and Decision Points

Algorithms can incorporate conditional logic based on user requirements. For example, pipeline generation algorithms might add or remove specific modules based on flags that indicate:

- Whether to handle blurry images
- Whether to remove debris
- Which quality control steps to include

This flexibility allows algorithms to adapt to different experimental needs while maintaining their functional structure.

## Code Examples

### Example 1: LoadData Generation

A simplified example of a LoadData generation function:

```python
def gen_illum_calc_load_data_by_batch_plate(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    for_sbs: bool = False,
) -> None:
    """Generate load data for illum calc pipeline.

    Parameters
    ----------
    index_path : Path | CloudPath
        Path to index file.
    out_path : Path | CloudPath
        Path to save output csv file.
    path_mask : str | None
        Path prefix mask to use.
    for_sbs : str | None
        Generate illums for SBS images.
    """
    # Read the index file containing image metadata
    df = pl.read_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    if not for_sbs:
        images_df = df.filter(
            pl.col("is_sbs_image").ne(True), pl.col("is_image").eq(True)
        )
    else:
        images_df = df.filter(
            pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True)
        )

    # Generate hierarchy of images
    images_hierarchy_dict = gen_image_hierarchy(images_df)

    # Set up path handling
    default_path_prefix: str = (
        images_df.select("prefix").unique().to_series().to_list()[0]
    )
    if path_mask is None:
        path_mask = default_path_prefix

    # Create LoadData CSV files for each batch/plate
    for batch in images_hierarchy_dict.keys():
        for plate in images_hierarchy_dict[batch].keys():
            if not for_sbs:
                # Write loaddata assuming no image nesting with cycles
                write_loaddata_csv_by_batch_plate(
                    images_df, out_path, path_mask, batch, plate
                )
            else:
                # Write loaddata assuming image nesting with cycles
                plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)
                for cycle in plate_cycles_list:
                    write_loaddata_csv_by_batch_plate_cycle(
                        images_df, out_path, path_mask, batch, plate, cycle
                    )
```

### Example 2: Pipeline Generation

A simplified example of a pipeline generation function:

```python
def gen_illum_calculate_cppipe_by_batch_plate(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    for_sbs: bool = False,
) -> None:
    """Write out illumination calculate pipeline to file.

    Parameters
    ----------
    load_data_path : Path | CloudPath
        Path to load data csv dir.
    out_dir : Path | CloudPath
        Path to output directory.
    workspace_path : Path | CloudPath
        Path to workspace directory.
    for_sbs : str | None
        Generate illums for SBS images.
    """
    # Create output directory
    out_dir.mkdir(exist_ok=True, parents=True)

    # Get all the generated load data files
    if not for_sbs:
        type_suffix = "painting"
        files_by_hierarchy = get_files_by(["batch"], load_data_path, "*.csv")
    else:
        type_suffix = "sbs"
        files_by_hierarchy = get_files_by(["batch", "plate"], load_data_path, "*.csv")

    # Get a sample load data file to determine pipeline parameters
    _, files = flatten_dict(files_by_hierarchy)[0]

    # Create the pipeline using CellProfiler's Python API
    with CellProfilerContext(out_dir=workspace_path) as cpipe:
        cpipe = generate_illum_calculate_pipeline(cpipe, files[0], for_sbs)

        # Save pipeline in both .cppipe and .json formats
        filename = f"illum_calc_{type_suffix}.cppipe"
        with out_dir.joinpath(filename).open("w") as f:
            cpipe.dump(f)

        filename = f"illum_calc_{type_suffix}.json"
        with out_dir.joinpath(filename).open("w") as f:
            dumpit(cpipe, f, version=6)
```

### Example 3: Pipeline Execution

A simplified example of a pipeline execution function:

```python
def run_cp_parallel(
    uow_list: list[tuple[Path, Path]],
    out_dir: Path,
    plugin_dir: Path | None = None,
    jobs: int = 20,
) -> None:
    """Run cellprofiler on multiple unit-of-work (UOW) items in parallel.

    Parameters
    ----------
    uow_list : list of tuple of Path
        List of tuples containing the paths to the pipeline and load data files.
    out_dir : Path
        Output directory path.
    plugin_dir : Path
        Path to cellprofiler plugin directory.
    jobs : int, optional
        Number of parallel jobs to use (default is 20).
    """
    # Start Java Virtual Machine for CellProfiler
    cellprofiler_core.utilities.java.start_java()

    # Run pipelines in parallel
    parallel(uow_list, run_cp, [out_dir, plugin_dir], jobs)

    # Shut down Java Virtual Machine
    cellprofiler_core.utilities.java.stop_java()
```

## Integration with Higher Layers

While algorithms are independent of higher-level components, they are integrated through:

1. **CLI Layer** - Wraps algorithms in command-line interfaces
2. **Module Layer** - Uses algorithms within standardized module interfaces
3. **Container Execution** - Runs algorithms in containerized environments

This integration happens without algorithms needing to be aware of these higher layers.

The key to this integration is that algorithms are pure functions that:

- Take well-defined inputs
- Produce well-defined outputs
- Have no side effects other than those explicitly defined (like writing files)
- Don't depend on global state

This functional purity makes them easy to wrap and integrate at higher levels.

## Algorithm Development

To create a new algorithm set, developers need to:

1. Create the appropriate functions following established patterns
2. Implement LoadData generation
3. Implement pipeline generation
4. Implement execution logic
5. Create corresponding CLI wrappers
6. Create corresponding modules

When implementing new algorithms, developers should maintain the same independence and functional style that characterizes the existing algorithm layer. This ensures that new algorithms can be integrated into the higher-level abstractions without requiring changes to the architecture.

## Conclusion

The algorithm layer provides the foundational capabilities of StarryNight through pure functions that implement core image processing logic. By maintaining complete independence from higher-level components, it creates a solid foundation that enables the rest of the architecture to be flexible, modular, and extensible.

This separation is not just a design choice but a core architectural principle that makes possible the higher-level abstractions that give StarryNight its power.

**Next: [CLI Layer](02_cli_layer.md)**
