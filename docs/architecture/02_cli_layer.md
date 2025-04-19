# StarryNight CLI Layer

## Overview

The CLI (Command Line Interface) layer in StarryNight provides command-line access to the underlying algorithms. It wraps pure algorithm functions with user-friendly interfaces, handles parameter parsing, and manages execution. Building upon the algorithm layer, the CLI layer serves as the primary direct interface for users to interact with StarryNight's capabilities through terminal commands.

## Purpose

The CLI layer serves several key purposes:

1. **User Access** - Provides direct command-line access to StarryNight algorithms
2. **Parameter Handling** - Converts command-line arguments to appropriate parameter types
3. **Path Management** - Handles different path formats (local, cloud storage, relative, absolute)
4. **Command Organization** - Structures commands into logical groups
5. **Documentation** - Provides help text and usage examples

The CLI layer directly imports algorithm functions and exposes them through command-line interfaces. For example, `analysis.py` in the CLI directory imports functions like `gen_analysis_load_data` and `gen_analysis_pipeline` from the algorithms layer and makes them accessible as CLI commands.

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

StarryNight uses the [Click](https://click.palletsprojects.com/) library for CLI implementation. Click provides a decorator-based approach to define commands, options, and arguments with clear help text. This allows for a clean separation between interface definition and implementation logic.

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

The CLI converts user-provided path strings into standardized path objects that work with both local and cloud storage. Users may provide paths in various formats (local, relative, cloud) which the CLI normalizes using the [cloudpathlib](https://cloudpathlib.drivendata.org/) library:

```python
from cloudpathlib import AnyPath

def cli_function(input_path, output_path):
    # Convert string paths to path objects
    input_path = AnyPath(input_path)
    output_path = AnyPath(output_path)

    # Call algorithm with consistent path interface
    algorithm_function(input_path, output_path)
```

This approach provides a consistent interface regardless of where data is stored, allowing algorithms to work with both local files and cloud storage seamlessly.

## Flag Handling

The CLI layer also handles flags that control algorithm behavior. For example, some commands support different assay types (SBS or CP) through flags rather than separate commands. This approach simplifies the user experience by providing a consistent interface while allowing the CLI to invoke different underlying algorithm functions based on the flags provided.

## Integration with main.py

The CLI layer integrates all command groups into a single entry point in `main.py`. Each algorithm set defines its own command group, which is then imported and registered with the main CLI application. This approach creates a modular structure where new algorithm sets can be easily added without modifying existing code.

This creates a consistent, hierarchical command structure:

```
starrynight
├── analysis
│   ├── loaddata
│   └── cppipe
├── illum
│   ├── calc
│   │   ├── loaddata
│   │   └── cppipe
│   └── apply
│       ├── loaddata
│       └── cppipe
├── segcheck
└── [other commands...]
```

## Creating New CLI Commands

To create a new CLI command, developers follow this pattern:

1. Create a new file in the CLI directory (or use an existing one)
2. Import the relevant algorithm functions
3. Create a click command group
4. Define commands using Click decorators
5. Implement the command functions to call algorithms
6. Add the command group to main.py

This pattern helps maintain a clean separation between different algorithm sets (groups of related functions that collectively handle a specific pipeline stage) while providing a unified command structure to users. Each algorithm set can evolve independently without affecting others, which simplifies maintenance and development.

## CLI Limitations

While the CLI is powerful for direct algorithm access, it has limitations compared to higher-level StarryNight components:

1. No containerization - Runs in the current environment without isolation
2. Manual parameter specification - All parameters must be specified directly
3. No workflow composition - Each command runs independently
4. No parallelism management - Multi-step processes must be coordinated manually

These limitations are addressed by the module and pipeline layers.

## Example: analysis.py

The `cli/analysis.py` file demonstrates the CLI pattern (simplified excerpt):

```python
import click
from cloudpathlib import AnyPath

from starrynight.algorithms.analysis import (
    gen_analysis_cppipe_by_batch_plate,
    gen_analysis_load_data_by_batch_plate,
)

@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-c", "--corr_images", required=True)
@click.option("-p", "--comp_images", required=True)
@click.option("-m", "--path_mask", default=None)
def gen_analysis_load_data(
    index: str,
    out: str,
    corr_images: str,
    comp_images: str,
    path_mask: str | None,
) -> None:
    """Generate analysis loaddata file."""
    gen_analysis_load_data_by_batch_plate(
        AnyPath(index),
        AnyPath(out),
        path_mask,
        AnyPath(corr_images),
        AnyPath(comp_images),
    )

@click.group()
def analysis() -> None:
    """Analysis commands."""
    pass

analysis.add_command(gen_analysis_load_data)
# The actual file includes additional commands like 'cppipe'
```

## CLI Usage Examples

Example 1: Generate load data for analysis (local storage)
```bash
starrynight analysis loaddata \
  -i /path/to/index \
  -o /path/to/output \
  -c /path/to/corrected_images \
  -p /path/to/compensated_images
```

Example 2: Generate a CellProfiler pipeline
```bash
starrynight analysis cppipe \
  -l /path/to/loaddata \
  -o /path/to/output \
  -w /path/to/workspace \
  -b /path/to/barcode.csv \
  -n DAPI \
  -e CellMask \
  -m MitoTracker
```

Example 3: Working with cloud storage data
```bash
starrynight illum calc loaddata \
  -i s3://bucket-name/path/to/index \
  -o s3://bucket-name/path/to/output
```

## Conclusion

The CLI layer sits directly above the algorithm layer in the StarryNight architecture, providing a straightforward interface to the underlying algorithms while remaining below the more sophisticated module layer. By following consistent patterns with the Click library and using cloudpathlib for path handling, the CLI offers a user-friendly experience while maintaining flexibility across different storage environments.

While the CLI is only one way to access StarryNight functionality (alongside notebooks and the UI), it serves as an important bridge between pure algorithm functions and higher-level abstractions. It provides direct access for testing and scripting while establishing patterns that inform the module layer discussed next.

**Next: [Module Layer](03_module_layer.md)**
