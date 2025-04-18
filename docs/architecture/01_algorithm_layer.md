# StarryNight Algorithm Layer

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

By focusing solely on the core computational logic without higher-level concerns, the algorithm layer maintains simplicity and testability.

## Design Principles

Algorithms in StarryNight follow these key design principles:

- **Independence**: No dependencies on other StarryNight components
- **Clear Boundaries**: Well-defined inputs, outputs, and side effects
- **Focused Responsibility**: Each algorithm performs a specific task
- **Portability**: Can be used in any context without modification
- **Explicit State**: Avoid global state or implicit dependencies

The most important characteristic of the algorithm layer is its **complete independence** from the rest of the system.

## Algorithm Sets Structure

Algorithms are organized into "algorithm sets" -- groups of related functions that collectively handle a specific pipeline stage.

### Common Pattern

Most algorithm sets follow a consistent pattern with three key function types:

!!! abstract "Common patterns"

    === "1: LoadData Generation"
        Functions that create CSV files defining which images to process

        - Typically named `gen_<algorithm>_load_data_by_batch_plate()`
        - These functions identify relevant images from indexes or metadata
        - They organize images by batch, plate, well, and site
        - They output CSV files with paths and metadata CellProfiler needs to load images
        - LoadData files contain metadata, filenames, paths, and frame information

    === "2: Pipeline Generation"
        Functions that create processing pipeline definitions

        - Typically named `gen_<algorithm>_cppipe_by_batch_plate()`
        - These functions programmatically create processing pipelines
        - They configure pipeline modules with appropriate parameters
        - They often infer parameters from sample LoadData files
        - They output pipeline files in formats like .cppipe or .json

    === "3: Execution"
        Functions that run the pipeline on the loaded data

        - Often using `run_cp_parallel()` or similar functions
        - These functions handle running the generated pipelines against the data
        - They manage parallel execution for performance
        - They handle resource allocation and cleanup
        - They organize outputs according to the experimental structure

This pattern provides a clear separation of concerns even within the algorithm layer itself.

### Common Across Algorithm Sets

While each algorithm set handles different processing stages, they share common characteristics:

1. **Input/Output Pattern** - Each algorithm expects specific inputs and produces well-defined outputs
2. **Parameter Handling** - Consistent parameter passing and validation
3. **Path Handling** - Using standard approaches for file paths
4. **Error Handling** - Consistent approaches to error conditions

## Implementation Patterns

Algorithms employ several recurring implementation patterns:

!!! abstract "Implementation patterns"

    === "Sample Data Inference"
        This pattern primarily applies to **pipeline generation algorithms**. When creating pipeline definitions, these algorithms:

        1. Read a sample LoadData file
        2. Extract channel names, cycle counts, and other metadata
        3. Use this information to configure the pipeline appropriately

        This approach allows pipeline generation algorithms to adapt to different experimental contexts without requiring all parameters to be specified explicitly.

    === "Path Handling"
        This pattern applies to **all algorithm types**. All algorithms use the `cloudpathlib` library's `AnyPath` class, which provides a consistent interface for:

        - Local file paths
        - Cloud storage paths (S3, etc.)
        - Relative and absolute paths

        This abstraction enables algorithms to work with data regardless of its location, which is essential for all algorithm types from LoadData generation to execution.

    === "Processing Organization"

        This pattern applies primarily to **LoadData generation and execution algorithms**. These algorithms organize processing by experimental hierarchy:

        - Plate - A multi-well plate containing experimental samples
        - Well - A compartment within a plate with one experimental condition
        - Site - A microscope field of view capturing a region of a well
        - Batch - A group of plates

        Algorithms typically group by batch-plate, batch-plate-well, or batch-plate-well-site depending on processing needs.

## Beyond CellProfiler

While many algorithm sets focus on CellProfiler integration, others serve different purposes:

- **Indexing** - Creating indexes of available data
- **Inventory** - Managing metadata about available data
- **Quality Control** - Analyzing results for quality issues
- **Feature Selection** - Identifying informative features
- **Data Visualization** - Creating visualizations of results

These non-CellProfiler algorithm sets use the same architectural principles but may not follow the three-part pattern of LoadData generation, pipeline generation, and execution.

## Algorithm Complexity and Decision Points

Pipeline generation algorithms can incorporate conditional logic based on user requirements. For example, these algorithms might add or remove specific modules based on flags that indicate:

- Whether to handle blurry images
- Whether to remove debris
- Which quality control steps to include

This flexibility allows pipeline generation algorithms to adapt to different experimental needs while maintaining their functional structure.

## Code Examples

The following examples are simplified pseudocode based on actual StarryNight implementations but edited for clarity. They demonstrate the typical patterns found in algorithm sets.

!!! abstract "Code Examples"

    === "Example 1: LoadData Generation"

            def gen_algorithm_load_data_by_batch_plate(
                index_path: Path | CloudPath,
                out_path: Path | CloudPath,
                path_mask: str | None,
                for_special_type: bool = False,
            ) -> None:
                """Generate LoadData CSV files for a specific algorithm.

                Reads image metadata from an index, organizes by batch/plate structure,
                and writes LoadData CSV files for CellProfiler.
                """
                # Read from index file (typically parquet format)
                df = pl.read_parquet(index_path.resolve().__str__())

                # Filter for relevant images based on criteria
                if not for_special_type:
                    images_df = df.filter(pl.col("type_flag").ne(True), pl.col("is_image").eq(True))
                else:
                    images_df = df.filter(pl.col("type_flag").eq(True), pl.col("is_image").eq(True))

                # Organize images hierarchically (by batch, plate, etc.)
                images_hierarchy_dict = gen_image_hierarchy(images_df)

                # Handle path prefix for correct file resolution
                default_path_prefix = images_df.select("prefix").unique().to_series().to_list()[0]
                if path_mask is None:
                    path_mask = default_path_prefix

                # Generate LoadData files for each batch/plate combination
                for batch in images_hierarchy_dict.keys():
                    for plate in images_hierarchy_dict[batch].keys():
                        if not for_special_type:
                            # Standard case
                            write_loaddata_csv_by_batch_plate(
                                images_df, out_path, path_mask, batch, plate
                            )
                        else:
                            # Special case with cycle information
                            plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)
                            for cycle in plate_cycles_list:
                                write_loaddata_csv_by_batch_plate_cycle(
                                    images_df, out_path, path_mask, batch, plate, cycle
                                )

    === "Example 2: Pipeline Generation"

            def gen_algorithm_cppipe_by_batch_plate(
                load_data_path: Path | CloudPath,
                out_dir: Path | CloudPath,
                workspace_path: Path | CloudPath,
                special_option: bool = False,
            ) -> None:
                """Create a CellProfiler pipeline programmatically.

                Reads a sample LoadData file to determine parameters,
                then constructs a pipeline with appropriate modules.
                """
                # Ensure output directory exists
                out_dir.mkdir(exist_ok=True, parents=True)

                # Find appropriate LoadData files to use as samples
                if not special_option:
                    type_suffix = "standard"
                    files_by_hierarchy = get_files_by(["batch"], load_data_path, "*.csv")
                else:
                    type_suffix = "special"
                    files_by_hierarchy = get_files_by(["batch", "plate"], load_data_path, "*.csv")

                # Get sample file for inferring parameters
                _, files = flatten_dict(files_by_hierarchy)[0]

                # Create pipeline with CellProfiler API
                with CellProfilerContext(out_dir=workspace_path) as cpipe:
                    # Generate pipeline with appropriate modules based on options
                    cpipe = generate_specific_pipeline(cpipe, files[0], special_option)

                    # Save pipeline in multiple formats
                    filename = f"algorithm_{type_suffix}.cppipe"
                    with out_dir.joinpath(filename).open("w") as f:
                        cpipe.dump(f)
                    filename = f"algorithm_{type_suffix}.json"
                    with out_dir.joinpath(filename).open("w") as f:
                        json.dump(cpipe.json(), f)

    === "Example 3: Pipeline Execution"

            def run_cp_parallel(
                uow_list: list[tuple[Path, Path]],
                out_dir: Path,
                plugin_dir: Path | None = None,
                jobs: int = 20,
            ) -> None:
                """Run CellProfiler pipelines in parallel.

                Takes a list of pipeline and LoadData file pairs (units of work),
                then executes them with appropriate parallelism.

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
                # Initialize execution environment (e.g., start Java VM for CellProfiler)
                cellprofiler_core.utilities.java.start_java()

                # Execute all units of work in parallel
                # The 'parallel' function is a utility that runs the specified function
                # on each item in the list with the given parameters
                parallel(uow_list, run_cp, [out_dir, plugin_dir], jobs)

## Algorithm Development

For CellProfiler-related algorithm sets, developers typically need to:

1. Create the appropriate functions following established patterns
2. Implement LoadData generation
3. Implement pipeline generation
4. Implement execution logic

For other algorithm types (indexing, inventory, quality control, etc.), the specific functions will vary based on purpose, but the underlying principles remain the same.

Regardless of algorithm type, implementations should follow the established patterns and independence principles of the algorithm layer.

## Conclusion

The algorithm layer provides the foundational capabilities of StarryNight through pure Python functions that implement core image processing logic. This organization enables flexible and extensible scientific image processing.

**Next: [CLI Layer](02_cli_layer.md)**
