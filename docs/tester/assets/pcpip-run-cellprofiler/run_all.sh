STARRYNIGHT_REPO_REL="../../../.."
LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/starrynight_example_output_baseline/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"
REPRODUCE_DIR="${STARRYNIGHT_REPO_REL}/scratch/reproduce_starrynight_example_output_baseline"
METADATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/starrynight_example_input/Source1/workspace/metadata"

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
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/images_segmentation/

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

# 7_BC_Preprocess

cellprofiler \
    -c \
    -L 10 \
    -i ${METADATA_DIR}/ \
    --pipeline ${PIPELINE_DIR}/7_BC_Preprocess/ref_7_BC_Preprocess.cppipe \
    --data-file ${LOAD_DATA_DIR}/load_data_pipeline7.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/images_preprocessed/barcoding/ \
    --plugins-directory ${STARRYNIGHT_REPO_REL}/plugins/CellProfiler-plugins/active_plugins/
