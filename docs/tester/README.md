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

[diff](docs/tester/pipelines/1_CP_Illum/1_CP_Illum__1_Illum_Plate1_Plate2.diff)
< ModuleCount:22
---
> ModuleCount:16
75,129d74
<     Select the input image:OrigZEB1
<     Name the output image:DownsampledZEB1
<     Resizing method:Resize by a fraction or multiple of the original size
<     X Resizing factor:0.25
<     Y Resizing factor:0.25
<     Z Resizing factor:1.0
<     Width (x) of the final image:100
<     Height (y) of the final image:100
<     # of planes (z) in the final image:10
<     Interpolation method:Bilinear
<     Method to specify the dimensions:Manual
<     Select the image with the desired dimensions:None
<     Additional image count:0
<
< CorrectIlluminationCalculate:[module_num:6|svn_version:'Unknown'|variable_revision_number:2|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
<     Select the input image:DownsampledZEB1
<     Name the output image:IllumZEB1
<     Select how the illumination function is calculated:Regular
<     Dilate objects in the final averaged image?:No
<     Dilation radius:1
<     Block size:60
<     Rescale the illumination function?:Yes
<     Calculate function for each image individually, or based on all images?:All: Across cycles
<     Smoothing method:Median Filter
<     Method to calculate smoothing filter size:Manually
<     Approximate object diameter:10
<     Smoothing filter size:10
<     Retain the averaged image?:No
<     Name the averaged image:IllumBlueAvg
<     Retain the dilated image?:No
<     Name the dilated image:IllumBlueDilated
<     Automatically calculate spline parameters?:Yes
<     Background mode:auto
<     Number of spline points:5
<     Background threshold:2
<     Image resampling factor:2
<     Maximum number of iterations:40
<     Residual value for convergence:0.001
<
< Resize:[module_num:7|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
<     Select the input image:IllumZEB1
<     Name the output image:UpsampledIllumZEB1
<     Resizing method:Resize by a fraction or multiple of the original size
<     X Resizing factor:4
<     Y Resizing factor:4
<     Z Resizing factor:1.0
<     Width (x) of the final image:100
<     Height (y) of the final image:100
<     # of planes (z) in the final image:10
<     Interpolation method:Bilinear
<     Method to specify the dimensions:Manual
<     Select the image with the desired dimensions:None
<     Additional image count:0
<
< Resize:[module_num:8|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
144c89
< CorrectIlluminationCalculate:[module_num:9|svn_version:'Unknown'|variable_revision_number:2|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
---
> CorrectIlluminationCalculate:[module_num:6|svn_version:'Unknown'|variable_revision_number:2|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
169c114
< Resize:[module_num:10|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
---
> Resize:[module_num:7|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
184c129
< Resize:[module_num:11|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
---
> Resize:[module_num:8|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
199c144
< CorrectIlluminationCalculate:[module_num:12|svn_version:'Unknown'|variable_revision_number:2|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
---
> CorrectIlluminationCalculate:[module_num:9|svn_version:'Unknown'|variable_revision_number:2|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
224c169
< Resize:[module_num:13|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
---
> Resize:[module_num:10|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
239,294c184
< Resize:[module_num:14|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
<     Select the input image:OrigWGA
<     Name the output image:DownsampledWGA
<     Resizing method:Resize by a fraction or multiple of the original size
<     X Resizing factor:0.25
<     Y Resizing factor:0.25
<     Z Resizing factor:1.0
<     Width (x) of the final image:100
<     Height (y) of the final image:100
<     # of planes (z) in the final image:10
<     Interpolation method:Bilinear
<     Method to specify the dimensions:Manual
<     Select the image with the desired dimensions:None
<     Additional image count:0
<
< CorrectIlluminationCalculate:[module_num:15|svn_version:'Unknown'|variable_revision_number:2|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
<     Select the input image:DownsampledWGA
<     Name the output image:IllumWGA
<     Select how the illumination function is calculated:Regular
<     Dilate objects in the final averaged image?:No
<     Dilation radius:1
<     Block size:60
<     Rescale the illumination function?:Yes
<     Calculate function for each image individually, or based on all images?:All: Across cycles
<     Smoothing method:Median Filter
<     Method to calculate smoothing filter size:Manually
<     Approximate object diameter:10
<     Smoothing filter size:10
<     Retain the averaged image?:No
<     Name the averaged image:IllumBlueAvg
<     Retain the dilated image?:No
<     Name the dilated image:IllumBlueDilated
<     Automatically calculate spline parameters?:Yes
<     Background mode:auto
<     Number of spline points:5
<     Background threshold:2
<     Image resampling factor:2
<     Maximum number of iterations:40
<     Residual value for convergence:0.001
<
< Resize:[module_num:16|svn_version:'Unknown'|variable_revision_number:5|show_window:False|notes:[]|batch_state:array([], dtype=uint8)|enabled:True|wants_pause:False]
<     Select the input image:IllumWGA
<     Name the output image:UpsampledIllumWGA
<     Resizing method:Resize by a fraction or multiple of the original size
<     X Resizing factor:4
<     Y Resizing factor:4
<     Z Resizing factor:1.0
<     Width (x) of the final image:100
<     Height (y) of the final image:100
<     # of planes (z) in the final image:10
<     Interpolation method:Bilinear
<     Method to specify the dimensions:Manual
<     Select the image with the desired dimensions:None
<     Additional image count:0
(trimmed, rest are module_num diffs)
</details>

## 2_CP_Apply_Illum

```
diff 2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe 2_CP_Apply_Illum/2_CP_Apply_Illum_Plate3_Plate4.cppipe
```

2_CP_Apply_Illum_Plate3_Plate4 gas a different naming convention of output images. Also there's some extra bit in the CorrectIlluminationApply module that's likely wrong because those channels likely don't exist.

Decision: 2_CP_Apply_Illum.cppipe

Reason: We are focused on Plate1 for the fixture


[diff](docs/tester/pipelines/2_CP_Apply_Illum/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff)


## 3_CP_SegmentationCheck

```
```

Decision:

Reason:

[diff](docs/tester/pipelines/5_BC_Illum/5_BC_Illum__5_BC_Illum_byWell.diff)


## 5_BC_Illum

```
```

Decision:

Reason:

[diff](docs/tester/pipelines/)


## 6_BC_Apply_Illum

Decision: 6_BC_Apply_Illum.cppipe

Reason: We have a single pipeline


## 7_BC_Preprocess

```
```

Decision:

Reason:

[diff](docs/tester/pipelines/7_BC_Preprocess/7_BC_Preprocess__7_BC_Preprocess_4.diff)
[diff](docs/tester/pipelines/)


## 9_Analysis

```
```

Decision:

Reason:

[diff](docs/tester/pipelines/9_Analysis/9_Analysis__9_Analysis_Plate1_Plate2.diff)
[diff](docs/tester/pipelines/9_Analysis/9_Analysis_foci__9_Analysis_Plate1_Plate2.diff)
[diff](docs/tester/pipelines/9_Analysis/9_Analysis_rerun__9_Analysis_Plate1_Plate2.diff)
