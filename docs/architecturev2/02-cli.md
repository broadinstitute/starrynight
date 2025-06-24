# CLI Layer

!!! warning "Experimental - Not Reviewed"
    Content may be incomplete or inaccurate.

## Purpose

The CLI Layer provides command-line access to StarryNight's algorithm functions, solving the problem of making scientific algorithms accessible to users without requiring Python programming knowledge. This layer wraps standalone Python algorithm functions with user-friendly interfaces, parameter validation, and consistent error handling. By maintaining a thin wrapper approach, the CLI layer ensures that all algorithm capabilities remain available through both programmatic and command-line interfaces, supporting both interactive exploration and automated pipeline execution.

## Responsibilities

- Wrap algorithm functions with Click-based command-line interfaces
- Parse and validate command-line arguments before passing to algorithms
- Provide consistent command structure and user experience across all algorithm sets
- NOT responsible for: Implementing algorithms, orchestrating workflows, managing execution backends, or handling complex multi-step operations

## Key Design Decisions

1.  **Direct Algorithm Imports (Decision #3)**: The CLI layer imports algorithm functions directly and wraps them without modification. This thin wrapper approach ensures that CLI commands have identical behavior to direct function calls, maintaining consistency and avoiding hidden complexity. The Click framework provides the infrastructure for parameter parsing and command organization.

2.  **Click Integration (Decision #8)**: All CLI implementations use the Click framework for its declarative parameter definition, automatic help generation, and robust argument parsing. This standardization ensures consistent user experience across commands while leveraging Click's built-in support for path handling, type conversion, and validation.

## Interfaces

### Inputs

- Command-line arguments and options parsed by Click
- File paths as strings converted to cloudpathlib AnyPath objects
- Algorithm parameters with Click-validated types and constraints

### Outputs

- Algorithm function return values passed through to shell
- Status messages and progress indicators to stderr
- Exit codes following Unix conventions (0 for success, non-zero for errors)

### Dependencies

- Internal dependencies: Algorithm layer functions (direct imports following upward-only rule)
- External dependencies: Click framework, cloudpathlib for path conversion

## Patterns

The CLI layer follows consistent patterns for wrapping algorithm functions:

### Command Structure Pattern

The CLI uses Click's decorator-based approach to create hierarchical command structures. Commands are organized into groups, with each group containing related subcommands. Options are defined with validation rules, while arguments represent required positional parameters. This pattern enables intuitive command-line interfaces like `starrynight illum calc` or `starrynight analysis run`.

### Path Handling Pattern

All file paths received as command-line strings are converted to cloudpathlib's AnyPath objects before being passed to algorithm functions. This conversion happens at the CLI boundary, ensuring that algorithm functions always receive path objects that work seamlessly with both local filesystems and cloud storage. The pattern maintains consistency across all commands while abstracting storage details from users.

### Direct Algorithm Wrapping Pattern

CLI commands import algorithm functions directly and wrap them with minimal additional logic. The wrapper handles only CLI-specific concerns: parameter conversion from strings to appropriate types, validation of user inputs, and status reporting. The actual algorithm call passes through unchanged, maintaining the principle that CLI commands are thin wrappers around algorithm functionality.

### Parameter Patterns

- File paths: Use `click.Path()` for validation
- Boolean flags: Use `is_flag=True`
- Multiple values: Use `multiple=True` for lists
- Choices: Use `click.Choice()` for enums
- Required options: Use `required=True`

### Error Handling Pattern

The CLI layer relies on Click's built-in error handling:

- Invalid arguments produce automatic error messages
- Missing required options are caught by Click
- Algorithm errors propagate naturally to the user

This approach ensures that CLI commands remain thin wrappers that focus solely on command-line interface concerns, while the actual implementation logic stays in the algorithm layer.

## Implementation Location

- Primary location: `starrynight/src/starrynight/cli/`
- Main entry point: `starrynight/src/starrynight/cli/main.py`
- Tests: `starrynight/tests/cli/`

Individual command modules are named after the algorithms they wrap (e.g., `illum.py` for illumination commands, `index.py` for barcode indexing).

## See Also

- Previous: [Algorithm Layer](01-algorithm.md), Next: [Module Layer](03-module.md)
