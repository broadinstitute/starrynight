# Pipeline Validation: 1_CP_Illum (illum_calc)

## Pipeline Overview
- **Reference Pipeline**: `ref_1_CP_Illum.cppipe`
- **StarryNight Module**: `illum_calc`
- **Description**: Calculates illumination correction functions to normalize uneven lighting patterns across microscopy images.

## Validation Status
- [ ] **Stage 1 - Graph Topology**
- [ ] **Stage 2 - LoadData Generation**
- [ ] **Stage 3 - Reference Execution**
- [ ] **Stage 4 - StarryNight Pipeline**
- [ ] **Stage 5 - End-to-End**

## Setup and Environment
Set up required environment variables before running any commands:

```bash
# Base directories
export STARRYNIGHT_REPO="$(git rev-parse --show-toplevel)"
export WKDIR="./scratch/starrynight_example_output/workspace"

# Reference data locations
export REF_PIPELINE="${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-pipelines/ref_1_CP_Illum.cppipe"
export REF_GRAPH="${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-pipelines/_ref_graph_format/dot/ref_1_CP_Illum.dot"
export REF_LOADDATA="${STARRYNIGHT_REPO}/scratch/pcpip_example_output/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed/load_data_pipeline1.csv"

# StarryNight output locations
export SN_LOADDATA="${WKDIR}/cellprofiler/loaddata/cp/illum_calc/Batch1/illum_calc_Batch1_Plate1.csv"
export SN_PIPELINE="${WKDIR}/cellprofiler/cppipe/cp/illum_calc"
export SN_PIPELINE_DOT="${SN_PIPELINE}/illum_calc_painting.dot"
export SN_JSON="${SN_PIPELINE}/illum_calc_painting.json"
export SN_OUTPUT="${WKDIR}/illum/cp/illum_calc"

# Validation outputs
export VALIDATION_DIR="${WKDIR}/validation/illum_calc"
export REF_OUTPUT="${VALIDATION_DIR}/reference_output"
export SN_TEST_OUTPUT="${VALIDATION_DIR}/starrynight_output"

# Make validation directories
mkdir -p ${VALIDATION_DIR}
```

## Reference Materials
- [Reference Pipeline](docs/tester/assets/pcpip-pipelines/ref_1_CP_Illum.cppipe)
- [Reference Graph](docs/tester/assets/pcpip-pipelines/_ref_graph_format/dot/ref_1_CP_Illum.dot)
- [Reference JSON](docs/tester/assets/pcpip-pipelines/_ref_graph_format/json/ref_1_CP_Illum.json)
- [Test Dataset](docs/tester/assets/pcpip-create-fixture)
- [Reference LoadData CSV](${STARRYNIGHT_REPO}/scratch/pcpip_example_output/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed/load_data_pipeline1.csv)

## Stage 1: Graph Topology
**Objective**: Verify StarryNight pipeline structure matches reference

**StarryNight Command**:
```bash
# Generate pipeline
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum_calc/ \
    -o ${SN_PIPELINE} \
    -w ${WKDIR}

# Note: StarryNight automatically generates JSON version alongside the .cppipe file
```

**Comparison Command**:
```bash
# First get the cp_graph.py tool (if not already available)
# From: https://github.com/shntnu/cp_graph/blob/v0.8.0/cp_graph.py

# FIXME: Read /Users/shsingh/Documents/GitHub/cp_graph/README.md carefully to see how we can also output the png files so we can also see it visually (and dont use ultra-minimal for that)

# Generate DOT graph from pipeline JSON with ultra-minimal flag
uv run --script cp_graph.py ${SN_JSON} ${SN_PIPELINE_DOT} --ultra-minimal

# Compare generated DOT with reference
diff ${SN_PIPELINE_DOT} ${REF_GRAPH}
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
```bash
# Generate LoadData files
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum_calc
```

**Comparison Command**:
```bash
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
```bash
# Note: The run_pcpip.sh script can be used to run specific PCPIP steps
# By default, outputs go to ${STARRYNIGHT_REPO}/scratch/reproduce_pcpip_example_output
# To modify output location, update the REPRODUCE_DIR variable in the script

# Option 1: Run using run_pcpip.sh script (recommended)
cd ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/
# First modify the script to output to the reference output location
sed -i.bak "s|REPRODUCE_DIR=.*|REPRODUCE_DIR=\"${REF_OUTPUT}\"|" run_pcpip.sh
# Run only pipeline 1
./run_pcpip.sh 1

# Option 2: Run directly with CellProfiler
cellprofiler -c -r \
    -p ${REF_PIPELINE} \
    -i $(dirname ${REF_LOADDATA}) \
    -o ${REF_OUTPUT}
```

**Results**:
```
# Results will be added here
```

## Stage 4: StarryNight Pipeline
**Objective**: Verify StarryNight pipeline with reference LoadData

**Command**:
```bash
# Option 1: Modify run_pcpip.sh to use StarryNight pipeline
cd ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/
# Make a copy for StarryNight testing
cp run_pcpip.sh run_starrynight.sh
# Update output directory and pipeline path in the script
sed -i.bak "s|REPRODUCE_DIR=.*|REPRODUCE_DIR=\"${SN_TEST_OUTPUT}\"|" run_starrynight.sh
# Update pipeline path in PIPELINE_CONFIG array - line ~80
# TODO: Use sed to update pipeline path
# Run the modified script
./run_starrynight.sh 1

# Option 2: Run directly with CellProfiler
cellprofiler -c -r \
    -p ${SN_PIPELINE}/*.cppipe \
    -i $(dirname ${REF_LOADDATA}) \
    -o ${SN_TEST_OUTPUT}
```

**Comparison Command**:
```bash
#FIXME: Read ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/README.md carefully to make sure these will work right
# Validate output structure and compare with reference
python ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/verify_file_structure.py \
    --directory ${SN_TEST_OUTPUT} \
    --output ${VALIDATION_DIR}/starrynight_structure.yaml

python ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/verify_file_structure.py \
    --directory ${REF_OUTPUT} \
    --output ${VALIDATION_DIR}/reference_structure.yaml

python ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/compare_structures.py \
    ${VALIDATION_DIR}/reference_structure.yaml \
    ${VALIDATION_DIR}/starrynight_structure.yaml \
    --output-file ${VALIDATION_DIR}/stage4_comparison.yaml
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
```bash
# Generate LoadData files
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum_calc

# Generate CellProfiler pipelines
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum_calc/ \
    -o ${SN_PIPELINE} \
    -w ${WKDIR}

# Execute pipelines
starrynight cp \
    -p ${SN_PIPELINE}/ \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum_calc \
    -o ${SN_OUTPUT}
```

**Comparison Command**:
```bash
#FIXME: Read ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/README.md carefully to make sure these will work right
# Validate output structure and compare with reference
python ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/verify_file_structure.py \
    --directory ${SN_OUTPUT} \
    --output ${VALIDATION_DIR}/e2e_structure.yaml

python ${STARRYNIGHT_REPO}/docs/tester/assets/pcpip-test/compare_structures.py \
    ${VALIDATION_DIR}/reference_structure.yaml \
    ${VALIDATION_DIR}/e2e_structure.yaml \
    --output-file ${VALIDATION_DIR}/e2e_comparison.yaml
```

**Results**:
```
# Results will be added here
```

**Discrepancies**:
- None identified yet

## Implementation Notes

### Key Module Requirements
- Processes microscopy images to generate background illumination functions
- Uses downsampling (0.25x) and upsampling (4x) with bilinear interpolation
- Supports both standard (batch/plate) and SBS (batch/plate/cycle) image structures
- Produces illumination correction files in .npy format

### Important Settings
- **Block Size**: 60 (median filtering for background model)
- **Filter Size**: 20 (smoothing parameter for illumination function)
- **Rescaling**: 0.25x downsampling for processing, 4x upsampling for output
- **Output Format**: NumPy (.npy) files for illumination functions

## Test Runs
- **YYYY-MM-DD**: [Stage] - [Command] - [Result]
