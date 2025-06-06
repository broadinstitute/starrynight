# PCPIP Reference Pipelines

!!!warning "Reference Pipeline Maintenance"

    **This directory contains legacy reference pipelines that are no longer actively maintained.**

    For current reference pipelines, use: **`starrynight/src/starrynight/templates/cppipe/`**

    - The templates directory is the single source of truth for production pipeline templates
    - This test directory was synchronized one final time on 2025-01-06 for historical consistency
    - Future updates will only be made to the templates directory
    - This directory remains useful for historical reference and specialized test fixtures

A curated collection of CellProfiler pipelines that serve as references for the Pooled Cell Painting Image Processing (PCPIP) workflow.

## Introduction

This repository contains carefully selected reference implementations of CellProfiler pipelines for the PCPIP workflow. These reference pipelines document standard configurations and variations for processing pooled cell painting images, and may be used as test fixtures for the StarryNight pipeline parser and validation tools.

For full context, see the [original PCPIP repository pipelines](https://github.com/broadinstitute/pooled-cell-painting-image-processing/tree/6c34fdb1a07d85a54dbcdfb148ad3418025e6616/pipelines/12cycles).

> **Note on Pipeline Structures**: These pipelines have been reviewed as suitable test fixtures by the PCPIP workflow experts. While some pipelines use [unusual](https://github.com/broadinstitute/starrynight/issues/73#issuecomment-2831353285) approaches to object identification and handling (particularly in pipelines 3, 7, and 9), these aspects don't affect their suitability as test fixtures and reference implementations.

## Directory Structure

| Directory            | Description                                     |
| -------------------- | ----------------------------------------------- |
| `/` (root)           | Reference pipeline files (prefixed with `ref_`) |
| `_pcpip_12cycles/`   | Original 12-cycle pipelines from PCPIP          |
| `_refsource/`        | Source pipeline variants with comparison diffs  |
| `_ref_graph_format/` | Pipeline visualizations (JSON, DOT, SVG, PNG)   |

## Reference Pipelines Overview

The PCPIP workflow consists of the following pipeline stages, represented by the reference pipelines in this repository:

### 1. CP_Illum (`ref_1_CP_Illum.cppipe`)
Creates illumination correction functions for all cycles and channels. This is the first step in the workflow, which calculates illumination correction functions used in subsequent steps.

### 2. CP_Apply_Illum (`ref_2_CP_Apply_Illum.cppipe`)
Applies illumination correction functions to all cycles and channels. This pipeline corrects for uneven illumination in the raw images.

### 3. CP_SegmentationCheck (`ref_3_CP_SegmentationCheck.cppipe`)
Quality control step to verify cell segmentation. This pipeline identifies primary objects (nuclei) and checks segmentation quality. Note: This pipeline uses two `IdentifySecondaryObjects` modules for PreCells => Cells, which is an unusual approach but doesn't impact its effectiveness as a test fixture.

### 5. BC_Illum (`ref_5_BC_Illum.cppipe`)
Creates barcode-specific illumination correction functions. This pipeline calculates illumination correction specifically for barcode images.

### 6. BC_Apply_Illum (`ref_6_BC_Apply_Illum.cppipe`)
Applies illumination correction to barcode cycle images across all channels (DAPI, A, C, G, T). This pipeline not only corrects for uneven illumination but also performs image alignment between cycles to ensure proper barcode reading.

### 7. BC_Preprocess (`ref_7_BC_Preprocess.cppipe`)
Preprocesses barcode images for analysis. This pipeline prepares barcode images for subsequent analysis steps. Note: Contains some non-standard object handling approaches that don't affect outputs.

### 9. Analysis (`ref_9_Analysis.cppipe`)
Performs cellular analysis measurements. This pipeline identifies cells, measures features, and exports results. Similar to Pipeline 3, this uses some unusual object identification approaches that are appropriate for test fixtures but not necessarily representative of common workflows.

## Specialized Pipeline Variants

Some specialized variants demonstrate specific processing requirements:

### 6_BC_Apply_Illum_DebrisMask
A specialized variant of pipeline 6 developed for datasets with significant debris that requires masking. This pipeline demonstrates the extensibility requirements for StarryNight, showing how specialized processing steps can be swapped in to address dataset-specific challenges. While valuable as a reference for extensibility design, it is not required as a standard test fixture. See PCPIP `12cycle` [version](_pcpip_12cycles/6_BC_Apply_Illum_DebrisMask.cppipe).

### 7A_BC_Preprocess_Troubleshooting
A variant of pipeline 7 created for testing multiple CompensateColors parameter settings within a single pipeline execution. If StarryNight successfully implements module iteration capabilities, pipeline 7A becomes largely redundant. The 7A pipeline was created as a workaround for testing multiple parameters within a single pipeline execution. A truly modular system would allow iterative parameter testing without requiring specialized pipeline variants. See PCPIP `12cycle` [version](_pcpip_12cycles/7A_BC_Preprocess_Troubleshooting.cppipe).

## Visualization Resources

The `_ref_graph_format/` directory contains pipeline visualizations to aid in understanding pipeline structure:

- **JSON files**: Pipeline data exported from CellProfiler 4.2.8
- **DOT files**: Graph definitions for pipeline structure
- **SVG/PNG files**: Visual representations of pipeline workflows

These visualizations help understand pipeline structure without requiring CellProfiler installation.

!!!warning "Reference Pipeline Update 2025-01-06"

    The reference pipelines were updated to match the production template versions from `starrynight/src/starrynight/templates/cppipe/`. Key changes include:

    **Metadata tag standardization:**

    - `ref_5_BC_Illum.cppipe`: Changed from `SBSCycle` to `Cycle` metadata tag
    - `ref_6_BC_Apply_Illum.cppipe` and `ref_7_BC_Preprocess.cppipe`: Changed from `Well_Value` to `Well` metadata tag

    **Channel naming consistency:**

    - `ref_6_BC_Apply_Illum.cppipe` and `ref_7_BC_Preprocess.cppipe`: Changed from `DAPI` to `DNA` for DNA channel naming

    These changes ensure consistency between test fixtures and production templates, facilitating better validation and testing workflows.

!!!note "Pipeline Selection Details"

    Pipeline variants in `_refsource` are from `s3://BUCKET/projects/PROJECT/workspace/pipelines/BATCH`. These variants were compared to select the most appropriate reference implementations.

    ```sh
    cd _refsource
    diff 1_CP_Illum/1_CP_Illum.cppipe 1_CP_Illum/1_Illum_Plate1_Plate2.cppipe > 1_CP_Illum/1_CP_Illum__1_Illum_Plate1_Plate2.diff
    diff 2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe 2_CP_Apply_Illum/2_CP_Apply_Illum_Plate3_Plate4.cppipe > 2_CP_Apply_Illum/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff
    diff 3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate3_Plate4.cppipe 3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe > 3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate3_Plate4__3_CP_SegmentationCheck_Plate1_Plate2.diff
    diff 5_BC_Illum/5_BC_Illum.cppipe 5_BC_Illum/5_BC_Illum_byWell.cppipe > 5_BC_Illum/5_BC_Illum__5_BC_Illum_byWell.diff
    diff 7_BC_Preprocess/7_BC_Preprocess.cppipe 7_BC_Preprocess/7_BC_Preprocess_4.cppipe > 7_BC_Preprocess/7_BC_Preprocess__7_BC_Preprocess_4.diff
    diff 9_Analysis/9_Analysis.cppipe 9_Analysis/9_Analysis_Plate1_Plate2.cppipe > 9_Analysis/9_Analysis__9_Analysis_Plate1_Plate2.diff
    diff 9_Analysis/9_Analysis_foci.cppipe 9_Analysis/9_Analysis_Plate1_Plate2.cppipe > 9_Analysis/9_Analysis_foci__9_Analysis_Plate1_Plate2.diff
    diff 9_Analysis/9_Analysis_rerun.cppipe 9_Analysis/9_Analysis_Plate1_Plate2.cppipe > 9_Analysis/9_Analysis_rerun__9_Analysis_Plate1_Plate2.diff
    cd -
    ```

    After reviewing the diffs, these pipeline variants were selected:

    - `1_CP_Illum`: `1_Illum_Plate1_Plate2.cppipe`
    - `2_CP_Apply_Illum`: `2_CP_Apply_Illum.cppipe`
    - `3_CP_SegmentationCheck`: `3_CP_SegmentationCheck_Plate1_Plate2.cppipe`
    - `5_BC_Illum`: `5_BC_Illum.cppipe`
    - `6_BC_Apply_Illum`: `6_BC_Apply_Illum.cppipe`
    - `7_BC_Preprocess`: `7_BC_Preprocess.cppipe`
    - `9_Analysis`: `9_Analysis_Plate1_Plate2.cppipe`

!!!note "Reference Pipelines Creation"

    The selected pipeline variants were initially copied to create the reference pipelines:

    ```sh
    cp _refsource/1_CP_Illum/1_Illum_Plate1_Plate2.cppipe ref_1_CP_Illum.cppipe
    cp _refsource/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe ref_2_CP_Apply_Illum.cppipe
    cp _refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe ref_3_CP_SegmentationCheck.cppipe
    cp _refsource/5_BC_Illum/5_BC_Illum.cppipe ref_5_BC_Illum.cppipe
    cp _refsource/6_BC_Apply_Illum/6_BC_Apply_Illum.cppipe ref_6_BC_Apply_Illum.cppipe
    cp _refsource/7_BC_Preprocess/7_BC_Preprocess.cppipe ref_7_BC_Preprocess.cppipe
    cp _refsource/9_Analysis/9_Analysis_Plate1_Plate2.cppipe ref_9_Analysis.cppipe
    ```

    The reference pipelines were modified over time to:

    1. Drop cycles 4-10
    2. Replace `RunCellPose` with `IdentifyPrimaryObjects`
    3. Synchronize with production template versions (2025-01-06)

    You can view the commit history of specific pipeline files using GitHub, for example:
    ```
    git log --follow -- tests/pcpip-pipelines/ref_1_CP_Illum.cppipe
    ```

    Or view the history through GitHub's interface by clicking on a file and then selecting "History" or "Blame".


!!!note "Pipeline Comparison Details"

    Comparisons between reference pipeline sources and PCPIP 12-cycle pipelines were conducted using the following commands:

    ```sh
    mkdir -p _pcpip_12cycles/diff

    refsource_1="_refsource/1_CP_Illum/1_Illum_Plate1_Plate2.cppipe"
    pcpip_1="_pcpip_12cycles/1_CP_Illum.cppipe"
    diff_1="_pcpip_12cycles/diff/1_CP_Illum"
    diff -w ${refsource_1} ${pcpip_1} > ${diff_1}.diff

    refsource_2="_refsource/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe"
    pcpip_2="_pcpip_12cycles/2_CP_Apply_Illum.cppipe"
    diff_2="_pcpip_12cycles/diff/2_CP_Apply_Illum"
    diff -w ${refsource_2} ${pcpip_2} > ${diff_2}.diff

    refsource_3="_refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe"
    pcpip_3="_pcpip_12cycles/3_CP_SegmentationCheck.cppipe"
    diff_3="_pcpip_12cycles/diff/3_CP_SegmentationCheck"
    diff -w ${refsource_3} ${pcpip_3} > ${diff_3}.diff

    refsource_5="_refsource/5_BC_Illum/5_BC_Illum.cppipe"
    pcpip_5="_pcpip_12cycles/5_BC_Illum.cppipe"
    diff_5="_pcpip_12cycles/diff/5_BC_Illum"
    diff -w ${refsource_5} ${pcpip_5} > ${diff_5}.diff

    refsource_6="_refsource/6_BC_Apply_Illum/6_BC_Apply_Illum.cppipe"
    pcpip_6="_pcpip_12cycles/6_BC_Apply_Illum.cppipe"
    diff_6="_pcpip_12cycles/diff/6_BC_Apply_Illum"
    diff -w ${refsource_6} ${pcpip_6} > ${diff_6}.diff

    refsource_7="_refsource/7_BC_Preprocess/7_BC_Preprocess.cppipe"
    pcpip_7="_pcpip_12cycles/7_BC_Preprocess.cppipe"
    diff_7="_pcpip_12cycles/diff/7_BC_Preprocess"
    diff -w ${refsource_7} ${pcpip_7} > ${diff_7}.diff

    refsource_9="_refsource/9_Analysis/9_Analysis_Plate1_Plate2.cppipe"
    pcpip_9="_pcpip_12cycles/9_Analysis.cppipe"
    diff_9="_pcpip_12cycles/diff/9_Analysis"
    diff -w ${refsource_9} ${pcpip_9} > ${diff_9}.diff
    ```

    This was discussed further in [issue #68](https://github.com/broadinstitute/starrynight/issues/68#issuecomment-2780020724).


!!!note "Pipeline Visualization Generation"

    Files in `_ref_graph_format` were created using the following:

    - **JSON files**: Exported from CellProfiler 4.2.8
    - **DOT files**: Generated using [cp_graph](https://github.com/shntnu/cp_graph/blob/v0.10.0/cp_graph.py) tool
    - **SVG/PNG files**: Generated from DOT files using Graphviz

    ```sh
    cd _ref_graph_format/
    rm -rf dot dotmin png svg
    mkdir -p dot dotmin png svg

    CP_GRAPH="${HOME}/Documents/GitHub/cp_graph/cp_graph.py"
    ROOT_NODES_FILE=root_nodes.txt
    ROOT_NODES=$(cat ${ROOT_NODES_FILE}| tr ',' '\n' | paste -sd "," -)
    find json/ -name "*.json" | \
    parallel uv run --script ${CP_GRAPH} \
      {} \
      dot/{/.}.dot \
      --rank-nodes \
      --remove-unused-data \
      --exclude-module-types=ExportToSpreadsheet \
      --rank-ignore-filtered \
      --root-nodes=${ROOT_NODES}  # --highlight-filtered

    find dot -name "*.dot" | parallel dot -Gdpi=50 -Tpng {} -o png/{/.}.png

    find dot -name "*.dot" | parallel dot -Tsvg {} -o svg/{/.}.svg

    find json/ -name "*.json" | \
    parallel uv run --script ${CP_GRAPH} \
      {} \
      dotmin/{/.}.dot \
      --remove-unused-data \
      --exclude-module-types=ExportToSpreadsheet \
      --root-nodes=${ROOT_NODES} \
      --ultra-minimal # --highlight-filtered
    ```
