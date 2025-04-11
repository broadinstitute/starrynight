# StarryNight Testing Strategy

## Overview

This document outlines our structured approach to validate StarryNight against the reference PCPIP implementation. We'll use a progressive validation strategy, incrementally testing components before integrating them into the complete system.

## Testing Stages

### Stage 1: Pipeline Graph Topology Validation
- **Objective**: Verify that StarryNight pipelines have identical module dependency graphs compared to PCPIP
- **Approach**:
    - Use `cp_graph.py` to convert CellProfiler pipeline JSONs to DOT graph files
    - Compare generated DOT files against reference graphs in `_ref_graph_format/dot`
    - Validate module connections, data flow, and overall structure
- **Success Criteria**: Graph structural equivalence without requiring identical module settings

### Stage 2: LoadData CSV Generation Validation
- **Objective**: Ensure StarryNight generates compatible LoadData CSV files
- **Approach**:
    - Generate LoadData CSVs using StarryNight
    - Compare against reference LoadData CSVs using `compare_structures.py`
    - Validate CSV structure, headers, and key metadata fields
- **Success Criteria**: Functionally equivalent CSV files (allowing for formatting differences)

### Stage 3: Reference Pipeline Execution
- **Objective**: Run reference pipelines with reference LoadData and capture outputs
- **Approach**:
    - Execute reference CellProfiler pipelines using command-line invocation
    - Use `run_pcpip.sh` script to orchestrate multi-stage pipeline execution
    - Capture all outputs and file structures
- **Success Criteria**: Successful execution of all pipeline stages with expected outputs

### Stage 4: StarryNight Pipeline Execution
- **Objective**: Run StarryNight-generated pipelines with reference LoadData
- **Approach**:
    - Execute StarryNight-generated CellProfiler pipelines with identical inputs
    - Compare outputs against reference using `verify_file_structure.py` and `compare_structures.py`
    - Iterate on pipelines until outputs match
- **Success Criteria**: Outputs that match reference results (allowing for numerical differences)

### Stage 5: StarryNight End-to-End Testing
- **Objective**: Validate complete StarryNight workflow including orchestration
- **Approach**:
    - Execute StarryNight's CellProfiler invocation with StarryNight-generated LoadData
    - Compare against reference outputs
    - Iterate on orchestration system until outputs match
- **Success Criteria**: End-to-end process produces equivalent results to reference

## Testing Tools

1. **Structure Validation (`verify_file_structure.py`)**:
    - Validates file existence, sizes, and generates content fingerprints
    - Categories different file types (CSV, images, illumination files)
    - Reports detailed validation results in YAML format

2. **Structure Comparison (`compare_structures.py`)**:
    - Compares validation reports to identify differences
    - Hierarchical comparison (sections → sets → folders → types → files)
    - Supports multiple output formats (YAML, JSON, text)

3. **Pipeline Runner (`run_pcpip.sh`)**:
    - Orchestrates CellProfiler pipeline execution
    - Manages pipeline configuration and dependencies
    - Handles logging and parallel execution

4. **Graph Analysis (`cp_graph.py`)**:
    - Extracts module dependency graphs from pipelines
    - Visualizes data flow between modules
    - Supports structural comparison of pipelines

## Validation Documentation and Issue Tracking

### Documentation Structure
- Detailed validation procedures are maintained in version-controlled documentation:
  - `/docs/tester/pipeline-validations/`: Directory containing all pipeline validations
    - `/docs/tester/pipeline-validations/pipeline-validation-overview.md`: Overview of validation approach
    - `/docs/tester/pipeline-validations/pipeline-1-validation-illum-calc.md`: Pipeline 1 validation
  - `/docs/tester/tools/`: Directory containing testing tool documentation
    - `/docs/tester/tools/overview.md`: Overview of testing tools
    - `/docs/tester/tools/cp_graph.md`: cp_graph documentation
    - `/docs/tester/tools/verify_file_structure.md`: verify_file_structure documentation
    - `/docs/tester/tools/compare_structures.md`: compare_structures documentation
    - `/docs/tester/tools/run_pcpip.md`: run_pcpip documentation
  - `/docs/tester/testing-strategy.md`: General testing strategy (this document)

### Issue Tracking
- One GitHub issue will be created for each of the 7 CellProfiler pipelines
- Issues will link to the documentation and track high-level progress
- Issues provide a place for discussions while documentation provides detailed procedures
- Each issue will use a simple template that refers to the detailed documentation

## Test Dataset

We'll use the test fixture created in `/docs/tester/assets/pcpip-create-fixture` as our reference dataset. This provides a balance between:

- Being small enough for efficient testing
- Being representative enough to validate all features
- Having clear expected outputs for validation

## Success Factors

- **Structural Equivalence**: Maintaining identical data flow between modules
- **Functional Equivalence**: Producing comparable outputs (allowing for numerical differences)
- **Reproducibility**: Consistent results across executions
- **Traceability**: Clear documentation of validation results and issues

The goal is not byte-for-byte identical outputs, but functionally equivalent results that ensure StarryNight delivers the same scientific value as the original PCPIP implementation while providing a more maintainable and extensible architecture.
