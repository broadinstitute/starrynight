# Illumination Calculation (illum_calc.py)

Calculates illumination correction functions for microscopy images to normalize uneven illumination patterns, a critical preprocessing step that improves downstream analysis quality.

## Key Components

- **Image Downsampling/Upsampling**: Uses 4x downsampling during processing and 4x upsampling for final outputs to improve performance while maintaining quality

### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **CorrectIlluminationCalculate**: Uses median filtering (block size 60, filter size 20) to model background illumination patterns
- **Resize**: Implements bilinear interpolation for both downsampling (0.25x) and upsampling (4x)
- **SaveImages**: Stores illumination functions as NumPy (.npy) files

## Implementation Notes

- **SBS vs. Non-SBS Images**: Handles both standard images (batch/plate) and sequential images (batch/plate/cycle)
- **Performance Optimization**: Downsampling reduces processing time while maintaining correction quality
- **Smooth Gradients**: Bilinear interpolation preserves smooth illumination gradients during resizing operations
