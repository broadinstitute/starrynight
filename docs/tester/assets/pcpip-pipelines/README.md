# Pipelines

This document tracks the selection process for CellProfiler image analysis pipelines. It compares different pipeline versions, documents their differences, and records our decisions on which versions to use for the reference PCPIP workflow. The document includes diff commands, comparison notes, and final copy commands for the selected pipelines.

## Diffs

The pipelines in `_original` are from the `pipelines` directory of `s3://BUCKET/projects/PROJECT/workspace/pipelines/BATCH`

```bash
cd _original
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

## Selection

### 1_CP_Illum

[diff](_original/1_CP_Illum/1_CP_Illum__1_Illum_Plate1_Plate2.diff)

Differences: 1_CP_Illum.cppipe has downsampling/upsampling but 1_Illum_Plate1_Plate2.cppipe does not

Decision: `1_Illum_Plate1_Plate2.cppipe`

Reason: We are focused on Plate1 for the fixture


### 2_CP_Apply_Illum

[diff](_original/2_CP_Apply_Illum/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff)

Differences: 2_CP_Apply_Illum_Plate3_Plate4 has a different naming convention of output images. Also there's some extra bit in the CorrectIlluminationApply module that's likely wrong because those channels likely don't exist.

Decision: `2_CP_Apply_Illum.cppipe`

Reason: We are focused on Plate1 for the fixture


### 3_CP_SegmentationCheck

[diff](_original/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2__3_CP_SegmentationCheck_Plate3_Plate4.diff)

Differences: TODO

Decision: TODO Likely `3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe`

Reason: TODO


### 5_BC_Illum

[diff](_original/5_BC_Illum/5_BC_Illum__5_BC_Illum_byWell.diff)

Differences: TODO

Decision: TODO Likely `5_BC_Illum.cppipe`

Reason: TODO


### 6_BC_Apply_Illum

Decision: `6_BC_Apply_Illum.cppipe`

Reason: We have a single pipeline


### 7_BC_Preprocess

[diff](_original/7_BC_Preprocess/7_BC_Preprocess__7_BC_Preprocess_4.diff)

Differences: TODO

Decision: TODO Likely `7_BC_Preprocess.cppipe`

Reason: TODO


### 9_Analysis

[diff](_original/9_Analysis/9_Analysis__9_Analysis_Plate1_Plate2.diff)
[diff](_original/9_Analysis/9_Analysis_foci__9_Analysis_Plate1_Plate2.diff)
[diff](_original/9_Analysis/9_Analysis_rerun__9_Analysis_Plate1_Plate2.diff)

Differences: TODO

Decision: TODO Likely `9_Analysis_Plate1_Plate2.cppipe`

Reason: TODO


## Create reference pipelines

```bash
cp _original/1_CP_Illum/1_Illum_Plate1_Plate2.cppipe 1_CP_Illum/ref_1_CP_Illum.cppipe
cp _original/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe 2_CP_Apply_Illum/ref_2_CP_Apply_Illum.cppipe
cp _original/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe 3_CP_SegmentationCheck/ref_3_CP_SegmentationCheck.cppipe
cp _original/5_BC_Illum/5_BC_Illum.cppipe 5_BC_Illum/ref_5_BC_Illum.cppipe
cp _original/6_BC_Apply_Illum/6_BC_Apply_Illum.cppipe 6_BC_Apply_Illum/ref_6_BC_Apply_Illum.cppipe
cp _original/7_BC_Preprocess/7_BC_Preprocess.cppipe 7_BC_Preprocess/ref_7_BC_Preprocess.cppipe
cp _original/9_Analysis/9_Analysis_Plate1_Plate2.cppipe 9_Analysis/ref_9_Analysis.cppipe
```

## Compare reference pipelines sources with PCPIP repo pipelines

```

```

## Modifications needed:

-  Refer to nuclear channel as `DNA` in CP pipelines, and `DAPI` in BC pipelines and be consistent about it
- `ref_9_Analysis.cppipe`: refers to ZEB1 and WGA, which cannot be disabled without deleting.
- `ref_6_BC_Apply_Illum.cppipe`, `ref_7_BC_Preprocess.cppipe`, `ref_9_Analysis.cppipe` - trim Cycles to 1-3, for testing
