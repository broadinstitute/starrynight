# Pipelines

```bash
diff 1_CP_Illum/1_CP_Illum.cppipe 1_CP_Illum/1_Illum_Plate1_Plate2.cppipe > 1_CP_Illum/diff/1_CP_Illum__1_Illum_Plate1_Plate2.diff
diff 2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe 2_CP_Apply_Illum/2_CP_Apply_Illum_Plate3_Plate4.cppipe > 2_CP_Apply_Illum/diff/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff
diff 5_BC_Illum/5_BC_Illum.cppipe 5_BC_Illum/5_BC_Illum_byWell.cppipe > 5_BC_Illum/diff/5_BC_Illum__5_BC_Illum_byWell.diff
diff 7_BC_Preprocess/7_BC_Preprocess.cppipe 7_BC_Preprocess/7_BC_Preprocess_4.cppipe > 7_BC_Preprocess/diff/7_BC_Preprocess__7_BC_Preprocess_4.diff
diff 9_Analysis/9_Analysis.cppipe 9_Analysis/9_Analysis_Plate1_Plate2.cppipe > 9_Analysis/diff/9_Analysis__9_Analysis_Plate1_Plate2.diff
diff 9_Analysis/9_Analysis_foci.cppipe 9_Analysis/9_Analysis_Plate1_Plate2.cppipe > 9_Analysis/diff/9_Analysis_foci__9_Analysis_Plate1_Plate2.diff
diff 9_Analysis/9_Analysis_rerun.cppipe 9_Analysis/9_Analysis_Plate1_Plate2.cppipe > 9_Analysis/diff/9_Analysis_rerun__9_Analysis_Plate1_Plate2.diff
```

## 1_CP_Illum

```
diff 1_CP_Illum/1_CP_Illum.cppipe 1_CP_Illum/1_Illum_Plate1_Plate2.cppipe
```

1_CP_Illum.cppipe has downsampling/upsampling but 1_Illum_Plate1_Plate2.cppipe does not

Decision: 1_Illum_Plate1_Plate2.cppipe

Reason: We are focused on Plate1 for the fixture

[diff](pipelines/1_CP_Illum/1_CP_Illum__1_Illum_Plate1_Plate2.diff)

## 2_CP_Apply_Illum

```
diff 2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe 2_CP_Apply_Illum/2_CP_Apply_Illum_Plate3_Plate4.cppipe
```

2_CP_Apply_Illum_Plate3_Plate4 gas a different naming convention of output images. Also there's some extra bit in the CorrectIlluminationApply module that's likely wrong because those channels likely don't exist.

Decision: 2_CP_Apply_Illum.cppipe

Reason: We are focused on Plate1 for the fixture


[diff](pipelines/2_CP_Apply_Illum/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff)


## 3_CP_SegmentationCheck

```
```

Decision:

Reason:

[diff](pipelines/5_BC_Illum/5_BC_Illum__5_BC_Illum_byWell.diff)


## 5_BC_Illum

```
```

Decision:

Reason:

[diff](pipelines/5_BC_Illum/5_BC_Illum__5_BC_Illum_byWell.diff)


## 6_BC_Apply_Illum

Decision: 6_BC_Apply_Illum.cppipe

Reason: We have a single pipeline


## 7_BC_Preprocess

```
```

Decision:

Reason:

[diff](pipelines/7_BC_Preprocess/7_BC_Preprocess__7_BC_Preprocess_4.diff)


## 9_Analysis

```
```

Decision:

Reason:

[diff](pipelines/9_Analysis/9_Analysis__9_Analysis_Plate1_Plate2.diff)
[diff](pipelines/9_Analysis/9_Analysis_foci__9_Analysis_Plate1_Plate2.diff)
[diff](pipelines/9_Analysis/9_Analysis_rerun__9_Analysis_Plate1_Plate2.diff)
