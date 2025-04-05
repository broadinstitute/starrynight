# Pipelines

This document tracks the selection process for CellProfiler image analysis pipelines. It compares different pipeline versions, documents their differences, and records our decisions on which versions to use for the reference PCPIP workflow. The document includes diff commands, comparison notes, and final copy commands for the selected pipelines.

## Select among variants in `pipelines`

The pipelines in `_refsource` are from the `pipelines` directory of `s3://BUCKET/projects/PROJECT/workspace/pipelines/BATCH`

We compared up to two versions of the variants of each pipeline.

```bash
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

For all but 1 and 2, we picked one of the variants that "looked right"

### 1_CP_Illum

[diff](_refsource/1_CP_Illum/1_CP_Illum__1_Illum_Plate1_Plate2.diff)

Differences: 1_CP_Illum.cppipe has downsampling/upsampling but 1_Illum_Plate1_Plate2.cppipe does not

Decision: `1_Illum_Plate1_Plate2.cppipe`

Reason: We are focused on Plate1 for the fixture


### 2_CP_Apply_Illum

[diff](_refsource/2_CP_Apply_Illum/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff)

Differences: 2_CP_Apply_Illum_Plate3_Plate4 has a different naming convention of output images. Also there's some extra bit in the CorrectIlluminationApply module that's likely wrong because those channels likely don't exist.

Decision: `2_CP_Apply_Illum.cppipe`

Reason: We are focused on Plate1 for the fixture


### 3_CP_SegmentationCheck

[diff](_refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2__3_CP_SegmentationCheck_Plate3_Plate4.diff)

Differences: SKIPPED

Decision: Likely `3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe`

Reason: SKIPPED


### 5_BC_Illum

[diff](_refsource/5_BC_Illum/5_BC_Illum__5_BC_Illum_byWell.diff)

Differences: SKIPPED

Decision: Likely `5_BC_Illum.cppipe`

Reason: SKIPPED


### 6_BC_Apply_Illum

Decision: `6_BC_Apply_Illum.cppipe`

Reason: We have a single pipeline


### 7_BC_Preprocess

[diff](_refsource/7_BC_Preprocess/7_BC_Preprocess__7_BC_Preprocess_4.diff)

Differences: SKIPPED

Decision: Likely `7_BC_Preprocess.cppipe`

Reason: SKIPPED


### 9_Analysis

[diff](_refsource/9_Analysis/9_Analysis__9_Analysis_Plate1_Plate2.diff)
[diff](_refsource/9_Analysis/9_Analysis_foci__9_Analysis_Plate1_Plate2.diff)
[diff](_refsource/9_Analysis/9_Analysis_rerun__9_Analysis_Plate1_Plate2.diff)

Differences: SKIPPED

Decision: Likely `9_Analysis_Plate1_Plate2.cppipe`

Reason: SKIPPED


## Create reference pipelines

Copy the selected ones as `ref_*.cppipe`

```bash
cp _refsource/1_CP_Illum/1_Illum_Plate1_Plate2.cppipe ref_1_CP_Illum.cppipe
cp _refsource/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe ref_2_CP_Apply_Illum.cppipe
cp _refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe ref_3_CP_SegmentationCheck.cppipe
cp _refsource/5_BC_Illum/5_BC_Illum.cppipe ref_5_BC_Illum.cppipe
cp _refsource/6_BC_Apply_Illum/6_BC_Apply_Illum.cppipe ref_6_BC_Apply_Illum.cppipe
cp _refsource/7_BC_Preprocess/7_BC_Preprocess.cppipe ref_7_BC_Preprocess.cppipe
cp _refsource/9_Analysis/9_Analysis_Plate1_Plate2.cppipe ref_9_Analysis.cppipe
```

After copying, the reference pipelines were modified by hand to

1. Drop cycles 4-10
2. Replace `RunCellPose` with `IdentifyPrimaryObjects`

## Compare the unmodified reference pipelines sources with PCPIP repo pipelines

```bash
mkdir -p _pcpip_12cycles/diff

refsource_1="_refsource/1_CP_Illum/1_Illum_Plate1_Plate2.cppipe"
pcpip_1="_pcpip_12cycles/1_CP_Illum.cppipe"
diff_1="_pcpip_12cycles/diff/1_CP_Illum"
diff -w ${refsource_1} ${pcpip_1} > ${diff_1}.diff
python scripts/diff.py ${pcpip_1} ${refsource_1} --format html --output ${diff_1}.html

refsource_2="_refsource/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe"
pcpip_2="_pcpip_12cycles/2_CP_Apply_Illum.cppipe"
diff_2="_pcpip_12cycles/diff/2_CP_Apply_Illum"
diff -w ${refsource_2} ${pcpip_2} > ${diff_2}.diff
python scripts/diff.py ${pcpip_2} ${refsource_2} --format html --output ${diff_2}.html

refsource_3="_refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe"
pcpip_3="_pcpip_12cycles/3_CP_SegmentationCheck.cppipe"
diff_3="_pcpip_12cycles/diff/3_CP_SegmentationCheck"
diff -w ${refsource_3} ${pcpip_3} > ${diff_3}.diff
python scripts/diff.py ${pcpip_3} ${refsource_3} --format html --output ${diff_3}.html

refsource_5="_refsource/5_BC_Illum/5_BC_Illum.cppipe"
pcpip_5="_pcpip_12cycles/5_BC_Illum.cppipe"
diff_5="_pcpip_12cycles/diff/5_BC_Illum"
diff -w ${refsource_5} ${pcpip_5} > ${diff_5}.diff
python scripts/diff.py ${pcpip_5} ${refsource_5} --format html --output ${diff_5}.html

refsource_6="_refsource/6_BC_Apply_Illum/6_BC_Apply_Illum.cppipe"
pcpip_6="_pcpip_12cycles/6_BC_Apply_Illum.cppipe"
diff_6="_pcpip_12cycles/diff/6_BC_Apply_Illum"
diff -w ${refsource_6} ${pcpip_6} > ${diff_6}.diff
python scripts/diff.py ${pcpip_6} ${refsource_6} --format html --output ${diff_6}.html

refsource_7="_refsource/7_BC_Preprocess/7_BC_Preprocess.cppipe"
pcpip_7="_pcpip_12cycles/7_BC_Preprocess.cppipe"
diff_7="_pcpip_12cycles/diff/7_BC_Preprocess"
diff -w ${refsource_7} ${pcpip_7} > ${diff_7}.diff
python scripts/diff.py ${pcpip_7} ${refsource_7} --format html --output ${diff_7}.html

refsource_9="_refsource/9_Analysis/9_Analysis_Plate1_Plate2.cppipe"
pcpip_9="_pcpip_12cycles/9_Analysis.cppipe"
diff_9="_pcpip_12cycles/diff/9_Analysis"
diff -w ${refsource_9} ${pcpip_9} > ${diff_9}.diff
python scripts/diff.py ${pcpip_9} ${refsource_9} --format html --output ${diff_9}.html
```
