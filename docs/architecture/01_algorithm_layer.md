# StarryNight Algorithm Layer

!!! Note

    1. **Clarify LoadData concept**: Add an early explanation of CellProfiler's LoadData CSV files and their purpose. Replace all instances of "data load configuration" with "LoadData creation" throughout the document.
    2. **Reduce redundancy**: Remove repetitive mentions of algorithm independence, keeping only the essential statements at the beginning and conclusion.
    3. **Add early CellProfiler context**: Insert a note near the beginning clarifying that while most examples are CellProfiler-centric, the algorithm layer extends beyond it (as detailed later).
    4. **Replace quoted sections**: Examine the algorithm code patterns and replace all verbatim quotes with clearer technical explanations based on actual implementation patterns.
    5. **Expand code examples**: Add representative code examples for all three common algorithm functions: LoadData generation, pipeline generation (gen_CP_pipe), and pipeline execution.
    6. **Update terminology consistency**: Ensure consistent terminology throughout, particularly around pipeline generation and execution concepts.
    7. **Review section flow**: Verify the logical progression of sections, ensuring concepts are introduced before they're referenced in later explanations.


## Overview

The algorithm layer forms the foundation of the StarryNight framework. Algorithms are pure Python functions that implement specific image processing operations and pipeline generation capabilities without dependencies on higher-level StarryNight components.

This document explains the structure and organization of the algorithm layer.

## Purpose

Algorithms in StarryNight serve several essential purposes:

1. **Image Processing Logic** - Implementing the core computational steps
2. **Pipeline Generation** - Creating CellProfiler pipeline files programmatically
3. **Data Load Configuration** - Specifying how data should be loaded for processing
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

1. **Load Data Generation** - Functions that create configurations for loading data
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

As noted in the architecture discussions:

> "In all of the cell profiler pipeline when I'm generating... the first thing that we do in the function is try to read one of the sample load data for that module, and then extract out the channel names, the number of cycles and things like that... from the load data itself."

This pattern allows algorithms to adapt to different experimental contexts by inferring parameters from data.

### Path Handling

Algorithms must handle various path types:

> "People are going to use the CLI to give you paths. And these paths can be a relative path, an absolute path, a path that's in the local file system, or it can be a file path that's in some S3 bucket..."

This is addressed at the CLI layer but influences algorithm design.

### Processing Organization

Algorithms typically organize processing by Batch, Plate, Well, and Site. This hierarchical organization matches the physical structure of biological experiments.

## Beyond CellProfiler

While many algorithm sets focus on CellProfiler integration, others serve different purposes:

> "We also have indexing and inventory. Okay, so those are not cell profiler centric."

These algorithm sets handle data organization, metadata extraction, and inventory management rather than image processing directly.

Other non-CellProfiler algorithm sets might include:

- **Indexing** - Creating indexes of available data
- **Inventory** - Managing metadata about available data
- **Quality Control** - Analyzing results for quality issues
- **Feature Selection** - Identifying informative features
- **Data Visualization** - Creating visualizations of results

## Algorithm Complexity and Decision Points

Algorithms can incorporate conditional logic based on user requirements:

> "If you want to go that route, these algorithms will become complex. This can try to account for like, 'Okay, if a user wants to create a pipeline that will take care of blurry images or take care of debris in their images'... based on those flags, we can make certain decisions, what modules to add in which stage, right?"

This flexibility allows algorithms to adapt to different experimental needs while maintaining their functional structure.

## Core Architecture Benefit

The complete independence of the algorithm layer is what enables the higher-level abstractions without sacrificing flexibility. The architecture discussions emphasize:

> "The first thing, which is the algorithm model, like, completely separate the core part. It's not dependent, dependent on anything else. And then, you know, you can use it independently, you know, the CLI and everything, right?"

This separation is the foundation that allows the more sophisticated abstractions to be built on top without creating tight coupling or circular dependencies.

## Code Example

A simplified example of what an algorithm function might look like:

```python
def gen_analysis_load_data_by_batch_plate(
    images_path: AnyPath,
    output_path: AnyPath,
    batch_id: str,
    plate_id: str,
    channels: List[str],
    **kwargs
) -> AnyPath:
    """
    Generate a CellProfiler LoadData CSV file for the analysis pipeline.

    Parameters
    ----------
    images_path : AnyPath
        Path to the processed images
    output_path : AnyPath
        Path where the load data file will be written
    batch_id : str
        Batch identifier
    plate_id : str
        Plate identifier
    channels : List[str]
        List of channel names to include

    Returns
    -------
    AnyPath
        Path to the generated load data file
    """
    # Implementation details...
    # 1. Find all relevant images
    # 2. Organize them by well and site
    # 3. Generate the LoadData CSV
    # 4. Return the path to the file
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
2. Implement load data generation
3. Implement pipeline generation
4. Implement execution logic
5. Create corresponding CLI wrappers
6. Create corresponding modules

When implementing new algorithms, developers should maintain the same independence and functional style that characterizes the existing algorithm layer. This ensures that new algorithms can be integrated into the higher-level abstractions without requiring changes to the architecture.

## Conclusion

The algorithm layer provides the foundational capabilities of StarryNight through pure functions that implement core image processing logic. By maintaining complete independence from higher-level components, it creates a solid foundation that enables the rest of the architecture to be flexible, modular, and extensible.

This separation is not just a design choice but a core architectural principle that makes possible the higher-level abstractions that give StarryNight its power.

**Next: [CLI Layer](02_cli_layer.md)**
