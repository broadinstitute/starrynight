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

By separating these functions from higher-level concerns like UI, execution environment, and workflow composition, the algorithm layer maintains simplicity and testability.

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

1. **LoadData Generation** - Functions that create CSV files defining which images to process
    - Typically named `gen_<algorithm>_load_data_by_batch_plate()`
    - These functions identify relevant images from indexes or metadata
    - They organize images by batch, plate, well, and site
    - They output CSV files with paths and metadata CellProfiler needs to load images
    - LoadData files contain metadata, filenames, paths, and frame information

2. **Pipeline Generation** - Functions that create processing pipeline definitions
    - Typically named `gen_<algorithm>_cppipe_by_batch_plate()`
    - These functions programmatically create processing pipelines
    - They configure pipeline modules with appropriate parameters
    - They often infer parameters from sample LoadData files
    - They output pipeline files in formats like .cppipe or .json

3. **Execution** - Functions that run the pipeline on the loaded data
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

### Sample Data Inference

This pattern primarily applies to **pipeline generation algorithms**. When creating pipeline definitions, these algorithms:

1. Read a sample LoadData file
2. Extract channel names, cycle counts, and other metadata
3. Use this information to configure the pipeline appropriately

This approach allows pipeline generation algorithms to adapt to different experimental contexts without requiring all parameters to be specified explicitly.

### Path Handling

This pattern applies to **all algorithm types**. All algorithms use the `cloudpathlib` library's `AnyPath` class, which provides a consistent interface for:

- Local file paths
- Cloud storage paths (S3, etc.)
- Relative and absolute paths

This abstraction enables algorithms to work with data regardless of its location, which is essential for all algorithm types from LoadData generation to execution.

### Processing Organization

This pattern applies primarily to **LoadData generation and execution algorithms**. These algorithms organize processing by:

- Batch - A collection of related plates
- Plate - A physical container with multiple wells
- Well - A single experimental unit
- Site - A specific imaging location within a well

This hierarchical organization matches the physical structure of biological experiments and allows algorithms to process data in logical groups.

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

### Example 1: LoadData Generation

```python
def generate_load_data(index_path, output_path, path_mask=None, for_special_type=False):
    """Generate LoadData CSV files for a specific algorithm.

    Reads image metadata from an index, organizes by batch/plate structure,
    and writes LoadData CSV files for CellProfiler.
    """
    # Read and filter image metadata
    image_data = read_metadata_from_index(index_path)
    image_data = filter_images_by_type(image_data, for_special_type)

    # Organize images hierarchically
    image_hierarchy = organize_by_batch_plate(image_data)

    # Set up path handling
    path_prefix = determine_path_prefix(image_data, path_mask)

    # For each batch and plate, create a LoadData file
    for batch in image_hierarchy:
        for plate in image_hierarchy[batch]:
            if not for_special_type:
                write_standard_load_data(
                    image_data, output_path, path_prefix, batch, plate
                )
            else:
                # Handle special case with cycle information
                cycles = get_cycles_for_batch_plate(image_data, batch, plate)
                for cycle in cycles:
                    write_cycled_load_data(
                        image_data, output_path, path_prefix, batch, plate, cycle
                    )
```

### Example 2: Pipeline Generation

```python
def generate_pipeline(load_data_path, output_dir, workspace_path, pipeline_type=None):
    """Create a CellProfiler pipeline programmatically.

    Reads a sample LoadData file to determine parameters,
    then constructs a pipeline with appropriate modules.
    """
    # Ensure output directory exists
    create_directory(output_dir)

    # Find LoadData files to use as samples
    load_data_files = find_load_data_files(load_data_path, pipeline_type)
    sample_file = select_sample_file(load_data_files)

    # Read the sample file to determine parameters
    channels, metadata = extract_parameters_from_load_data(sample_file)

    # Create pipeline with appropriate modules
    pipeline = create_empty_pipeline()

    # Add LoadData module configured for the input files
    add_load_data_module(pipeline, sample_file)

    # Add processing modules based on pipeline type
    if pipeline_type == "illumination":
        for channel in channels:
            add_illumination_modules(pipeline, channel)
    elif pipeline_type == "segmentation":
        add_segmentation_modules(pipeline, channels, metadata)

    # Add output modules
    add_output_modules(pipeline, output_dir)

    # Save the pipeline to disk
    save_pipeline(pipeline, output_dir, pipeline_type)
```

### Example 3: Pipeline Execution

```python
def execute_pipeline(pipeline_paths, load_data_paths, output_dir, jobs=20):
    """Run CellProfiler pipelines in parallel.

    Takes a list of pipeline and LoadData files,
    then executes them with appropriate parallelism.
    """
    # Prepare execution environment
    initialize_execution_environment()

    # Create unit-of-work pairs (pipeline + load data)
    work_units = list(zip(pipeline_paths, load_data_paths))

    # Configure parallel execution
    parallel_executor = create_parallel_executor(jobs)

    # Execute all units of work
    for pipeline_path, load_data_path in work_units:
        parallel_executor.submit(
            run_single_pipeline,
            pipeline_path,
            load_data_path,
            output_dir
        )

    # Wait for completion and clean up
    parallel_executor.wait_for_completion()
    cleanup_execution_environment()
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
