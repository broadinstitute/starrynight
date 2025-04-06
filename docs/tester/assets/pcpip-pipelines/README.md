# Pipelines

This document tracks the selection process for CellProfiler image analysis pipelines. It compares different pipeline versions, documents their differences, and records our decisions on which versions to use for the reference PCPIP workflow. The document includes diff commands, comparison notes, and final copy commands for the selected pipelines.

TODO: Once this [issue](https://github.com/broadinstitute/starrynight/issues/68#issuecomment-2780020724) is settled, `ref_*.cppipe` will be the selected reference pipelines for development.

## 1. Compare pipeline variants in `_refsource`

The pipelines in `_refsource` are from the `pipelines` directory of `s3://BUCKET/projects/PROJECT/workspace/pipelines/BATCH`

We compared up to three versions of the variants of each pipeline.

<details>

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

</details>

For all but 1 and 2, we picked one of the variants that "looked right", without carefully inspecting the diffs.

`1_CP_Illum`

- [diff](_refsource/1_CP_Illum/1_CP_Illum__1_Illum_Plate1_Plate2.diff)
- Differences: 1_CP_Illum.cppipe has downsampling/upsampling but 1_Illum_Plate1_Plate2.cppipe does not
- Decision: `1_Illum_Plate1_Plate2.cppipe`
- Reason: We are focused on Plate1 for the fixture


`2_CP_Apply_Illum`

- [diff](_refsource/2_CP_Apply_Illum/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff)
- Differences: 2_CP_Apply_Illum_Plate3_Plate4 has a different naming convention of output images. Also there's some extra bit in the CorrectIlluminationApply module that's likely wrong because those channels likely don't exist.
- Decision: `2_CP_Apply_Illum.cppipe`
- Reason: We are focused on Plate1 for the fixture

`3_CP_SegmentationCheck`

- [diff](_refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate3_Plate4__3_CP_SegmentationCheck_Plate1_Plate2.diff)
- Decision: Likely `3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe`

`5_BC_Illum`

- [diff](_refsource/5_BC_Illum/5_BC_Illum__5_BC_Illum_byWell.diff)
- Decision: Likely `5_BC_Illum.cppipe`

`6_BC_Apply_Illum`

- Decision: `6_BC_Apply_Illum.cppipe`
- Reason: We have a single pipeline

`7_BC_Preprocess`

- [diff](_refsource/7_BC_Preprocess/7_BC_Preprocess__7_BC_Preprocess_4.diff)
- Decision: Likely `7_BC_Preprocess.cppipe`

`9_Analysis`

- [diff](_refsource/9_Analysis/9_Analysis__9_Analysis_Plate1_Plate2.diff), [diff](_refsource/9_Analysis/9_Analysis_foci__9_Analysis_Plate1_Plate2.diff), [diff](_refsource/9_Analysis/9_Analysis_rerun__9_Analysis_Plate1_Plate2.diff)
- Decision: Likely `9_Analysis_Plate1_Plate2.cppipe`

`6_BC_Apply_Illum_DebrisMask`

- Decision: Use the PCPIP `12cycle` [version](_pcpip_12cycles/6_BC_Apply_Illum_DebrisMask.cppipe): `6_BC_Apply_Illum_DebrisMask.cppipe`

`7A_BC_Preprocess_Troubleshooting`

- Decision: Use the PCPIP `12cycle` [version](_pcpip_12cycles/7A_BC_Preprocess_Troubleshooting.cppipe) `7A_BC_Preprocess_Troubleshooting.cppipe`

## 2. Create reference pipelines

Copy the selected ones to `ref_{PIPELINE}.cppipe`

<details>

```bash
cp _refsource/1_CP_Illum/1_Illum_Plate1_Plate2.cppipe ref_1_CP_Illum.cppipe
cp _refsource/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe ref_2_CP_Apply_Illum.cppipe
cp _refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe ref_3_CP_SegmentationCheck.cppipe
cp _refsource/5_BC_Illum/5_BC_Illum.cppipe ref_5_BC_Illum.cppipe
cp _refsource/6_BC_Apply_Illum/6_BC_Apply_Illum.cppipe ref_6_BC_Apply_Illum.cppipe
cp _refsource/7_BC_Preprocess/7_BC_Preprocess.cppipe ref_7_BC_Preprocess.cppipe
cp _refsource/9_Analysis/9_Analysis_Plate1_Plate2.cppipe ref_9_Analysis.cppipe
cp _pcpip_12cycles/7A_BC_Preprocess_Troubleshooting.cppipe ref_7A_BC_Preprocess_Troubleshooting.cppipe
cp _pcpip_12cycles/6_BC_Apply_Illum_DebrisMask.cppipe ref_6_BC_Apply_Illum_DebrisMask.cppipe
```

</details>

## 3. Modify reference pipelines

After copying, the reference pipelines were modified by hand to

1. Drop cycles 4-10
2. Replace `RunCellPose` with `IdentifyPrimaryObjects`

TODO: Fix `ref_7A_BC_Preprocess_Troubleshooting` and `ref_6_BC_Apply_Illum_DebrisMask`

## 4. Compare the _unmodified_ reference pipelines sources with PCPIP `12cycle` [pipelines](https://github.com/broadinstitute/pooled-cell-painting-image-processing/tree/6c34fdb1a07d85a54dbcdfb148ad3418025e6616/pipelines/12cycles)

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

This was discussed further in https://github.com/broadinstitute/starrynight/issues/68#issuecomment-2780020724


## Troubleshooting pipeline notes


```sh
diff <(cat _pcpip_12cycles/6_BC_Apply_Illum.cppipe | cleancat) <(cat _pcpip_12cycles/6_BC_Apply_Illum_DebrisMask.cppipe|cleancat|grep -v "Save with lossless compression"|grep -v "Allow fuzzy feature matching?:No"| sed 's/_Masked$//g' |sed 's/_masked$//g')
```

```diff
3c3
< DateRevision:413
---
> DateRevision:425
5c5
< ModuleCount:81
---
> ModuleCount:95
290a291,467
>     Operation:Maximum
>     Raise the power of the result by:1.0
>     Multiply the result by:1.0
>     Add to result:0.0
>     Set values less than 0 equal to 0?:Yes
>     Set values greater than 1 equal to 1?:Yes
>     Replace invalid values with 0?:Yes
>     Ignore the image masks?:No
>     Name the output image:MaxAllDAPIs
>     Image or measurement?:Image
>     Select the first image:Cycle01_DAPI
>     Multiply the first image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the second image:Cycle02_DAPI_PreAligned
>     Multiply the second image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the third image:Cycle03_DAPI_PreAligned
>     Multiply the third image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the fourth image:Cycle04_DAPI_PreAligned
>     Multiply the fourth image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the fifth image:Cycle05_DAPI_PreAligned
>     Multiply the fifth image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the sixth image:Cycle06_DAPI_PreAligned
>     Multiply the sixth image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the seventh image:Cycle07_DAPI_PreAligned
>     Multiply the seventh image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the eighth image:Cycle08_DAPI_PreAligned
>     Multiply the eighth image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the ninth image:Cycle09_DAPI_PreAligned
>     Multiply the ninth image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the tenth image:Cycle10_DAPI_PreAligned
>     Multiply the tenth image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the eleventh image:Cycle11_DAPI_PreAligned
>     Multiply the eleventh image by:1.0
>     Measurement:
>     Image or measurement?:Image
>     Select the twelfth image:Cycle12_DAPI_PreAligned
>     Multiply the twelfth image by:1.0
>     Measurement:
>
>     Select the input image:MaxAllDAPIs
>     Name the primary objects to be identified:Debris
>     Typical diameter of objects, in pixel units (Min,Max):40,1000
>     Discard objects outside the diameter range?:Yes
>     Discard objects touching the border of the image?:No
>     Method to distinguish clumped objects:Intensity
>     Method to draw dividing lines between clumped objects:Intensity
>     Size of smoothing filter:10
>     Suppress local maxima that are closer than this minimum allowed distance:7.0
>     Speed up by using lower-resolution image to find local maxima?:Yes
>     Fill holes in identified objects?:After both thresholding and declumping
>     Automatically calculate size of smoothing filter for declumping?:Yes
>     Automatically calculate minimum allowed distance between local maxima?:Yes
>     Handling of objects if excessive number of objects identified:Continue
>     Maximum number of objects:500
>     Use advanced settings?:Yes
>     Threshold setting version:12
>     Threshold strategy:Global
>     Thresholding method:Minimum Cross-Entropy
>     Threshold smoothing scale:1.3488
>     Threshold correction factor:10
>     Lower and upper bounds on threshold:0.0,1.0
>     Manual threshold:0.0
>     Select the measurement to threshold with:None
>     Two-class or three-class thresholding?:Two classes
>     Log transform before thresholding?:No
>     Assign pixels in the middle intensity class to the foreground or the background?:Foreground
>     Size of adaptive window:50
>     Lower outlier fraction:0.05
>     Upper outlier fraction:0.05
>     Averaging method:Mean
>     Variance method:Standard deviation
>     # of deviations:2.0
>     Thresholding method:Minimum Cross-Entropy
>
>     Select the input image:Cycle01_DAPI
>     Name the output image:Cycle01_DAPI
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle02_DAPI_PreAligned
>     Name the output image:Cycle02_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle03_DAPI_PreAligned
>     Name the output image:Cycle03_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle04_DAPI_PreAligned
>     Name the output image:Cycle04_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle05_DAPI_PreAligned
>     Name the output image:Cycle05_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle06_DAPI_PreAligned
>     Name the output image:Cycle06_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle07_DAPI_PreAligned
>     Name the output image:Cycle07_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle08_DAPI_PreAligned
>     Name the output image:Cycle08_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle09_DAPI_PreAligned
>     Name the output image:Cycle09_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle10_DAPI_PreAligned
>     Name the output image:Cycle10_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle11_DAPI_PreAligned
>     Name the output image:Cycle11_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
>     Select the input image:Cycle12_DAPI_PreAligned
>     Name the output image:Cycle12_DAPI_PreAligned
>     Use objects or an image as a mask?:Objects
>     Select object for mask:Debris
>     Select image for mask:None
>     Invert the mask?:Yes
>
308a486,488
>     Select the additional image:Cycle02_DAPI_PreAligned
>     Name the output image:Cycle02_DAPI
>     Select how the alignment is to be applied:Similarly
327a508,510
>     Select the additional image:Cycle03_DAPI_PreAligned
>     Name the output image:Cycle03_DAPI
>     Select how the alignment is to be applied:Similarly
346a530,532
>     Select the additional image:Cycle04_DAPI_PreAligned
>     Name the output image:Cycle04_DAPI
>     Select how the alignment is to be applied:Similarly
365a552,554
>     Select the additional image:Cycle05_DAPI_PreAligned
>     Name the output image:Cycle05_DAPI
>     Select how the alignment is to be applied:Similarly
384a574,576
>     Select the additional image:Cycle06_DAPI_PreAligned
>     Name the output image:Cycle06_DAPI
>     Select how the alignment is to be applied:Similarly
403a596,598
>     Select the additional image:Cycle07_DAPI_PreAligned
>     Name the output image:Cycle07_DAPI
>     Select how the alignment is to be applied:Similarly
422a618,620
>     Select the additional image:Cycle08_DAPI_PreAligned
>     Name the output image:Cycle08_DAPI
>     Select how the alignment is to be applied:Similarly
441a640,642
>     Select the additional image:Cycle09_DAPI_PreAligned
>     Name the output image:Cycle09_DAPI
>     Select how the alignment is to be applied:Similarly
460a662,664
>     Select the additional image:Cycle10_DAPI_PreAligned
>     Name the output image:Cycle10_DAPI
>     Select how the alignment is to be applied:Similarly
479a684,686
>     Select the additional image:Cycle11_DAPI_PreAligned
>     Name the output image:Cycle11_DAPI
>     Select how the alignment is to be applied:Similarly
497a705,707
>     Select how the alignment is to be applied:Similarly
>     Select the additional image:Cycle12_DAPI_PreAligned
>     Name the output image:Cycle12_DAPI
```
