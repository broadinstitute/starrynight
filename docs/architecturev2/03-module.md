# Module Layer

!!! warning "Experimental - Not Reviewed"
    Content may be incomplete or inaccurate.

## Purpose

The Module Layer provides standardized, composable units of work that bridge the gap between individual algorithm functions and complete workflows. This layer solves the problem of expressing complex multi-step operations in a backend-agnostic way by combining specifications (what needs to be done) with compute graphs (how execution flows). By maintaining a dual nature of declarative specifications through a schema system (derived from Bilayers) and executable graphs through Pipecraft, modules enable inspection, validation, and execution across different computational backends while preserving the simplicity of CLI-based invocation.

## Responsibilities

- Define module specifications using a schema system for inputs, outputs, and parameters
- Create compute graphs via Pipecraft to express execution dependencies and data flow
- Map to CLI command groups for consistent invocation patterns
- NOT responsible for: Implementing algorithms, managing workflow orchestration, handling backend-specific execution, or defining complete end-to-end pipelines

## Key Design Decisions

1.  **Dual Nature Design (Decision #4)**: Modules combine schema specifications (defining interfaces) with Pipecraft compute graphs (defining execution). The schema is derived from Bilayers but used locally through starrynight.modules.schema. This separation of "what" from "how" enables multiple critical capabilities: backend-agnostic execution, workflow inspection before running, parameter validation, and graph optimization. The specification defines the contract while the compute graph defines the implementation strategy.

2.  **CLI Invocation Pattern (Decision #3)**: Each module maps directly to a CLI command group, maintaining consistency between programmatic and command-line usage. This design ensures that modules can be invoked identically whether called from Python code, shell scripts, or workflow engines. The pattern reinforces the principle that modules are self-contained units executable in isolation.

## Interfaces

### Inputs

- Module specifications via schema system defining required parameters
- Data paths and configuration through standardized interfaces
- Dependencies from CLI layer commands

### Outputs

- Compute graphs consumable by Pipecraft
- Execution artifacts as defined in specifications
- Module metadata for pipeline composition

### Dependencies

**Internal dependencies:**

- CLI layer for command implementations (following upward-only rule)
- `starrynight.modules.schema` (derived from Bilayers)
- Module base class: `starrynight.modules.common.StarrynightModule`

**External dependencies:**

- Pipecraft for compute graphs

## Patterns

Modules in StarryNight follow a consistent pattern that combines declarative specifications with executable compute graphs. Every module inherits from `StarrynightModule` and implements four key methods. This dual nature pattern demonstrates how modules separate the contract (what inputs/outputs are expected) from the execution strategy (how work gets done through containerized steps). The pattern ensures CLI commands are invoked consistently, execution remains backend-agnostic through containerization, interfaces can be validated before execution, and modules remain composable into larger pipelines.

### Module Identity Pattern

A unique name and identifier for the module that establishes its identity within the system and enables registration in the module registry.

### Specification Pattern

Declarative interface definition using the schema system that defines inputs, outputs, parameters, and citations. This pattern provides a formal contract that can be validated before execution.

### Pipeline Creation Pattern

Compute graph construction via Pipecraft that specifies container-based execution with CLI commands. This pattern translates the declarative specification into an executable workflow.

### Unit of Work Pattern

Optional task decomposition for parallel execution. This pattern allows modules to split work into independent units that can be processed concurrently.

## Implementation Location

Primary location: `starrynight/src/starrynight/modules/`
Tests: `starrynight/tests/modules/`

Modules are organized by workflow type in subdirectories:

- `cp_illum_calc/` - Cell Painting illumination calculation modules
- `sbs_illum_calc/` - SBS illumination calculation modules
- `analysis/` - Analysis modules
- `stitchcrop/` - Stitching and cropping modules

Each module directory typically contains load data generation, pipeline generation, and execution modules. All available modules are registered in `starrynight/src/starrynight/modules/registry.py`.

## See Also

- Previous: [CLI Layer](02-cli.md), Next: [Pipeline Layer](04-pipeline.md)
