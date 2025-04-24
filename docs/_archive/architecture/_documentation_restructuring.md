# StarryNight Documentation Restructuring

## Overview

This document summarizes the restructuring of the StarryNight architecture documentation. The documentation has been reorganized to follow the logical layer structure of the architecture, combining related files into comprehensive layer-specific documents.

## Restructuring Process

The original documentation consisted of individual component files that described specific aspects of the architecture. These have been reorganized into layer-based documents that provide a more coherent and comprehensive view of each architectural layer.

## New Documentation Structure

The new documentation structure organizes files by architectural layer:

1. **Architecture Overview** (`00_architecture_overview.md`) - Unchanged, already comprehensive
2. **Algorithm Layer** (`01_algorithm_layer.md`) - Expanded from algorithms_foundation
3. **CLI Layer** (`03_cli_layer.md`) - Derived from cli_integration
4. **Module System** (`04-05_module_system.md`) - Combined module_abstraction and bilayer_integration
5. **Pipeline Construction** (`05_pipeline_construction.md`) - Combined pipecraft_integration and pipeline_composition_execution
6. **Execution System** (`07-08_execution_system.md`) - Combined execution_model and snakemake_backend
7. **Experiment Configuration** (`09-11_experiment_configuration.md`) - Combined experiment_configuration and module_configuration

## Original Files and Their Mapping

| Original File                        | New Location                                        |
| ------------------------------------ | --------------------------------------------------- |
| 00_architecture_overview.md          | Unchanged                                           |
| 01_algorithms_foundation.md          | Incorporated into 01_algorithm_layer.md             |
| 03_cli_integration.md                | Incorporated into 03_cli_layer.md                   |
| 04_module_abstraction.md             | Incorporated into 04-05_module_system.md            |
| 05_bilayer_integration.md            | Incorporated into 04-05_module_system.md            |
| 06_pipecraft_integration.md          | Incorporated into 05_pipeline_construction.md       |
| 07_execution_model.md                | Incorporated into 07-08_execution_system.md         |
| 08_snakemake_backend.md              | Incorporated into 07-08_execution_system.md         |
| 09_experiment_configuration.md       | Incorporated into 09-11_experiment_configuration.md |
| 10_11_module_configuration.md        | Incorporated into 09-11_experiment_configuration.md |
| 12_pipeline_composition_execution.md | Incorporated into 05_pipeline_construction.md       |

## Document Characteristics

Each combined document follows a consistent structure:

1. **Table of Contents** - Detailed navigation of document contents
2. **Overview** - Introduction to the architectural layer
3. **Purpose** - Why this layer exists in the architecture
4. **Layer-Specific Sections** - Detailed explanations of components
5. **Examples** - Practical code examples
6. **Integration with Other Layers** - How the layer connects to others
7. **Conclusion** - Summary of key concepts
8. **Next Document Link** - Navigation to the next logical document

## Navigation Flow

The documents are designed to be read in sequence, following the architectural layers from bottom to top:

1. Architecture Overview
2. Algorithm Layer
3. CLI Layer
4. Module System
5. Pipeline Construction
6. Execution System
7. Experiment Configuration

This follows the natural progression from low-level implementation to high-level abstraction in the StarryNight architecture.

## Benefits of the New Structure

The restructured documentation offers several advantages:

1. **Logical Grouping** - Related concepts are presented together
2. **Improved Coherence** - Each layer is explained comprehensively
3. **Better Navigation** - Clearer structure for readers to follow
4. **Reduced Redundancy** - Combined overlapping explanations
5. **Consistent Format** - Unified structure across all documents
6. **Better Cross-Referencing** - More effective linking between related concepts

## Archive of Original Files

For reference, the original component-specific files have been preserved in the `archive/` directory:

```
architecture/
└── archive/
    ├── 03_cli_integration.md
    ├── 04_module_abstraction.md
    ├── 05_bilayer_integration.md
    ├── 06_pipecraft_integration.md
    ├── 07_execution_model.md
    ├── 08_snakemake_backend.md
    ├── 09_experiment_configuration.md
    ├── 10_11_module_configuration.md
    └── 12_pipeline_composition_execution.md
```

These archived files contain the original component-specific documentation that has been integrated into the new layer-based documents.

## Conclusion

The restructured documentation provides a more integrated view of the StarryNight architecture, focusing on logical layers rather than individual components. This approach better reflects the architectural design principles and should make the documentation more accessible and useful to developers working with the framework.

The layer-based documents should be considered the primary documentation source going forward, with the archived files available for historical reference if needed.
