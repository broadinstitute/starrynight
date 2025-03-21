
BUCKET=XXXXXX
PROJECT=XXXXXX
BATCH=XXXXXX

export S3_PATH="s3://${BUCKET}/projects/${PROJECT}/${BATCH}"
export INPUT_DIR='./scratch/starrynight_example_input'
export OUTPUT_BASELINE_DIR='./scratch/starrynight_example_output_baseline'

# Inputs

## SBS images

parallel mkdir -p ${INPUT_DIR}/Source1/Batch1/images/Plate1/20X_c{1}_SBS-{1}/ ::: 1 2 3

parallel --match '.*' --match '(.*) (.*) (.*)' \
    aws s3 cp "${S3_PATH}/images/Plate1/20X_c{1}_SBS-{1}/Well{2.1}_Point{2.1}_{2.2}_ChannelC,A,T,G,DAPI_Seq{2.3}.ome.tiff" \
    "${INPUT_DIR}/Source1/Batch1/images/Plate1/20X_c{1}_SBS-{1}/" ::: \
    1 2 3 ::: \
    "A1 0000 0000" "A1 0001 0001" "A1 0002 0002" "A1 0003 0003" "A2 0000 1025" "A2 0001 1026" "A2 0002 1027" "A2 0003 1028" "B1 0000 3075" "B1 0001 3076" "B1 0002 3077" "B1 0003 3078"


## Cell Painting images

mkdir -p ${INPUT_DIR}/Source1/Batch1/images/20X_CP_Plate1_20240319_122800_179

parallel --match '(.*) (.*) (.*)' \
   aws s3 cp "${S3_PATH}/images/Plate1/20X_CP_Plate1_20240319_122800_179/Well{1.1}_Point{1.1}_{1.2}_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq{1.3}.ome.tiff" \
   "${INPUT_DIR}/Source1/Batch1/images/Plate1/20X_CP_Plate1_20240319_122800_179/" ::: \
   "A1 0000 0000" "A1 0001 0001" "A1 0002 0002" "A1 0003 0003" "A2 0000 1025" "A2 0001 1026" "A2 0002 1027" "A2 0003 1028" "B1 0000 3075" "B1 0001 3076" "B1 0002 3077" "B1 0003 3078"

# Outputs

## Illumination correction images

mkdir -p ${OUTPUT_BASELINE_DIR}/Source1/Batch1/illum/Plate1
parallel \
   aws s3 cp "${S3_PATH}/illum/Plate1/Plate1_Cycle{1}_Illum{2}.npy" "${OUTPUT_BASELINE_DIR}/Source1/Batch1/illum/Plate1/" ::: \
   1 2 3 ::: \
   DNA A T G C

parallel \
   aws s3 cp "${S3_PATH}/illum/Plate1/Plate1_Illum{1}.npy" "${OUTPUT_BASELINE_DIR}/Source1/Batch1/illum/Plate1/" ::: \
   DNA Phalloidin ZO1

## Cell Painting images: Illumination corrected

parallel \
   aws s3 cp "${S3_PATH}/images_corrected/painting/Plate1-Well{1}/Plate_Plate1_Well_Well{1}_Site_{2}_Corr{3}.tiff" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_corrected/painting/Plate1-Well{1}/" ::: \
   A1 A2 B1 ::: 0 1 ::: DNA Phalloidin ZO1

parallel \
   aws s3 cp "${S3_PATH}/images_corrected/painting/Plate1-Well{1}/PaintingIllumApplication_{2}.csv" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_corrected/painting/Plate1-Well{1}/" ::: \
   A1 A2 B1 ::: Cells ConfluentRegions Experiment Image Nuclei

# SBS images: Illumination aligned

parallel \
   aws s3 cp "${S3_PATH}/images_aligned/barcoding/Plate1-Well{1}-{2}/Plate_Plate1_Well_{1}_Site_{2}_Cycle0{3}_{4}.tiff" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_aligned/barcoding/Plate1-Well{1}-{2}/" ::: \
   A1 A2 B1 ::: 0 1 2 3 ::: 1 2 3 ::: A T G C DAPI


parallel \
   aws s3 cp "${S3_PATH}/images_aligned/barcoding/Plate1-Well{1}-{2}/BarcodingApplication_{3}.csv" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_aligned/barcoding/Plate1-Well{1}-{2}/" ::: \
   A1 A2 B1 ::: 0 1 2 3 ::: Experiment Image

## SBS images: Illumination corrected

parallel \
   aws s3 cp "${S3_PATH}/images_corrected/barcoding/Plate1-Well{1}-{2}/Plate_Plate1_Well_{1}_Site_{2}_Cycle0{3}_{4}.tiff" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_corrected/barcoding/Plate1-Well{1}-{2}/" ::: \
   A1 A2 B1 ::: 0 1 2 3 ::: 1 2 3 ::: A T G C

parallel \
   aws s3 cp "${S3_PATH}/images_corrected/barcoding/Plate1-Well{1}-{2}/Plate_Plate1_Well_{1}_Site_{2}_Cycle0{3}_{4}.tiff" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_corrected/barcoding/Plate1-Well{1}-{2}/" ::: \
   A1 A2 B1 ::: 0 1 2 3 ::: 1 ::: DAPI
# DAPI is present only in the first cycle


parallel \
   aws s3 cp "${S3_PATH}/images_corrected/barcoding/Plate1-Well{1}-{2}/BarcodePreprocessing_{3}.csv" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_corrected/barcoding/Plate1-Well{1}-{2}/" ::: \
   A1 A2 B1 ::: 0 1 2 3 ::: BarcodeFoci PreFoci Experiment Image Nuclei

## Segmentation images

parallel \
   aws s3 cp "${S3_PATH}/images_segmentation/Plate1/Plate_Plate1_Well_Well{1}_Site_{2}_Corr{3}_SegmentCheck.png" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_segmentation/Plate1/" ::: \
   A1 A2 B1 ::: 0 ::: DNA

parallel \
   aws s3 cp "${S3_PATH}/images_segmentation/Plate1/Plate_Plate1_Well_Well{1}_Site_{2}_Corr{3}_SegmentCheck.png" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_segmentation/Plate1/" ::: \
   A1 A2 B1 ::: 0 ::: DNA

parallel \
   aws s3 cp "${S3_PATH}/images_segmentation/Plate1/SegmentationCheck_{1}.csv" \
   "${OUTPUT_BASELINE_DIR}/Source1/Batch1/images_segmentation/Plate1/" ::: \
   Experiment Image Nuclei Cells PreCells ConfluentRegions

## Load Data CSVs

export S3_PATH_WORKSPACE="s3://${BUCKET}/projects/${PROJECT}/workspace"

aws s3 sync \
   "${S3_PATH_WORKSPACE}/load_data_csv/${BATCH}/Plate1/" \
   "${OUTPUT_BASELINE_DIR}/Source1/workspace_example/load_data_csv/Batch1/Plate1/"

## Analysis CSVs

parallel \
   aws s3 sync \
   "${S3_PATH_WORKSPACE}/analysis/${BATCH}/Plate1-Well{1}-{2}/" \
   "${OUTPUT_BASELINE_DIR}/Source1/workspace_example/analysis/${BATCH}/Plate1-Well{1}-{2}/" \
   --exclude \""*.csv\"" ::: \
   A1 A2 B1 ::: 0 1 2 3


parallel \
   aws s3 sync \
   "${S3_PATH_WORKSPACE}/analysisfix/${BATCH}/Plate1-Well{1}-{2}/" \
   "${OUTPUT_BASELINE_DIR}/Source1/workspace_example/analysis/${BATCH}/Plate1-Well{1}-{2}/" ::: \
   A1 A2 B1 ::: 0 1 2 3
# Note that the analysis files are synced from two different locations: analysis and analysisfix.
# analysisfix was a rerun of analysis

# Compress files to reduce disk usage after downloading
echo "Compressing files to reduce disk usage..."

## Compress all TIFF files
find ${OUTPUT_BASELINE_DIR} -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'
find ${INPUT_DIR} -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'

# Compress CSV files
find ${OUTPUT_BASELINE_DIR} -type f -name "*.csv" | parallel 'gzip -9 {}'
