# Algorithm Layer

!!! warning "Experimental - Not Reviewed"
    Content may be incomplete or inaccurate.

## Purpose

The Algorithm Layer forms the foundation of StarryNight, providing Python functions that implement core image processing logic. This layer solves the fundamental problem of encapsulating scientific algorithms with minimal dependencies on infrastructure concerns, enabling reuse across different execution contexts and frameworks. By minimizing dependencies to essential utilities and templates, algorithms can be developed, tested, and validated with clear interfaces, ensuring that scientific logic remains focused and maintainable.

## Responsibilities

-   Implement standalone Python functions for image processing tasks
-   Organize algorithms by workflow type in `starrynight/src/starrynight/algorithms/`
    - Core workflows: `illum_calc`, `illum_apply`, `analysis`, `align`, `preprocess`
    - Specialized workflows: `segcheck`, `presegcheck`, `stitchcrop`, `inventory`, `index`
    - Shared execution: `cp.py` provides common CellProfiler execution
-   Maintain clear input/output contracts using standard Python types and cloudpathlib paths
-   NOT responsible for: Command-line interfaces, workflow orchestration, execution management, or any infrastructure concerns

## Key Design Decisions

1.  **Functional Independence (Decision #2)**: Algorithm functions minimize dependencies, importing only necessary utilities from `starrynight.utils`, `templates`, and `parsers`. This controlled dependency approach balances practical code reuse with maintaining clear boundaries. Core algorithm logic remains independent, while common utilities for data formatting and template rendering are shared.

2.  **Three-Function Pattern (Decision #7)**: CellProfiler-based algorithms follow a consistent pattern of LoadData generation (`gen_*_load_data`), Pipeline generation (`gen_*_cppipe`), and Execution (`run_cp`). The execution function is shared across all CellProfiler workflows, promoting code reuse. This standardization enables predictable integration while maintaining flexibility for non-CellProfiler algorithms.

## Interfaces

### Inputs

- File paths via cloudpathlib AnyPath (supporting local and cloud storage)
- Algorithm-specific parameters as primitive Python types
- Data structures using standard libraries (pandas/polars DataFrames, NumPy arrays)

### Outputs

- Processed data files written to specified paths
- Return values as standard Python types or None for side-effect operations
- Generated artifacts (CSV files, .cppipe definitions, processed images)

### Dependencies

- Internal dependencies: `starrynight.utils` (data formatting), `starrynight.templates` (template rendering), `starrynight.parsers` (file parsing)
- External dependencies: cloudpathlib, pandas/polars, NumPy, scikit-image, CellProfiler (for specific algorithms)

## Patterns

The algorithm layer follows consistent patterns for implementing image processing workflows. Here's the typical structure found in `starrynight/src/starrynight/algorithms/`:

### Three-Function Pattern

The pattern consists of three complementary functions that work together for CellProfiler workflows:

1.  **LoadData Generation** (`gen_*_load_data`): Reads input data, applies filtering and transformations, then writes a LoadData CSV file. These functions leverage shared utilities from `starrynight.utils` for consistent data formatting across workflows.

2.  **Pipeline Generation** (`gen_*_cppipe`): Configures CellProfiler modules, builds the processing pipeline, and saves the configuration. The template system from `starrynight.templates` ensures consistent pipeline generation while allowing workflow-specific customization.

3.  **Execution** (`run_cp`): A shared function that loads the pipeline, configures the execution context, and runs the processing. This common execution function is implemented in `starrynight/src/starrynight/algorithms/cp.py` and used by all CellProfiler-based algorithms.

This pattern enables consistent integration while maintaining flexibility for non-CellProfiler algorithms that may only need subset of these functions.

### Naming Conventions

Functions follow predictable naming patterns:

- `gen_*_load_data` for LoadData generation functions
- `gen_*_cppipe` for pipeline generation functions
- `run_*` for execution functions

### Path Handling

All paths use cloudpathlib's AnyPath for cloud/local compatibility, ensuring algorithms work seamlessly across different storage backends.

### Utility Delegation

Common operations are delegated to `starrynight.utils` modules, promoting code reuse and consistent behavior across algorithms.

### Separation of Concerns

Data preparation, pipeline configuration, and execution are kept as distinct functions, allowing flexible composition and testing of individual components.

## Implementation Location

All algorithm implementations can be found in:

- Primary location: `starrynight/src/starrynight/algorithms/`
- Tests: `starrynight/tests/algorithms/`

Each algorithm file typically contains the relevant functions for its workflow, following the patterns described above.

## See Also

- Next: [CLI Layer](02-cli.md)
