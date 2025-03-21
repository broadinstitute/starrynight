# Image Alignment (align.py)

Registers images across different cycles in sequencing-based imaging (SBS) experiments, enabling accurate tracking of cells across multiple imaging cycles for applications like optical pooled screening.

## Key Components

- **Cross-Correlation Alignment**: Uses phase correlation to align images, maintaining relative positions of cellular structures
- **Nuclei Channel Reference**: Uses the DAPI/nuclei channel as the primary reference for alignment due to its stable features
- **Quality Control Metrics**: Computes and exports correlation values to identify problematic alignments

### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **Align**: Implements cross-correlation alignment (M_CROSS_CORRELATION) while maintaining original image size
- **MeasureColocalization**: Measures alignment quality between reference and aligned images
- **FlagImage**: Identifies images that failed to align properly (correlation < 0.9)

## Implementation Notes

- **Multi-Channel Strategy**: After aligning the nuclei channel, all other channels use the same transformation matrix to preserve spatial relationships
- **Reference Cycle**: Typically uses cycle 1 as the reference, aligning all subsequent cycles to it
- **Parallel Processing**: Organizes alignment by batch/plate to enable efficient parallel processing
