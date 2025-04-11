# run_pcpip Tool

The `run_pcpip.sh` script orchestrates the execution of CellProfiler pipelines for PCPIP workflows. It manages pipeline configuration, dependencies, and execution flow to ensure consistent results.

## Core Functionality

- **Pipeline Orchestration**: Manages the execution of multiple pipelines
- **Configuration Management**: Handles pipeline settings and dependencies
- **Output Organization**: Controls output file locations and structure
- **Error Handling**: Gracefully handles pipeline failures
- **Logging**: Records execution details for troubleshooting

## Usage

```bash
./run_pcpip.sh [pipeline_number]
```

- Running without arguments executes all pipelines in sequence
- Specifying a pipeline number runs only that pipeline

## Pipeline Configuration

The script defines a configuration array (`PIPELINE_CONFIG`) that specifies:

- Pipeline execution order
- Pipeline file paths
- Pipeline dependencies
- Output directories
- Plate and well specifications

```bash
PIPELINE_CONFIG=(
  "1,pipeline_path=${REF_PIPELINE_DIR}/ref_1_CP_Illum.cppipe,output=illum/Plate1"
  "2,pipeline_path=${REF_PIPELINE_DIR}/ref_2_CP_Apply_Illum.cppipe,output=cp_image/Plate1"
  ...
)
```

## Environment Variables

The script uses several key environment variables:

- `STARRYNIGHT_REPO_REL`: Relative path to repository root
- `LOAD_DATA_DIR`: Directory containing LoadData CSV files
- `REPRODUCE_DIR`: Output directory for pipeline results
- `METADATA_DIR`: Directory containing metadata files

## Pipeline Execution Process

For each pipeline, the script:

1. Extracts configuration parameters from `PIPELINE_CONFIG`
2. Creates necessary output directories
3. Executes CellProfiler with the appropriate parameters
4. Handles plate and well specifications
5. Records execution status

## Customization

### Output Directory

By default, outputs go to `${STARRYNIGHT_REPO_REL}/scratch/reproduce_pcpip_example_output`. To modify the output location, update the `REPRODUCE_DIR` variable:

```bash
sed -i.bak "s|REPRODUCE_DIR=.*|REPRODUCE_DIR=\"/new/output/path\"|" run_pcpip.sh
```

### Pipeline Path

To use a different pipeline file, modify the relevant entry in the `PIPELINE_CONFIG` array:

```bash
sed -i.bak "s|1,pipeline_path=.*|1,pipeline_path=/path/to/new/pipeline.cppipe|" run_pcpip.sh
```

## Usage in Pipeline Validation

In the pipeline validation process, `run_pcpip.sh` is used primarily in Stages 3-4 to:

1. Execute reference pipelines to establish baseline outputs
2. Execute StarryNight-generated pipelines for comparison
3. Ensure consistent execution environment for both reference and StarryNight pipelines

For detailed usage examples, refer to the individual pipeline validation documents.
