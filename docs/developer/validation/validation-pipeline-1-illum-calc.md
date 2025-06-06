# Pipeline Validation: 1_CP_Illum (illum_calc)

> **IMPORTANT: Code Migration Notice**
> All implementation code has been moved from `/docs/tester/assets/` to the `/tests/` directory as part of the documentation refactoring plan. This document has been updated to reference the new locations.

## Pipeline Overview

- **Reference Pipeline**: `ref_1_CP_Illum.cppipe`
- **StarryNight Module**: `illum_calc`
- **Description**: Calculates illumination correction functions to normalize uneven lighting patterns across Cell Painting channels specifically. Barcoding/SPS channels are handled separately by Pipeline 5. See [PCPIP documentation](../legacy/pcpip-specs.md) for details on all pipelines.

## Validation Status

- [ ] **Stage 1 - Graph Topology**
- [ ] **Stage 2 - LoadData Generation**
- [ ] **Stage 3 - Reference Execution**
- [ ] **Stage 4 - StarryNight Pipeline**
- [ ] **Stage 5 - End-to-End**

## Setup and Environment
Set up required environment variables before running any commands:

```sh
# Base directories
export STARRYNIGHT_REPO="$(git rev-parse --show-toplevel)"
export WKDIR="./scratch/starrynight_example_output/workspace"

# Reference data locations
export REF_PIPELINE="${STARRYNIGHT_REPO}/tests/pcpip-pipelines/ref_1_CP_Illum.cppipe"
export REF_GRAPH="${STARRYNIGHT_REPO}/tests/pcpip-pipelines/_ref_graph_format/dot/ref_1_CP_Illum.dot"
export REF_LOADDATA="${STARRYNIGHT_REPO}/scratch/pcpip_example_output/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed/load_data_pipeline1.csv"

# StarryNight output locations
export SN_LOADDATA="${WKDIR}/cellprofiler/loaddata/cp/illum_calc/Batch1/illum_calc_Batch1_Plate1.csv"
export SN_PIPELINE_DIR="${WKDIR}/cellprofiler/cppipe/cp/illum_calc"  # Directory containing pipeline files
export SN_PIPELINE_CPPIPE="${SN_PIPELINE_DIR}/illum_calc_painting.cppipe"  # CellProfiler pipeline file
export SN_PIPELINE_JSON="${SN_PIPELINE_DIR}/illum_calc_painting.json"  # JSON representation
export SN_PIPELINE_DOT="${SN_PIPELINE_DIR}/illum_calc_painting.dot"
export SN_PIPELINE_PNG="${SN_PIPELINE_DIR}/illum_calc_painting.png"
export SN_PIPELINE_VISUAL_DOT="${SN_PIPELINE_DIR}/illum_calc_painting_visual.dot"
export SN_OUTPUT="${WKDIR}/illum/cp/illum_calc"

# Validation outputs
export VALIDATION_DIR="${WKDIR}/validation/illum_calc"
export REF_OUTPUT="${VALIDATION_DIR}/reference_output"
export SN_TEST_OUTPUT="${VALIDATION_DIR}/starrynight_output"
export EMBEDDING_DIR="${VALIDATION_DIR}/embeddings"

# Make validation directories
mkdir -p ${VALIDATION_DIR}
mkdir -p ${EMBEDDING_DIR}
```

## Reference Materials
- Reference Pipeline: <https://github.com/broadinstitute/starrynight/blob/main/tests/pcpip-pipelines/ref_1_CP_Illum.cppipe>
- Reference Graph: <https://github.com/broadinstitute/starrynight/blob/main/tests/pcpip-pipelines/_ref_graph_format/dot/ref_1_CP_Illum.dot>
- Reference JSON: <https://github.com/broadinstitute/starrynight/blob/main/tests/pcpip-pipelines/_ref_graph_format/json/ref_1_CP_Illum.json>
- Test Dataset: `${STARRYNIGHT_REPO}/starrynight_example_input/`, created using [pcpip-create-fixture](https://github.com/broadinstitute/starrynight/tree/main/tests/pcpip-fixtures)
- Reference LoadData CSV: `${STARRYNIGHT_REPO}/scratch/pcpip_example_output/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed/load_data_pipeline1.csv`, created using [pcpip-create-fixture](https://github.com/broadinstitute/starrynight/tree/main/tests/pcpip-fixtures)

## Stage 1: Graph Topology
**Objective**: Verify StarryNight pipeline structure matches reference

**StarryNight Command**:
```sh
# Generate pipeline
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum_calc/ \
    -o ${SN_PIPELINE_DIR} \
    -w ${WKDIR}

# Note: StarryNight automatically generates JSON version alongside the .cppipe file
```

**Comparison Command**:
```sh
# First get the cp_graph.py tool (if not already available)
# From: https://github.com/shntnu/cp_graph/blob/v0.8.0/cp_graph.py

# 1. Generate ultra-minimal DOT graph for exact comparison
# See README.md for more information on cp_graph.py usage
uv run --script cp_graph.py ${SN_PIPELINE_JSON} ${SN_PIPELINE_DOT} --ultra-minimal

# 2. Generate visual DOT graph for human inspection
uv run --script cp_graph.py ${SN_PIPELINE_JSON} ${SN_PIPELINE_VISUAL_DOT}

# 3. Create PNG visualization from the visual DOT file
# Requires Graphviz to be installed
dot -Tpng ${SN_PIPELINE_VISUAL_DOT} -o ${SN_PIPELINE_PNG}

# 4. Compare generated DOT with reference for exact structural matching
diff ${SN_PIPELINE_DOT} ${REF_GRAPH}

# 5. Optional: Also generate PNG from reference for visual comparison
dot -Tpng ${REF_GRAPH} -o "${VALIDATION_DIR}/ref_1_CP_Illum.png"
```

**Results**:

```
# Results will be added here
```

**Discrepancies**:

- None identified yet

**Resolution**:

- None required yet

## Stage 2: LoadData Generation
**Objective**: Verify StarryNight generates compatible LoadData CSVs

**StarryNight Command**:
```sh
# Generate LoadData files
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum_calc
```

**Comparison Command**:
```sh
# Compare sample StarryNight LoadData with reference
# Note: compare_structures.py expects two file structure YAML files
# For comparing CSVs directly, we should extract headers and row counts first

# Extract headers and row counts for both CSVs
python -c "
import csv
def compare_csv_structure(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        headers1 = next(csv.reader(f1))
        headers2 = next(csv.reader(f2))
        rows1 = sum(1 for _ in f1) + 1
        rows2 = sum(1 for _ in f2) + 1
    print(f'CSV Comparison:\\n- File 1: {file1}\\n  Headers: {len(headers1)}\\n  Rows: {rows1}\\n- File 2: {file2}\\n  Headers: {len(headers2)}\\n  Rows: {rows2}')
    print('Headers match:' if sorted(headers1) == sorted(headers2) else 'Headers differ:')
    if sorted(headers1) != sorted(headers2):
        print(f'  Only in file1: {set(headers1) - set(headers2)}')
        print(f'  Only in file2: {set(headers2) - set(headers1)}')
compare_csv_structure('${REF_LOADDATA}', '${SN_LOADDATA}')
" > ${VALIDATION_DIR}/loaddata_comparison.txt
```

**Results**:
```
# Results will be added here
```

**Discrepancies**:

- None identified yet

## Stage 3: Reference Execution
**Objective**: Establish baseline outputs from reference pipeline

**Command**:
```sh
# Note: The run_pcpip.sh script must be used to run PCPIP steps
# By default, outputs go to ${STARRYNIGHT_REPO}/scratch/reproduce_pcpip_example_output
# To modify output location, update the REPRODUCE_DIR variable in the script

# Run using run_pcpip.sh script
cd ${STARRYNIGHT_REPO}/tests/tools/
# First modify the script to output to the reference output location
sed -i.bak "s|REPRODUCE_DIR=.*|REPRODUCE_DIR=\"${REF_OUTPUT}\"|" run_pcpip.sh
# Run only pipeline 1
./run_pcpip.sh 1

# Validate the reference output structure
python ${STARRYNIGHT_REPO}/tests/tools/verify_file_structure.py \
    --directory ${REF_OUTPUT} \
    --output ${VALIDATION_DIR}/reference_structure.yaml \
    --embedding-dir ${EMBEDDING_DIR}
```

**Results**:
```
# Results will be added here
```

## Stage 4: StarryNight-Generated Pipeline Execution
**Objective**: Verify StarryNight-generated CellProfiler pipeline with reference LoadData

**Command**:
```sh
# Modify run_pcpip.sh to use StarryNight-generated pipeline
cd ${STARRYNIGHT_REPO}/tests/tools/
# Make a copy for StarryNight testing
cp run_pcpip.sh run_starrynight.sh
# Update output directory and pipeline path in the script
sed -i.bak "s|REPRODUCE_DIR=.*|REPRODUCE_DIR=\"${SN_TEST_OUTPUT}\"|" run_starrynight.sh
# Update pipeline path in PIPELINE_CONFIG array - line ~80
sed -i.bak "s|1,file=.*|1,file=\"${SN_PIPELINE_CPPIPE}\"|" run_starrynight.sh
# Run the modified script
./run_starrynight.sh 1

# Validate the StarryNight output structure
python ${STARRYNIGHT_REPO}/tests/tools/verify_file_structure.py \
    --directory ${SN_TEST_OUTPUT} \
    --output ${VALIDATION_DIR}/starrynight_structure.yaml \
    --embedding-dir ${EMBEDDING_DIR}
```

**Comparison Command**:
```sh
# Compare reference and StarryNight output structures using multiple formats
# YAML format (default, machine-readable)
python ${STARRYNIGHT_REPO}/tests/tools/compare_structures.py \
    ${VALIDATION_DIR}/reference_structure.yaml \
    ${VALIDATION_DIR}/starrynight_structure.yaml \
    --output-file ${VALIDATION_DIR}/stage4_comparison.yaml \
    --compare-embeddings

# Text format (human-readable summary)
python ${STARRYNIGHT_REPO}/tests/tools/compare_structures.py \
    ${VALIDATION_DIR}/reference_structure.yaml \
    ${VALIDATION_DIR}/starrynight_structure.yaml \
    --output-file ${VALIDATION_DIR}/stage4_comparison.txt \
    --output-format text \
    --compare-embeddings
```

**Results**:
```
# Results will be added here
```

**Discrepancies**:
- None identified yet

## Stage 5: End-to-End
**Objective**: Verify complete StarryNight workflow

**Command**:
```sh
# Generate LoadData files
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum_calc

# Generate CellProfiler pipelines
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum_calc/ \
    -o ${SN_PIPELINE_DIR} \
    -w ${WKDIR}

# Execute pipelines
starrynight cp \
    -p ${SN_PIPELINE_DIR}/ \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum_calc \
    -o ${SN_OUTPUT}

# Note: In the future, the SN_OUTPUT path may need to be adjusted to match
# the expected output path structure from run_pcpip.sh for proper comparison

# Validate the StarryNight end-to-end output structure
python ${STARRYNIGHT_REPO}/tests/tools/verify_file_structure.py \
    --directory ${SN_OUTPUT} \
    --output ${VALIDATION_DIR}/e2e_structure.yaml \
    --embedding-dir ${EMBEDDING_DIR}
```

**Comparison Command**:
```sh
# Compare reference and StarryNight end-to-end output structures
# YAML format (default, machine-readable)
python ${STARRYNIGHT_REPO}/tests/tools/compare_structures.py \
    ${VALIDATION_DIR}/reference_structure.yaml \
    ${VALIDATION_DIR}/e2e_structure.yaml \
    --output-file ${VALIDATION_DIR}/e2e_comparison.yaml \
    --compare-embeddings

# Text format (human-readable summary)
python ${STARRYNIGHT_REPO}/tests/tools/compare_structures.py \
    ${VALIDATION_DIR}/reference_structure.yaml \
    ${VALIDATION_DIR}/e2e_structure.yaml \
    --output-file ${VALIDATION_DIR}/e2e_comparison.txt \
    --output-format text \
    --compare-embeddings

# Set custom tolerance for numerical differences (if needed)
python ${STARRYNIGHT_REPO}/tests/tools/compare_structures.py \
    ${VALIDATION_DIR}/reference_structure.yaml \
    ${VALIDATION_DIR}/e2e_structure.yaml \
    --output-file ${VALIDATION_DIR}/e2e_comparison_tolerance.yaml \
    --compare-embeddings \
    --tolerance 0.01
```

**Results**:
```
# Results will be added here
```

**Discrepancies**:
- None identified yet


## Test Runs
- **YYYY-MM-DD**: [Stage] - [Command] - [Result]
