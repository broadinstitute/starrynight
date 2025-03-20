# Analysis (analysis.py)

Implements a comprehensive analysis pipeline for microscopy images that integrates quality control, segmentation, feature extraction, and barcode calling to enable detailed phenotypic analysis of optical pooled screening experiments.

## Key Components

- **Multi-modality Integration**: Combines Cell Painting (CP) and sequential-based screening (SBS) images in a unified analysis pipeline
- **Multi-scale Feature Extraction**: Analyzes at subcellular (spots), cellular (nuclei, cells), and multicellular (neighborhoods, confluent regions) scales
- **Comprehensive Cell Profiling**: Extracts over 500 features covering intensity, morphology, texture, and spatial relationships

### CellProfiler Configuration

Key CellProfiler modules:

- **IdentifyPrimaryObjects**: Detects nuclei (10-80 pixels) and barcode spots (2-10 pixels)
- **IdentifySecondaryObjects**: Uses propagation with Otsu three-class thresholding for cell detection
- **MeasureObjectIntensity/Texture/Granularity**: Captures diverse cellular phenotypic features
- **MeasureObjectNeighbors**: Quantifies spatial relationships between cells
- **Custom Modules**: Integrates `CallBarcodes` and `CompensateColors` for genetic readouts

## Implementation Notes

- **Quality Control Integration**: Embeds multiple quality checkpoints throughout the pipeline including alignment verification
- **Hierarchical Object Relationships**: Establishes parent-child relationships between detected objects (nuclei → cells → cytoplasm)
- **Data Organization**: Processes data by batch/plate with channels and cycles from both CP and SBS modalities
- **Computational Optimization**: Employs strategic downsampling and memory management for large datasets

## Integration Points

- **Inputs**: Requires multiple image types including CP corrected images, SBS corrected images, and SBS compensated images
- **Outputs**:
    - Feature data exported as spreadsheets organized by object type
    - Visualization overlays showing segmentation results
    - Barcode calls with gene annotations
- **Dependencies**: CellProfiler with custom plugins for barcode calling and color compensation
- **Terminal Pipeline**: Represents the final processing step that generates data for downstream biological analysis
