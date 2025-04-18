# StarryNight Documentation Notes

## Documentation Structure
- Architecture documentation follows layered approach mirroring the system's layers
- Files numbered by layer (00-07)
- Original granular files were consolidated into layer-based documents (originals in _archive)
- The transcripts directory contains original content that informed documentation

## Architecture Layers
1. **00_architecture_overview.md** - Complete system overview
2. **01_algorithm_layer.md** - Foundation with pure Python functions
3. **02_cli_layer.md** - Command-line wrappers
4. **03_module_system.md** - Module abstraction (specs + compute graphs)
5. **04_pipeline_construction.md** - Module composition with Pipecraft
6. **05_execution_system.md** - Execution backends (Snakemake)
7. **06_experiment_configuration.md** - Parameter inference
8. **07_architecture_for_biologists.md** - Biologist-focused overview

## Key Architectural Principles
- **Algorithm Independence** - Pure functions with no dependencies on StarryNight
- **Module Dual Focus** - Specs (using Bilayers) + compute graphs
- **Backend-agnostic Execution** - Pipeline definition separate from execution
- **Automated Generation** - Complex workflows from simple definitions

## Related Code
- Main codebase: `../../starrynight/src/`
- Additional libraries:
  - Pipecraft: `../../pipecraft/` (for pipeline composition)
  - Bilayers: External library for schema definitions

## Document Standards
- Consistent structure with Overview, Purpose, Implementation, Examples
- Critical Points emphasized
- Code examples with proper formatting
- Progressive disclosure (overview → concepts → details)

## Key Components Reference
- **Algorithm Set**: Function group implementing specific pipeline step
- **Module**: Wrapper with spec and compute graph
- **Bilayers**: Schema system for module I/O
- **Pipecraft**: Library for composable pipeline graphs
- **Compute Graph**: Operations and relationships definition
- **Container**: Isolated execution environment
- **Snakemake**: Workflow engine executing compiled pipelines
