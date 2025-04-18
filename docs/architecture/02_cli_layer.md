# StarryNight CLI Layer

## Overview

The CLI (Command Line Interface) layer in StarryNight provides command-line access to the underlying algorithms. It wraps algorithm functions with user-friendly interfaces, handles parameter parsing, and manages execution. This document explores how the CLI layer is structured and how it integrates with the algorithm layer.

## Purpose

The CLI layer serves several key purposes:

1. **User Access** - Provides direct command-line access to StarryNight algorithms
2. **Parameter Handling** - Converts command-line arguments to appropriate parameter types
3. **Path Management** - Handles different path formats (local, cloud storage, relative, absolute)
4. **Command Organization** - Structures commands into logical groups
5. **Documentation** - Provides help text and usage examples

As noted in the architecture discussions:

> "This is just algorithms, okay... This is one of the CLI files. This is analysis.py inside the CLI folder, it just imports the load data generation function and the cell profiler pipeline generation function, and then it exposes those functions as a CLI module."

## Structure

The CLI layer follows a consistent organization pattern:

### Command Groups

Commands are organized into groups based on algorithm sets. For example:

- `analysis` group for analysis algorithms
- `illum` group for illumination algorithms
- `segcheck` group for segmentation check algorithms

### Command Implementation

Each command typically:
1. Imports algorithm functions
2. Defines command parameters using Click decorators
3. Implements a function that calls the underlying algorithm
4. Manages path conversions and validations

## Click Library Integration

StarryNight uses the [Click](https://click.palletsprojects.com/) library for CLI implementation:

> "So we are using click as our kind of CLI library. And with click, you just, you know, we can decorate a function with all the options you need, and then name the function, or like, name that command."

### Command Group Pattern

The pattern for creating new CLI command groups is consistent:

```python
@click.group()
def analysis():
    """Commands for analysis pipelines."""
    pass

@analysis.command()
@click.option("--input-path", required=True, help="Path to input data")
@click.option("--output-path", required=True, help="Path for output")
# Additional options...
def generate_load_data(input_path, output_path, **options):
    """Generate load data file for analysis pipeline."""
    # Convert paths to AnyPath
    input_path = AnyPath(input_path)
    output_path = AnyPath(output_path)

    # Call the algorithm function
    return algorithms.analysis.gen_analysis_load_data(
        input_path=input_path,
        output_path=output_path,
        **options
    )
```

## Path Handling

One of the key responsibilities of the CLI layer is handling different types of file paths:

> "The only thing to pay attention to here is, is how to handle paths. You know, because people are going to the who are going to use this, they're going to use a CLI to give you path. And these paths can be a relative path, an absolute path, a path that's in the local file system, or it can be a file path that's in some S3 bucket things like that."

### Cloud Path Library

The CLI uses the [cloudpathlib](https://cloudpathlib.drivendata.org/) library to handle various path types:

> "So trying to handle those things, the way I'm handling is by something called Cloud path library, and it gives you this, this class called any path. So based on which path you give it, it will try to create either a path lib object... or it can return a cloud path lib object that you can use to transparently kind of access files from S3 bucket."

This abstraction allows the CLI to work with both local and cloud storage using a consistent interface.

## Flag Handling

The CLI layer also handles flags that control algorithm behavior:

> "Previously, because we are using single functions to generate both SBS and CP pipelines. So we also exposed those parameters here, and based on like which flag is given. For example, if SBS flag is given or not, we are based on that we're calling different functions."

This simplifies the user experience by providing a consistent interface across different algorithm types.

## Integration with main.py

The CLI layer integrates all command groups into a single entry point:

> "You first create a group that is based on your algorithm set name, for example, for analysis, you create a group called analysis. You add all the sub-commands to the analysis... and then you import this group into the main.py CLI file, and then add that group to your main command."

This creates a consistent, hierarchical command structure:

```
starrynight
├── analysis
│   ├── generate-load-data
│   ├── generate-pipeline
│   └── run-pipeline
├── illum
│   ├── calculate
│   └── apply
└── segcheck
    ├── ...
```

## Creating New CLI Commands

To create a new CLI command, developers follow this pattern:

1. Create a new file in the CLI directory (or use an existing one)
2. Import the relevant algorithm functions
3. Create a click command group
4. Define commands using Click decorators
5. Implement the command functions to call algorithms
6. Add the command group to main.py

As the architecture discussions explain:

> "So basically, you know you you first create a group that is based on your algorithm, set name, for example, for analysis, you create a group called analysis. You add all the sub commands to the analysis for example, load data generation and generate C pipe. So you add those commands to your analysis group, and then you import this group into the main.pi CLI file, and then add that group to your main command."

## CLI Limitations

While the CLI is powerful for direct algorithm access, it has limitations compared to higher-level StarryNight components:

1. No containerization - Runs in the current environment without isolation
2. Manual parameter specification - All parameters must be specified directly
3. No workflow composition - Each command runs independently
4. No parallelism management - Multi-step processes must be coordinated manually

These limitations are addressed by the module and pipeline layers.

## Example: analysis.py

The `cli/analysis.py` file demonstrates the CLI pattern:

```python
import click
from cloudpathlib import AnyPath

from starrynight.algorithms import analysis

@click.group()
def analysis_commands():
    """Analysis pipeline commands."""
    pass

@analysis_commands.command()
@click.option(
    "--images-path",
    required=True,
    help="Path to the images to analyze"
)
@click.option(
    "--output-path",
    required=True,
    help="Path where load data will be written"
)
@click.option(
    "--batch-id",
    required=True,
    help="Batch identifier"
)
@click.option(
    "--plate-id",
    required=True,
    help="Plate identifier"
)
def generate_load_data(images_path, output_path, batch_id, plate_id):
    """Generate a load data file for the analysis pipeline."""
    images_path = AnyPath(images_path)
    output_path = AnyPath(output_path)

    analysis.gen_analysis_load_data_by_batch_plate(
        images_path=images_path,
        output_path=output_path,
        batch_id=batch_id,
        plate_id=plate_id
    )
```

## CLI Usage Examples

Example 1: Generate load data for analysis
```bash
starrynight analysis generate-load-data \
  --images-path /path/to/images \
  --output-path /path/to/output \
  --batch-id Batch1 \
  --plate-id Plate1
```

Example 2: Generate a CellProfiler pipeline
```bash
starrynight analysis generate-pipeline \
  --output-path /path/to/output \
  --nuclear-channel DAPI \
  --cell-channel CellMask
```

## Conclusion

The CLI layer provides a straightforward interface to StarryNight algorithms, making them accessible without programming. By following consistent patterns with the Click library and using cloudpathlib for path handling, the CLI offers a user-friendly experience while maintaining flexibility.

While the CLI is only one way to access StarryNight functionality (alongside notebooks and the UI), it provides an important direct interface for testing, scripting, and integration with other tools.

**Next: [Module System](03_module_system.md)**
