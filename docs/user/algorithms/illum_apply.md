# Illumination Apply (illum_apply.py)

!!! Warning
    - This document contains bot-generated text and has not yet been reviewed by developers!

Applies previously calculated illumination correction functions to microscopy images, normalizing uneven illumination patterns to improve downstream analysis accuracy.

## Key Components

- **Division-Based Correction**: Uses division method (DOS_DIVIDE) to normalize illumination, appropriate for fluorescence microscopy where illumination has multiplicative effects
- **Hierarchical Processing**: Handles both standard (batch/plate) and sequential (batch/plate/cycle) image organizations
- **Automatic Function Matching**: Automatically maps illumination functions to corresponding images based on metadata

### CellProfiler Configuration

Key CellProfiler modules:

- **CorrectIlluminationApply**: Implements division-based correction to normalize images
- **SaveImages**: Preserves corrected images as 16-bit TIFFs to maintain precision

## Implementation Notes

- **SBS vs. Non-SBS Images**: Handles both standard and cycle-based sequential imaging protocols
- **Modular Design**: Separates illumination function calculation from application, enabling reuse of correction functions
