# StarryNight Documentation Notes

## Project Structure
- StarryNight is a monorepo with four main packages:
  1. **StarryNight** (core) - Algorithms, CLI, Module system
  2. **PipeCraft** - Pipeline construction, execution backends
  3. **Conductor** - Job orchestration (minimally documented)
  4. **Canvas** - User interface (minimally documented)

## Documentation Structure
- Architecture documentation follows layered approach mirroring the system's layers
- Files numbered by layer (00-07)
- Original granular files were consolidated into layer-based documents (originals in _archive)
- Documentation focuses primarily on StarryNight core and PipeCraft packages
- The transcripts directory contains original content that informed documentation

## Architecture Layers
1. **00_architecture_overview.md** - Complete system overview with package structure
2. **01_algorithm_layer.md** - Foundation with pure Python functions
3. **02_cli_layer.md** - Command-line wrappers
4. **03_module_system.md** - Module abstraction (specs + compute graphs)
5. **04_pipeline_construction.md** - Module composition with Pipecraft
6. **05_execution_system.md** - Execution backends (Snakemake)
7. **06_experiment_configuration.md** - Parameter inference
8. **07_architecture_for_biologists.md** - Biologist-focused overview

## Key Architectural Principles
- **Algorithm Independence** - Pure functions with no dependencies on other components
- **Module Dual Focus** - Specs (using Bilayers) + compute graphs
- **Package Separation** - Pipeline definition in PipeCraft separate from algorithms
- **Backend-agnostic Execution** - Pipeline definition separate from execution
- **Automated Generation** - Complex workflows from simple definitions

## Related Code
- Main codebase: `../../starrynight/src/`
- Pipeline framework: `../../pipecraft/`
- Job orchestration: `../../conductor/`
- User interface: `../../canvas/`
- External libraries:
  - Bilayers: External library for schema definitions

## Document Standards
- Consistent structure with Overview, Purpose, Implementation, Examples
- Important information presented using annotations `{ .annotate }` rather than callouts
- Code examples with proper formatting
- Progressive disclosure (overview → concepts → details)
- Documentation scope/limitations stated upfront

## Key Components Reference
- **Algorithm Set**: Function group implementing specific pipeline step
- **Module**: Wrapper with spec and compute graph
- **Bilayers**: Schema system for module I/O
- **Pipecraft**: Library for composable pipeline graphs
- **Compute Graph**: Operations and relationships definition
- **Container**: Isolated execution environment
- **Snakemake**: Workflow engine executing compiled pipelines
