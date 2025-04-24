# Value and Limitations of Pipeline Automation

This document explores the value and limitations of automating CellProfiler pipeline generation for the next generation of Pooled Cell Painting Image Processing (PCPIP). It explains different module customization categories, their customization requirements, and the overall importance of programmatic pipeline creation.

## Pipeline Structure Overview

The PCPIP workflow consists of two parallel tracks followed by integrated analysis:

1. **Cell Painting Track** (Pipelines 1-4): Processes morphological channels (e.g., DNA, Phalloidin, ZO1)
2. **Barcoding Track** (Pipelines 5-8): Processes genetic barcode channels (DAPI, A, C, G, T)
3. **Combined Analysis** (Pipeline 9): Integrates phenotype and genotype data

## Module Customization Categories

Pipeline modules can be categorized into five distinct types based on their customization requirements (see diagrams below for reference):

### 1. Base-Times-Cycle Barcoding Modules

**Description:**

- Modules that repeat once per base per cycle
- Highly repetitive with minor variations in channel references
- Most tedious to manually configure

**Specific Examples:**

- Pipeline 6 (BC_Apply_Illum): `SaveImages` modules. Module count = A,T,G,C,DAPI x # cycles

**Automation Value:** High for initial creation, but moderate overall since there are finite cycle counts (3-12)

![Pipeline_6_SaveImages](../assets/sample_modules/p6_SaveImages.png)

### 2. All-Cycles-In-One Barcoding Modules

**Description:**

- Modules that appear once but list all cycles in their settings
- Need updates to all cycle references when cycle count changes

**Specific Examples:**

- Pipeline 6 (BC_Apply_Illum): `CorrectIlluminationApply` modules. Module count = A,T,G,C,DAPI. Setting count/module = # cycles
- Pipeline 7 (BC_Preprocess): `CompensateColors` module. Module count = 1. Setting count/module = A,T,G,C,DAPI x # cycles.

**Automation Value:** High for initial creation, but moderate overall since there are finite cycle counts (3-12)

![Pipeline_6_CorrectIlluminationApply](../assets/sample_modules/p6_CorrectIlluminationApply.png)

![Pipeline_7_CompensateColors](../assets/sample_modules/p7_CompensateColors.png)

### 3. Cycle-Count-Parameter Barcoding Modules

**Description:**

- Modules with a single cycle count parameter
- Simple to update manually (just changing a number)

**Specific Examples:**

- Pipeline 9 (Analysis): `CallBarcodes` module. Module count = 1. Setting count/module = 1.

**Automation Value:** Low - these are trivial to update manually

![Pipeline_9_CallBarcodes](../assets/sample_modules/p9_CallBarcodes.png)

### 4. Phenotype Measurement Modules

**Description:**

- Need adjustment for channel names but follow standard patterns
- Consistent structure across experiments
- CellProfiler often catches configuration errors

**Specific Examples:**

- Pipeline 2 (CP_Apply_Illum): `CorrectIlluminationApply` modules. Module count = 1. Setting count/module = # channels.
- Pipeline 9 (Analysis): `MeasureObjectIntensity` modules (and all `Measure*` modules in general). Module count = 1. Setting count/module = # channels.

**Automation Value:** Moderate - useful templates but easy to manually adjust

![Pipeline_2_CorrectIlluminationApply](../assets/sample_modules/p2_CorrectIlluminationApply.png)

![Pipeline_9_MeasureObjectIntensity1](../assets/sample_modules/p9_MeasureObjectIntensity1.png)


### 5. Phenotype Segmentation Modules

**Description:**

- Require expert tuning for each experiment
- Highly variable based on cell types and imaging conditions

**Specific Examples:**

- Pipeline 2 (CP_Apply_Illum): `IdentifyPrimaryObjects` module with manually tuned diameter ranges and thresholding methods
- Pipeline 9 (Analysis): `IdentifySecondaryObjects` module for cell segmentation that uses nuclei as seeds

**Automation Value:** Low - human expertise required regardless of automation

![Pipeline_2_IdentifyPrimaryObjects](../assets/sample_modules/p2_IdentifyPrimaryObjects.png)

![Pipeline_9_IdentifySecondaryObjects](../assets/sample_modules/p9_IdentifySecondaryObjects.png)

## Automation Priority

While automating pipeline generation would be beneficial, particularly for repetitive cycle-specific configurations, it's not a critical priority given:

1. **Bounded Problem Space:** The finite range of cycle counts (3-12) means templates for common configurations can cover most use cases.
2. **Existing Resources:** Pipelines for most common cycle counts already exist and can be adapted.
3. **Human Expertise Requirement:** The most complex pipeline elements require expert tuning regardless of automation.
4. **Reasonable Manual Effort:** Modifying pipelines for a new experiment typically takes only a couple of hours of work.
5. **Higher-Value Automation Targets:** Other areas offer greater automation benefits:
      - File-to-LoadData parsing
      - Workflow step chaining
      - QC report generation
      - Computing resource orchestration

## Addendum: Pipeline Diagrams

Pipeline 2 (CP_Apply_Illum)

![Pipeline 2: Cell Painting Apply Illumination](https://raw.githubusercontent.com/broadinstitute/starrynight/refs/heads/main/tests/pcpip-pipelines/_ref_graph_format/svg/ref_2_CP_Apply_Illum.svg)

Pipeline 6 (BC_Apply_Illum)

![Pipeline 6: Barcoding Apply Illumination](https://raw.githubusercontent.com/broadinstitute/starrynight/refs/heads/main/tests/pcpip-pipelines/_ref_graph_format/svg/ref_6_BC_Apply_Illum.svg)

Pipeline 7 (BC_Preprocess)

![Pipeline 7: Barcoding Preprocessing](https://raw.githubusercontent.com/broadinstitute/starrynight/refs/heads/main/tests/pcpip-pipelines/_ref_graph_format/svg/ref_7_BC_Preprocess.svg)

Pipeline 9 (Analysis)

![Pipeline 9: Analysis](https://raw.githubusercontent.com/broadinstitute/starrynight/refs/heads/main/tests/pcpip-pipelines/_ref_graph_format/svg/ref_9_Analysis.svg)
