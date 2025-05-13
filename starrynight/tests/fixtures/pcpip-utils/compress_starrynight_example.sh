
export INPUT_DIR='./scratch/starrynight_example_input'
export OUTPUT_BASELINE_DIR='./scratch/pcpip_example_output'

# Compress files to reduce disk usage after downloading
echo "Compressing files to reduce disk usage..."

## Compress all TIFF files
find ${OUTPUT_BASELINE_DIR} -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'
find ${INPUT_DIR} -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'

# Compress CSV files
find ${OUTPUT_BASELINE_DIR} -type f -name "*.csv" | parallel 'gzip -9 {}'
