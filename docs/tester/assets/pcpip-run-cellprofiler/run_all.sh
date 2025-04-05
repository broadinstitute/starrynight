#!/bin/bash
#
# run_all.sh - CellProfiler Pipeline Runner
#
# Description:
#   This script automates the execution of multiple CellProfiler pipelines in sequence,
#   applying them to plate/well/site data according to a predefined workflow.
#   The script uses a single configuration structure to manage all pipeline parameters
#   and execution options, making it easier to maintain and extend.
#
# Usage:
#   ./run_all.sh
#
# Configuration:
#   The script uses a multi-dimensional associative array (PIPELINE_CONFIG) to store
#   all configuration parameters for each pipeline. Each pipeline has the following
#   configuration options:
#
#   - [pipeline,file]: Pipeline file name
#   - [pipeline,data]: Data file name
#   - [pipeline,output]: Output directory pattern (with PLATE/WELL/SITE placeholders)
#   - [pipeline,group]: Group pattern for -g flag (with placeholders)
#   - [pipeline,params]: Required parameters (comma-separated)
#   - [pipeline,metadata]: Whether metadata directory is needed (true/false)
#   - [pipeline,background]: Whether to run in background (true/false)
#   - [pipeline,plugins]: Whether plugins are needed (true/false)
#
# Adding a new pipeline:
#   1. Add entries for the new pipeline number in the PIPELINE_CONFIG array
#   2. Create a new section at the bottom of the script that:
#      a. Sets the PIPELINE variable to the new number
#      b. Sets up any required loop variables (WELL, SITE, SBSCYCLE)
#      c. Calls run_pipeline
#      d. Calls wait if the pipeline runs in background
#
# Notes:
#   - This script currently uses a single plate value for simplicity. The pattern
#     substitution system can easily support multiple plates by:
#     1. Changing PLATE="Plate1" to PLATES=("Plate1" "Plate2" "PlateN")
#     2. Adding an outer loop: for PLATE in "${PLATES[@]}"; do ... done
#     3. No changes to the pattern substitution or function calls are needed
#
# Dependencies:
#   - CellProfiler
#

STARRYNIGHT_REPO_REL="../../../.."
LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/starrynight_example_output_baseline/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"
REPRODUCE_DIR="${STARRYNIGHT_REPO_REL}/scratch/reproduce_starrynight_example_output_baseline"
METADATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/starrynight_example_input/Source1/workspace/metadata"

PIPELINE_DIR="../pcpip-pipelines"

# Create a timestamp for this run
TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")

# Directory for logs with timestamp
LOG_DIR="${REPRODUCE_DIR}/logs/${TIMESTAMP}"
mkdir -p ${LOG_DIR}

PLATE=Plate1
WELLS=("WellA1" "WellA2" "WellB1")
SITES=(0 1)
SBSCYCLES=(1 2 3)

# Define all pipeline configurations
declare -A PIPELINE_CONFIG=(
  # Pipeline file names
  [1,file]="ref_1_CP_Illum.cppipe"
  [2,file]="ref_2_CP_Apply_Illum.cppipe"
  [3,file]="ref_3_CP_SegmentationCheck.cppipe"
  [5,file]="ref_5_BC_Illum.cppipe"
  [6,file]="ref_6_BC_Apply_Illum.cppipe"
  [7,file]="ref_7_BC_Preprocess.cppipe"
  [9,file]="ref_9_Analysis.cppipe"

  # Data files
  [1,data]="load_data_pipeline1.csv"
  [2,data]="load_data_pipeline2.csv"
  [3,data]="load_data_pipeline3.csv"
  [5,data]="load_data_pipeline5.csv"
  [6,data]="load_data_pipeline6.csv"
  [7,data]="load_data_pipeline7.csv"
  [9,data]="load_data_pipeline9.csv"

  # Output directory patterns
  [1,output]="illum/PLATE"
  [2,output]="images_corrected/painting/PLATE-WELL"
  [3,output]="images_segmentation/PLATE-WELL"
  [5,output]="illum/PLATE"
  [6,output]="images_aligned/barcoding/PLATE-WELL-SITE"
  [7,output]="images_corrected/barcoding/PLATE-WELL-SITE"
  [9,output]="../workspace/analysis/Batch1/PLATE-WELL-SITE"

  # Log filename patterns (only include relevant parameters for each pipeline)
  [1,log]="pipeline1_PLATE"
  [2,log]="pipeline2_PLATE_WELL"
  [3,log]="pipeline3_PLATE_WELL"
  [5,log]="pipeline5_PLATE_SBSCYCLE"
  [6,log]="pipeline6_PLATE_WELL_SITE"
  [7,log]="pipeline7_PLATE_WELL_SITE"
  [9,log]="pipeline9_PLATE_WELL_SITE"

  # Group patterns
  [1,group]="Metadata_Plate=PLATE"
  [2,group]="Metadata_Plate=PLATE,Metadata_Well=WELL"
  [3,group]="Metadata_Plate=PLATE,Metadata_Well=WELL"
  [5,group]="Metadata_Plate=PLATE,Metadata_SBSCycle=SBSCYCLE"
  [6,group]="Metadata_Plate=PLATE,Metadata_Well=WELL,Metadata_Site=SITE"
  [7,group]="Metadata_Plate=PLATE,Metadata_Well=WELL,Metadata_Site=SITE"
  [9,group]="Metadata_Plate=PLATE,Metadata_Well=WELL,Metadata_Site=SITE"

  # Required parameters (comma-separated)
  [1,params]="PLATE"
  [2,params]="PLATE,WELL"
  [3,params]="PLATE,WELL"
  [5,params]="PLATE,SBSCYCLE"
  [6,params]="PLATE,WELL,SITE"
  [7,params]="PLATE,WELL,SITE"
  [9,params]="PLATE,WELL,SITE"

  # Needs metadata flag (true/false)
  [1,metadata]="false"
  [2,metadata]="false"
  [3,metadata]="false"
  [5,metadata]="false"
  [6,metadata]="false"
  [7,metadata]="true"
  [9,metadata]="true"

  # Run in background (true/false)
  [1,background]="false"
  [2,background]="true"
  [3,background]="true"
  [5,background]="true"
  [6,background]="true"
  [7,background]="true"
  [9,background]="true"

  # Needs plugins (true/false)
  [1,plugins]="false"
  [2,plugins]="false"
  [3,plugins]="false"
  [5,plugins]="false"
  [6,plugins]="false"
  [7,plugins]="true"
  [9,plugins]="true"
)

# Function to apply variable substitution to a pattern
# Replaces placeholders (PLATE, WELL, SITE, SBSCYCLE) with their values
# if those variables are currently defined in the environment
#
# Parameters:
#   $1: Pattern string with placeholders
#
# Returns:
#   Pattern with placeholders replaced with actual values
apply_pattern() {
  local pattern=$1
  local result=$pattern

  # Apply all available substitutions
  result=${result//PLATE/$PLATE}

  if [[ -n "$WELL" ]]; then
    result=${result//WELL/$WELL}
  fi

  if [[ -n "$SITE" ]]; then
    result=${result//SITE/$SITE}
  fi

  if [[ -n "$SBSCYCLE" ]]; then
    result=${result//SBSCYCLE/$SBSCYCLE}
  fi

  echo "$result"
}

# Function to generate a log filename based on pipeline and parameters
# This creates descriptive log filenames containing all relevant parameters
#
# Parameters:
#   $1: Pipeline number
#   $2: PLATE value (required)
#   $3: WELL value (optional)
#   $4: SITE value (optional)
#   $5: SBSCYCLE value (optional)
#
# Returns:
#   Log filename with path
get_log_filename() {
  local pipeline=$1
  local plate=$2
  local well=$3
  local site=$4
  local sbscycle=$5
  local log_name="pipeline${pipeline}"

  # Add each defined parameter to the filename
  if [[ -n "$plate" ]]; then
    log_name="${log_name}_plate${plate}"
  fi

  if [[ -n "$well" ]]; then
    log_name="${log_name}_${well}"
  fi

  if [[ -n "$site" ]]; then
    log_name="${log_name}_site${site}"
  fi

  if [[ -n "$sbscycle" ]]; then
    log_name="${log_name}_cycle${sbscycle}"
  fi

  echo "${LOG_DIR}/${log_name}.log"
}

# Function to run a command with logging
# Redirects both stdout and stderr to a log file
#
# Parameters:
#   $1: Command to run
#   $2: Log filename
#   $3: Whether to run in background (true/false)
run_with_logging() {
  local cmd=$1
  local log_file=$2
  local run_bg=$3

  # Create log directory if it doesn't exist
  mkdir -p "$(dirname "$log_file")"

  # Add header to log file with timestamp and command
  {
    echo "===================================================="
    echo "  STARTED: $(date)"
    echo "  COMMAND: $cmd"
    echo "===================================================="
    echo ""
  } > "$log_file"

  # Run the command and log output
  if [[ "$run_bg" == "true" ]]; then
    # For background processes, redirect output to log
    eval "$cmd" >> "$log_file" 2>&1 &
  else
    # For foreground processes, redirect output to log
    eval "$cmd" >> "$log_file" 2>&1
  fi

  # Log completion for foreground processes
  if [[ "$run_bg" != "true" ]]; then
    {
      echo ""
      echo "===================================================="
      echo "  COMPLETED: $(date)"
      echo "  EXIT CODE: $?"
      echo "===================================================="
    } >> "$log_file"
  fi
}

# Function to run a pipeline with the right parameters
# This function builds and executes the cellprofiler command based on
# the configuration for the specified pipeline number
#
# Parameters:
#   $1: Pipeline number
#
# Environment:
#   Uses global variables (PLATE, WELL, SITE, SBSCYCLE) depending on
#   which pipeline is being run
run_pipeline() {
  local pipeline=$1
  local required_params=${PIPELINE_CONFIG[$pipeline,params]}
  local use_metadata=${PIPELINE_CONFIG[$pipeline,metadata]}
  local run_background=${PIPELINE_CONFIG[$pipeline,background]}
  local use_plugins=${PIPELINE_CONFIG[$pipeline,plugins]}

  # Build the basic command
  local cmd="cellprofiler -c -L 10"

  # Add group parameter
  cmd+=" -g \"$(apply_pattern "${PIPELINE_CONFIG[$pipeline,group]}")\""

  # Add metadata path if needed
  if [[ "$use_metadata" == "true" ]]; then
    cmd+=" -i ${METADATA_DIR}/"
  fi

  # Add pipeline, data file and output directory
  cmd+=" --pipeline ${PIPELINE_DIR}/${PIPELINE_CONFIG[$pipeline,file]}"
  cmd+=" --data-file ${LOAD_DATA_DIR}/${PIPELINE_CONFIG[$pipeline,data]}"
  cmd+=" --output-directory $(apply_pattern "${REPRODUCE_DIR}/Source1/Batch1/${PIPELINE_CONFIG[$pipeline,output]}")"

  # Add plugins if needed
  if [[ "$use_plugins" == "true" ]]; then
    cmd+=" --plugins-directory ${STARRYNIGHT_REPO_REL}/plugins/CellProfiler-plugins/active_plugins/"
  fi

  # Get log filename using pattern substitution
  local log_pattern=${PIPELINE_CONFIG[$pipeline,log]}
  local log_file="${LOG_DIR}/$(apply_pattern "$log_pattern").log"

  # Log the command execution
  echo "Running pipeline $pipeline, logging to: $log_file"

  # Run with logging
  run_with_logging "$cmd" "$log_file" "$run_background"
}

# Pipeline execution sequence
# --------------------------
# Each section sets up the required variables for a pipeline and calls run_pipeline

# 1_CP_Illum - PLATE only
PIPELINE=1
run_pipeline $PIPELINE

# 2_CP_Apply_Illum - PLATE, WELL
PIPELINE=2
for WELL in "${WELLS[@]}"; do
    run_pipeline $PIPELINE
done
wait

# 3_CP_SegmentationCheck - PLATE, WELL
PIPELINE=3
for WELL in "${WELLS[@]}"; do
    run_pipeline $PIPELINE
done
wait

# 5_BC_Illum - PLATE, SBSCYCLE
PIPELINE=5
for SBSCYCLE in "${SBSCYCLES[@]}"; do
    run_pipeline $PIPELINE
done
wait

# 6_BC_Apply_Illum - PLATE, WELL, SITE
PIPELINE=6
for WELL in "${WELLS[@]}"; do
    for SITE in "${SITES[@]}"; do
        run_pipeline $PIPELINE
    done
done
wait

# 7_BC_Preprocess - PLATE, WELL, SITE
PIPELINE=7
for WELL in "${WELLS[@]}"; do
    for SITE in "${SITES[@]}"; do
        run_pipeline $PIPELINE
    done
done
wait

# 9_Analysis - PLATE, WELL, SITE
PIPELINE=9
for WELL in "${WELLS[@]}"; do
    for SITE in "${SITES[@]}"; do
        run_pipeline $PIPELINE
    done
done
wait
