#!/bin/bash

rm -rf csv_output filelist_output

python3 generate_csvs.py \
    --wells A1 \
    --sites 0 \
    --tile_numbers 0 1 2 3 \
    --cycles 1 \
    --output generated_csvs.json

python process_json.py

find filelist_output -type f -exec cat {} +|sort | uniq  > generated_paths_from_csvs.txt
