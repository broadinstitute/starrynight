# Stitch and Crop (stitchcrop.py)

!!! Warning
    - This document contains bot-generated text and has not yet been reviewed by developers!

Stitches together multiple microscopy image tiles into a single composite image, enabling reconstruction of complete wells from multiple fields of view (FOVs).

## Key Components

- **ImageJ/Fiji Integration**: Uses Fiji's Grid/Collection Stitching plugin rather than CellProfiler for image stitching
- **Predefined Grid Layouts**: Includes optimized configurations for common tile layouts (52, 88, 256, 293, 316, 320, 394, 1332, 1364, 1396 tiles)
- **TileConfiguration Generation**: Automatically creates spatial relationship specifications for the stitching process

### ImageJ Configuration

Key ImageJ parameters:

- **Stitching Parameters**: 10% tile overlap, linear blending for seamless transitions
- **Quality Control**: Uses regression threshold (0.30) and displacement thresholds (2.50/3.50) for accurate alignment
- **Memory Optimization**: Keeps output virtual to minimize RAM usage while processing large composite images

## Implementation Notes

- **PyImageJ Bridge**: Directly calls ImageJ plugins through Python API rather than using external scripts
- **Coordinate Calculation**: Calculates approximate tile positions which are then refined during the stitching process
- **Parameter Optimization**: Balances memory usage against computation time for large image sets
- **Layout Strategy**: Adapts stitching configuration based on the number of tiles per well
