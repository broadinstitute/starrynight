#!/bin/bash

rm -rf Source1

python3 generate_outputs.py \
    --io-json ../io.json \
    --batch Batch1 \
    --plates Plate1 \
    --rows 1 \
    --columns 1 \
    --wells A1 \
    --tileperside 2 \
    --barcoding-cycles 1 \
    --output-file generated_paths.json \
    --output-format both \
    --create-files \
    --base-path Source1/


jq -r '.[][] | .[]' generated_paths.json|sort|uniq > generated_paths.txt
