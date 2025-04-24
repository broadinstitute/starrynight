# pcpip-pipelines

Documentation for selecting and comparing CellProfiler pipelines to create a reference set for the PCPIP workflow.

<https://github.com/broadinstitute/starrynight/tree/main/docs/tester/assets/pcpip-pipelines>

## Components

- Selected reference CellProfiler pipeline files (`.cppipe`) for the PCPIP workflow
- Comparison scripts to analyze differences between pipeline versions
- Pipeline selection documentation

## Pipeline Selection Process

This documents the selection of CellProfiler pipelines, comparing different versions and recording decisions on which to use as references.

### Pipeline Variants Comparison

Pipeline variants in `_refsource` are from `s3://BUCKET/projects/PROJECT/workspace/pipelines/BATCH`

<details>

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

</details>

### Pipeline Selection Decisions

After skimming the [diffs](https://github.com/broadinstitute/starrynight/tree/main/docs/tester/assets/pcpip-pipelines/_refsource) (e.g., [this](https://github.com/broadinstitute/starrynight/blob/main/docs/tester/assets/pcpip-pipelines/_refsource/2_CP_Apply_Illum/2_CP_Apply_Illum__2_CP_Apply_Illum_Plate3_Plate4.diff)), these pipeline variants were selected:

- `1_CP_Illum`: `1_Illum_Plate1_Plate2.cppipe`
- `2_CP_Apply_Illum`: `2_CP_Apply_Illum.cppipe`
- `3_CP_SegmentationCheck`: `3_CP_SegmentationCheck_Plate1_Plate2.cppipe`
- `5_BC_Illum`: `5_BC_Illum.cppipe`
- `6_BC_Apply_Illum`: `6_BC_Apply_Illum.cppipe`
- `7_BC_Preprocess`: `7_BC_Preprocess.cppipe`
- `9_Analysis`: `9_Analysis_Plate1_Plate2.cppipe`

### Reference Pipelines Creation

```sh
cp _refsource/1_CP_Illum/1_Illum_Plate1_Plate2.cppipe ref_1_CP_Illum.cppipe
cp _refsource/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe ref_2_CP_Apply_Illum.cppipe
cp _refsource/3_CP_SegmentationCheck/3_CP_SegmentationCheck_Plate1_Plate2.cppipe ref_3_CP_SegmentationCheck.cppipe
cp _refsource/5_BC_Illum/5_BC_Illum.cppipe ref_5_BC_Illum.cppipe
cp _refsource/6_BC_Apply_Illum/6_BC_Apply_Illum.cppipe ref_6_BC_Apply_Illum.cppipe
cp _refsource/7_BC_Preprocess/7_BC_Preprocess.cppipe ref_7_BC_Preprocess.cppipe
cp _refsource/9_Analysis/9_Analysis_Plate1_Plate2.cppipe ref_9_Analysis.cppipe
```

## Reference Pipelines Modifications

The reference pipelines were further modified by hand to

1. Drop cycles 4-10
2. Replace `RunCellPose` with `IdentifyPrimaryObjects`

See the commit history of pipeline in <https://github.com/broadinstitute/starrynight/tree/main/docs/tester/assets/pcpip-pipelines/> to review the edits.

### Comparison with PCPIP Pipelines

Compare the _unmodified_ reference pipelines sources with PCPIP `12cycle` [pipelines](https://github.com/broadinstitute/
pooled-cell-painting-image-processing/tree/6c34fdb1a07d85a54dbcdfb148ad3418025e6616/pipelines/12cycles)

This was discussed further in <https://github.com/broadinstitute/starrynight/issues/68#issuecomment-2780020724>

```sh
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

## Specialized Pipeline Variants

### 6_BC_Apply_Illum_DebrisMask

See PCPIP `12cycle` [version](_pcpip_12cycles/6_BC_Apply_Illum_DebrisMask.cppipe).

The 6_BC_Apply_Illum_DebrisMask pipeline is a specialized variant of 6_BC_Apply_Illum developed for datasets with significant debris that requires masking. This pipeline demonstrates the extensibility requirements for starrynight, showing how specialized processing steps can be swapped in to address dataset-specific challenges. While valuable as a reference for extensibility design, it is not required as a standard test fixture.

### 7A_BC_Preprocess_Troubleshooting

See PCPIP `12cycle` [version](_pcpip_12cycles/7A_BC_Preprocess_Troubleshooting.cppipe).

If starrynight successfully implements module iteration capabilities, pipeline 7A becomes largely redundant. The 7A pipeline was created as a workaround for testing multiple CompensateColors parameter settings within a single pipeline execution. A truly modular system would allow iterative parameter testing without requiring specialized pipeline variants.

## Pipeline Visualization Files

Files in `_ref_graph_format` were created as follows:

- **JSON files**: Exported from CellProfiler 4.2.8
- **DOT files**: Generated using [cp_graph](https://github.com/shntnu/cp_graph/blob/v0.10.0/cp_graph.py) tool. **SVG/PNG files**: Generated from DOT files using Graphviz.
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
