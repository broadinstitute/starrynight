# Testing Tools Reference

This document provides a reference guide to the key tools used in StarryNight validation and testing. Rather than duplicating documentation, this guide summarizes each tool's purpose, usage patterns, and where to find more detailed information.

## cp_graph

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

## verify_file_structure.py

**Purpose**: Validates file existence, sizes, and metadata against expected structures.

**Source**: [`docs/tester/assets/pcpip-test/verify_file_structure.py`](../assets/pcpip-test/verify_file_structure.py)

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

## compare_structures.py

**Purpose**: Compares validation reports to identify detailed differences between file sets.

**Source**: [`docs/tester/assets/pcpip-test/compare_structures.py`](../assets/pcpip-test/compare_structures.py)

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

## run_pcpip.sh

**Purpose**: Orchestrates the execution of CellProfiler pipelines for PCPIP workflows.

**Source**: [`docs/tester/assets/pcpip-test/run_pcpip.sh`](../assets/pcpip-test/run_pcpip.sh)

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

## How These Tools Work Together

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

## Example Command Sequences

See the pipeline validation documents for detailed command sequences for each stage:

- [Pipeline 1: illum_calc validation](../pipeline-validations/pipeline-1-validation-illum-calc.md)
- [Pipeline Validation Overview](../pipeline-validations/pipeline-validation-overview.md)
