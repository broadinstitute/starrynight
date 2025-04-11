# Testing Tools Overview

This section documents the essential tools used for StarryNight validation and testing. These tools provide systematic ways to compare StarryNight implementations with reference PCPIP implementations.

## Core Testing Tools

### cp_graph

The `cp_graph.py` tool converts CellProfiler pipelines into standardized graph representations for analyzing data flow and module dependencies. It enables precise comparison of pipeline structures while deliberately excluding module settings.

- **Primary Use**: Compare the topology of pipeline module connections
- **Key Features**:
  - Standardized graph representation
  - Visual output for human inspection
  - Ultra-minimal mode for exact comparison
  - Support for multiple output formats (DOT, PNG, etc.)
- [Detailed Documentation](cp_graph.md)

### verify_file_structure

The `verify_file_structure.py` tool validates file existence, sizes, and metadata against expected structures. It categorizes different file types and generates detailed validation reports.

- **Primary Use**: Verify pipeline output structure
- **Key Features**:
  - Semantic file typing (CSV, images, illumination files)
  - File size and existence checking
  - Embedding generation for content comparison
  - YAML report generation
- [Detailed Documentation](verify_file_structure.md)

### compare_structures

The `compare_structures.py` tool compares validation reports from `verify_file_structure.py` to identify detailed differences between file sets.

- **Primary Use**: Compare reference and StarryNight outputs
- **Key Features**:
  - Hierarchical comparison (sections → sets → folders → types → files)
  - Multiple output formats (YAML, JSON, text)
  - Content-aware comparison using embeddings
  - Tolerance settings for numerical differences
- [Detailed Documentation](compare_structures.md)

### run_pcpip

The `run_pcpip.sh` script orchestrates the execution of CellProfiler pipelines for PCPIP workflows.

- **Primary Use**: Run reference pipelines end-to-end
- **Key Features**:
  - Pipeline configuration and dependency management
  - Consistent execution environment
  - Output path management
  - Logging and error handling
- [Detailed Documentation](run_pcpip.md)

## How These Tools Work Together

The tools form a comprehensive validation workflow:

1. **Graph Comparison**: Use `cp_graph.py` to verify structural equivalence between pipeline implementations
2. **Execution**: Run pipelines with `run_pcpip.sh` to generate outputs
3. **Validation**: Use `verify_file_structure.py` to catalog and validate outputs
4. **Comparison**: Use `compare_structures.py` to identify and report differences

## Usage in Pipeline Validation

Each pipeline validation document uses these tools in a coordinated way:

- **Stage 1**: `cp_graph.py` for structural comparison
- **Stage 3/4**: `run_pcpip.sh` for pipeline execution
- **Stage 4/5**: `verify_file_structure.py` for output validation
- **Stage 4/5**: `compare_structures.py` for detailed comparison

For detailed usage examples, refer to the individual pipeline validation documents.
