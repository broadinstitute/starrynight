BASE_DIR="../../scratch"
PIPELINE_DIR="${BASE_DIR}/starrynight_example_input/Source1/workspace/pipelines/Batch1/"
LOADDATA_DIR="${BASE_DIR}/starrynight_example_output_baseline/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"
REPRODUCE_DIR="${BASE_DIR}/reproduce_starrynight_example_output_baseline"


/Users/shsingh/Documents/GitHub/starrynight/scratch/starrynight_example_output_baseline/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed

# 1_CP_Illum

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/1_CP_Illum/1_CP_Illum.cppipe \
    --data-file ${LOADDATA_DIR}/load_data_pipeline1.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/illum/Plate1

# 2_CP_Apply_Illum

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/2_CP_Apply_Illum/2_CP_Apply_Illum.cppipe \
    --data-file ${LOADDATA_DIR}/load_data_pipeline2.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/images_corrected/painting/

# 5_BC_Illum

cellprofiler \
    -c \
    -L 10 \
    --pipeline ${PIPELINE_DIR}/5_BC_Illum/5_BC_Illum.cppipe \
    --data-file ${LOADDATA_DIR}/load_data_pipeline5.csv \
    --output-directory ${REPRODUCE_DIR}/Source1/Batch1/illum/Plate1
