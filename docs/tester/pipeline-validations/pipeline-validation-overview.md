# Pipeline Validation Overview

This section contains detailed validation procedures for each of the 7 CellProfiler pipelines in the PCPIP workflow. Each validation document follows a consistent structure and process to ensure thorough testing and comparison between StarryNight implementations and reference PCPIP.

## Pipeline Mapping

| #   | Reference Pipeline                | StarryNight Module | Description                                  |
| --- | --------------------------------- | ------------------ | -------------------------------------------- |
| 1   | ref_1_CP_Illum.cppipe             | illum_calc         | Illumination correction function calculation |
| 2   | ref_2_CP_Apply_Illum.cppipe       | illum_apply        | Apply illumination correction to images      |
| 3   | ref_3_CP_SegmentationCheck.cppipe | segcheck           | Quality control on segmentation              |
| 5   | ref_5_BC_Illum.cppipe             | sbs_illum_calc     | Seq-based illumination calculation           |
| 6   | ref_6_BC_Apply_Illum.cppipe       | sbs_illum_apply    | Apply seq-based illumination correction      |
| 7   | ref_7_BC_Preprocess.cppipe        | preprocess         | Preprocessing for barcode calling            |
| 9   | ref_9_Analysis.cppipe             | analysis           | Final analysis and measurements              |

## Validation Process

Each pipeline validation follows a standardized 5-stage process:

1. **Graph Topology Validation**: Compare the dependency graphs between StarryNight and reference pipelines
2. **LoadData Generation**: Verify StarryNight generates compatible LoadData CSVs
3. **Reference Execution**: Run reference pipelines with reference LoadData to establish baseline
4. **StarryNight Pipeline**: Run StarryNight-generated pipelines with reference LoadData
5. **End-to-End**: Execute complete StarryNight workflow and compare with reference

## Validation Document Structure

Each pipeline validation document follows a consistent structure:

- **Pipeline Overview**: Basic information about the pipeline and module
- **Validation Status**: Tracking checkboxes for each stage
- **Setup and Environment**: Environment variables and paths
- **Detailed Procedures**: Commands and instructions for each stage
- **Results and Discrepancies**: Track findings and resolutions
- **Implementation Notes**: Technical details specific to the module

## Creating New Validation Documents

To create a validation document for a new pipeline:

1. Copy the most recent pipeline validation document
2. Update all references to the specific pipeline (pipeline number, paths, module names)
3. Adjust environment variables, reference paths, and commands
4. Add module-specific implementation notes

## GitHub Issue Tracking

Each pipeline validation has a corresponding GitHub issue that:
- Tracks high-level progress using checkboxes
- Links to the detailed documentation
- Serves as a discussion forum for validation issues
- Summarizes current status and discrepancies

## Available Validations

- [Pipeline 1: illum_calc](pipeline-1-validation-illum-calc.md) - Illumination correction function calculation
