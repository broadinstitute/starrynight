# StarryNight Algorithm Layer

## Overview

The algorithm layer forms the foundation of the StarryNight framework. Algorithms are pure Python functions that implement specific image processing operations and pipeline generation capabilities without dependencies on higher-level StarryNight components.

This document explains the structure and organization of the algorithm layer, using the `algorithms/analysis.py` file as a primary example to illustrate key concepts.

## Purpose

Algorithms in StarryNight serve several essential purposes:

1. **Image Processing Logic** - Implementing the core computational steps
2. **Pipeline Generation** - Creating CellProfiler pipeline files programmatically
3. **Data Load Configuration** - Specifying how data should be loaded for processing
4. **Pipeline Execution** - Running processing steps on prepared data

By separating these functions from higher-level concerns like UI, execution environment, and workflow composition, the algorithm layer maintains simplicity and testability.

## Complete Independence

**Critical Point:** The most important characteristic of the algorithm layer is its complete independence from the rest of the system. As emphasized in the architecture discussions:

This independence means:
- Algorithms can be tested in isolation
- They have no dependencies on StarryNight modules, pipelines, or execution engines
- They can be used directly or through any of the higher-level abstractions
- Changes to higher layers don't affect the algorithm implementations

## Algorithm Sets Structure

Algorithms are organized into "algorithm sets" - groups of related functions that collectively handle a specific pipeline stage. From the architecture discussions:

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

### Differences Between Algorithm Sets

Each algorithm set has unique aspects:

> "The difference is, again, each of them expects load data to be in a certain format. That's not consistent across different modules. The same with cell profiler pipeline is completely different for the most part."

These differences reflect the specific requirements of each processing stage.

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

Algorithms typically organize processing by:
- Batch
- Plate
- Well
- Site

This hierarchical organization matches the physical structure of biological experiments.

## Example: analysis.py

The `algorithms/analysis.py` file demonstrates the algorithm pattern clearly. From the architecture discussions:

> "We have these functions right, and these functions accept some parameters, you can invoke and do things right... This has a bunch of functions that has three capabilities. One is to create a CP pipe file. One is to create the load data file, and one is to invoke the CP pipe file on the load data."

Key functions likely include:
- Functions to generate load data configurations
- Functions to generate CellProfiler pipelines
- Functions to run CellProfiler with the generated configurations

Analysis algorithms typically handle the final stages of a cell painting pipeline, where analyzed images are measured and features are extracted. These algorithms may include:

1. **Load Data Generation for Analysis** - Creating load data configurations that point to preprocessed images
2. **Pipeline Generation for Analysis** - Creating CellProfiler pipelines with measurement modules
3. **Analysis Execution** - Running the analysis pipelines and collecting measurement results

A typical analysis pipeline might include CellProfiler modules like:
- MeasureObjectSizeShape
- MeasureObjectIntensity
- MeasureTexture
- MeasureRadialDistribution
- ExportToDatabase

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

As emphasized in the architecture discussions, this separation is not just a design choice but a core architectural principle that makes possible the higher-level abstractions that give StarryNight its power.

**Next: [CLI Layer](02_cli_layer.md)**
