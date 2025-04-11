# StarryNight Testing Framework

Welcome to the StarryNight testing framework! This is your comprehensive guide for validating, testing, and creating test fixtures for PCPIP (Pooled Cell Painting Image Processing) workflows.

## Introduction: Why Validation Matters

StarryNight reimagines the Pooled Cell Painting Image Processing (PCPIP) pipeline with a more maintainable architecture, but we must ensure scientific equivalence with the original implementation. The testing framework outlined here provides a systematic approach to verify that StarryNight produces functionally equivalent results to the reference PCPIP pipeline, giving users confidence in the transition.

**What is validation?** In this context, validation means comparing StarryNight outputs against the original PCPIP implementation at multiple levels:
- Pipeline structure comparison
- Output file verification
- Content similarity analysis
- End-to-end workflow execution

## Getting Started

This guide serves different types of testers. Find your path based on your role:

### I'm new to StarryNight testing

If you're new to the testing framework and want to understand the process:

1. **Start here**: Read the "Validation Approach" and "Validation Process Overview" sections below to understand the big picture
2. Look at the [Pipeline Validation Overview](pipeline-validations/pipeline-validation-overview.md) to see all the pipelines that need validation
3. Review [Pipeline 1 (illum_calc) Validation](pipeline-validations/pipeline-1-validation-illum-calc.md) as a concrete example with detailed commands
4. Explore the "Testing Tools" section below to understand the utilities available

### I need to validate a specific pipeline module

If you need to validate a specific StarryNight module:

1. Check the [Pipeline Validation Overview](pipeline-validations/pipeline-validation-overview.md) to find the corresponding pipeline
2. Follow the 5-stage validation process outlined in the "Validation Stages" section below
3. Use [Pipeline 1 (illum_calc) Validation](pipeline-validations/pipeline-1-validation-illum-calc.md) as a template
4. Create a new validation document for your module following the same structure

### I'm developing new validation tools

If you're developing tools for the testing framework:

1. Understand the existing tools in the "Testing Tools" section below
2. Review the "Reference Assets" section to understand available test fixtures
3. Follow the modular structure of existing tools for compatibility

## Validation Approach

Our validation strategy follows these key principles:

1. **Progressive Testing**: We validate each component individually before testing them together
2. **Multiple Levels of Comparison**: From pipeline structure to final outputs
3. **Tolerance for Non-Critical Differences**: Accept numerical differences while ensuring functional equivalence
4. **Documentation-Driven Development**: Clear testing procedures that can be reproduced by anyone

> **Core Principle**: The goal is not byte-for-byte identical outputs, but functionally equivalent results that ensure StarryNight delivers the same scientific value as the original PCPIP implementation.

## Reference Materials

The testing framework includes these key resources:

- [**Pipeline Validations**](pipeline-validations/pipeline-validation-overview.md): Detailed procedures for each pipeline
- [**pcpip-pipelines**](assets/pcpip-pipelines/README.md): Reference CellProfiler pipeline files
- [**pcpip-create-fixture**](assets/pcpip-create-fixture/README.md): Tools for creating test fixtures
- [**pcpip-test**](assets/pcpip-test/README.md): Scripts for pipeline execution and comparison

> **How We Track Validation Progress**: Each pipeline validation has a corresponding GitHub issue that links to the detailed documentation. The issue tracks high-level progress with checkboxes, while the documentation contains all technical details, results, and discrepancies. This approach separates discussion (in issues) from reference documentation (in markdown files).

## Validation Process Overview

The following diagram illustrates the 5-stage validation process and the key tools used at each stage:

```mermaid
graph TD
    subgraph "Stage 1: Graph Topology"
        A1[Reference Pipeline] -->|cp_graph.py| B1[Reference Graph]
        A2[StarryNight Pipeline] -->|cp_graph.py| B2[StarryNight Graph]
        B1 ---|diff| B2
    end

    subgraph "Stage 2: LoadData Generation"
        C1[Reference LoadData CSV]
        C2[StarryNight LoadData CSV]
        C1 ---|Python script| C2
    end

    subgraph "Stage 3: Reference Execution"
        D1[Reference Pipeline] -->|run_pcpip.sh| E1[Reference Output]
        E1 -->|verify_file_structure.py| F1[Reference Structure]
    end

    subgraph "Stage 4: StarryNight Pipeline"
        D2[StarryNight Pipeline] -->|run_pcpip.sh| E2[StarryNight Output]
        E2 -->|verify_file_structure.py| F2[StarryNight Structure]
        F1 ---|compare_structures.py| F2
    end

    subgraph "Stage 5: End-to-End"
        G1[StarryNight CLI] -->|starrynight commands| G2[End-to-End Output]
        G2 -->|verify_file_structure.py| G3[E2E Structure]
        F1 ---|compare_structures.py| G3
    end
```

## Validation Stages

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

This section provides a reference guide to the key tools used in StarryNight validation and testing.

### cp_graph

**Purpose**: Converts CellProfiler pipelines to graph representations for structural comparison.

**Source**: [cp_graph.py](https://github.com/shntnu/cp_graph) (external repository)

**Key Features**:
- Extracts pipeline structural information to DOT graph format
- Provides visualization of module connections and data flow
- Enables "ultra-minimal" mode for precise diff comparisons
- Ignores irrelevant differences (like module numbering) for meaningful comparison

**Usage in Validation**:
```bash
# Generate ultra-minimal graph for comparison (Stage 1)
uv run --script cp_graph.py pipeline.json pipeline.dot --ultra-minimal

# Generate visual graph (Stage 1)
uv run --script cp_graph.py pipeline.json pipeline_visual.dot

# Create PNG visualization
dot -Tpng pipeline_visual.dot -o pipeline.png
```

### verify_file_structure.py

**Purpose**: Validates file existence, sizes, and metadata against expected structures.

**Source**: [`docs/tester/assets/pcpip-test/verify_file_structure.py`](assets/pcpip-test/verify_file_structure.py)

**Key Features**:
- Semantic typing for different file categories (CSV, images, etc.)
- Detailed reporting on file existence, sizes, and metadata
- Optional embedding generation for content comparison
- Path replacement for comparing files in different locations

**Usage in Validation**:
```bash
# Validate output structure (Stages 3-5)
python verify_file_structure.py \
    --directory ${OUTPUT_DIR} \
    --output structure.yaml \
    --embedding-dir ${EMBEDDING_DIR}
```

### compare_structures.py

**Purpose**: Compares validation reports to identify detailed differences between file sets.

**Source**: [`docs/tester/assets/pcpip-test/compare_structures.py`](assets/pcpip-test/compare_structures.py)

**Key Features**:
- Hierarchical comparison (sections → sets → folders → types → files)
- Multiple output formats (YAML, JSON, text)
- Content-aware comparison using embeddings
- Tolerance settings for numerical differences

**Usage in Validation**:
```bash
# Compare output structures (Stages 4-5)
python compare_structures.py \
    reference_structure.yaml \
    target_structure.yaml \
    --output-file comparison.yaml \
    --compare-embeddings
```

### run_pcpip.sh

**Purpose**: Orchestrates the execution of CellProfiler pipelines for PCPIP workflows.

**Source**: [`docs/tester/assets/pcpip-test/run_pcpip.sh`](assets/pcpip-test/run_pcpip.sh)

**Key Features**:
- Pipeline configuration and dependency management
- Consistent execution environment
- Output path management
- Support for running individual pipelines

**Usage in Validation**:
```bash
# Execute reference pipeline (Stage 3)
cd docs/tester/assets/pcpip-test/
./run_pcpip.sh 1  # Run pipeline 1
```

### How These Tools Work Together

The validation process uses these tools in a coordinated workflow:

1. **Graph Comparison** (Stage 1):
   - Use `cp_graph.py` to generate graph representations of both reference and StarryNight pipelines
   - Compare with `diff` to identify structural differences

2. **LoadData Validation** (Stage 2):
   - Generate LoadData CSVs with StarryNight
   - Use Python or custom scripts to compare with reference LoadData CSVs

3. **Output Validation** (Stages 3-5):
   - Use `run_pcpip.sh` to execute reference pipelines
   - Use `verify_file_structure.py` to catalog outputs
   - Run StarryNight pipelines to generate comparable outputs
   - Use `compare_structures.py` to identify differences

## Issue Tracking

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

## Conclusion

Thorough validation is essential to ensure StarryNight can confidently replace the original PCPIP implementation. By following this structured approach, we build trust in the new architecture while preserving the scientific integrity of the pipeline.

For questions or suggestions about the testing framework, please create a GitHub issue or reach out to the team directly.
