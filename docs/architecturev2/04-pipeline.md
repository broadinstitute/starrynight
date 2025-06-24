# Pipeline Layer

!!! warning "Experimental - Not Reviewed"
    Content may be incomplete or inaccurate.

## Purpose

The Pipeline Layer orchestrates complete scientific workflows by composing individual modules into end-to-end processing pipelines. This layer solves the problem of expressing complex, multi-stage analyses that span from raw microscopy data to final measurements, while maintaining clarity about execution order, parallelism opportunities, and data dependencies. By building on Pipecraft's compute graph capabilities, the Pipeline Layer enables researchers to define reproducible workflows that can execute across different computational backends without modification.

## Responsibilities

- Compose modules into complete workflow definitions
- Define execution patterns including sequential and parallel processing blocks
- Integrate with Pipecraft to create executable compute graphs
- NOT responsible for: Implementing processing logic, managing actual execution, handling backend-specific details, or defining module internals

## Key Design Decisions

1.  **Pipecraft Integration (Decision #9)**: Pipelines are expressed as Pipecraft compute graphs rather than backend-specific formats. This abstraction enables critical capabilities: backend portability (same pipeline runs on local machines or cloud), execution optimization (automatic parallelization where possible), and workflow inspection (visualize before running). The integration maintains StarryNight's principle of separating workflow definition from execution strategy.

2.  **Module Composition (Decision #1)**: Following the layered architecture principle, pipelines compose modules without bypassing layers or accessing lower-level components directly. This ensures that pipelines remain high-level workflow definitions rather than detailed execution scripts. The composition pattern enables reuse of validated modules across different experimental contexts.

## Interfaces

### Inputs

- Module definitions from the Module Layer
- Pipeline configuration specifying module connections
- Execution patterns (sequential/parallel blocks)

### Outputs

- Complete Pipecraft compute graphs ready for execution
- Pipeline metadata for validation and inspection
- Workflow documentation and visualization

### Dependencies

- Internal dependencies: Module Layer for component definitions (following upward-only rule)
- External dependencies: Pipecraft for workflow representation

## Patterns

The Pipeline Layer follows a consistent pattern for composing modules into workflows:

### Pipeline Definition

Pipelines are defined as functions that return both a module list and a Pipecraft pipeline structure. The pattern initializes modules with configuration, composes them using Pipecraft's sequential and parallel primitives, and returns both the module list and pipeline structure for execution.

### Module Composition

The Pipeline Layer uses Pipecraft's composition primitives:

- **Seq**: Sequential execution of pipeline stages
- **Parallel**: Concurrent execution of independent branches
- **Pipeline**: Base abstraction for all pipeline components

### Registry Pattern

All available pipelines are registered in a central registry, enabling dynamic pipeline discovery and instantiation based on experiment requirements.

### Composition Structure

A typical Cell Painting pipeline demonstrates the composition pattern:

1. **Module Initialization**: Create module instances with experiment-specific parameters
2. **Parallel Preprocessing**: Cell Painting and SBS workflows run concurrently
3. **Sequential Analysis**: Final analysis steps execute after preprocessing completes
4. **Module Communication**: Data flows between modules through defined interfaces

The actual module types and their specific parameters vary based on the experiment configuration, but the composition pattern remains consistent across all pipeline implementations.

## Implementation Location

- Primary location: `starrynight/src/starrynight/pipelines/`
- Tests: `starrynight/tests/pipelines/`
- Registry: `starrynight/src/starrynight/pipelines/registry.py`
- Pipecraft primitives: `pipecraft/src/pipecraft/pipeline.py`

## See Also

- Previous: [Module Layer](03-module.md), Next: [Execution Layer](05-execution.md)
