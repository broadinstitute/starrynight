STARRYNIGHT_REPO_REL="../../../.."
LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/starrynight_example_output_baseline/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"
REPRODUCE_DIR="${STARRYNIGHT_REPO_REL}/scratch/reproduce_starrynight_example_output_baseline"

PIPELINE_DIR="../pcpip-pipelines"


# 1_CP_Illum

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/1_CP_Illum/ref_1_CP_Illum.cppipe \
    --data-file ${LOAD_DATA_DIR}/load_data_pipeline1.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/illum/Plate1

# 2_CP_Apply_Illum

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/2_CP_Apply_Illum/ref_2_CP_Apply_Illum.cppipe \
    --data-file ${LOAD_DATA_DIR}/load_data_pipeline2.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/images_corrected/painting/

# 3_CP_SegmentationCheck

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/3_CP_SegmentationCheck/ref_3_CP_SegmentationCheck.cppipe \
    --data-file ${LOAD_DATA_DIR}/load_data_pipeline3.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/images_segmentation/ \
    --plugins-directory ${STARRYNIGHT_REPO_REL}/plugins/CellProfiler-plugins/active_plugins/

# [CP - ERROR] cellprofiler_core.pipeline._pipeline::run_with_yield: Error detected during run of module RunCellpose
# Traceback (most recent call last):
#   File "/nix/store/g96aiz9nakj9h2n5il8rxb08fjf8w7gm-python3-3.11.10-env/lib/python3.11/site-packages/cellprofiler_core/pipeline/_pipeline.py", line 1080, in run_with_yield
#     self.run_module(module, workspace)
#   File "/nix/store/g96aiz9nakj9h2n5il8rxb08fjf8w7gm-python3-3.11.10-env/lib/python3.11/site-packages/cellprofiler_core/pipeline/_pipeline.py", line 1459, in run_module
#     module.run(workspace)
#   File "/Users/shsingh/Documents/GitHub/starrynight/docs/tester/assets/pcpip-run-cellprofiler/../../../../plugins/CellProfiler-plugins/active_plugins/runcellpose.py", line 508, in run
#     from cellpose import models, io, core, utils

# 5_BC_Illum

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/5_BC_Illum/ref_5_BC_Illum.cppipe \
    --data-file ${LOAD_DATA_DIR}/load_data_pipeline5.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/illum/Plate1

# 6_BC_Apply_Illum

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/6_BC_Apply_Illum/ref_6_BC_Apply_Illum.cppipe \
    --data-file ${LOAD_DATA_DIR}/load_data_pipeline6.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/images_aligned/barcoding/
