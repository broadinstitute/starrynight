"""Starrynight constants."""

from enum import Enum


class ProjectType(Enum):
    """Project types.

    Attributes
    ----------
    OPS_GENERIC : generic ops pipeline.

    """

    OPS_GENERIC = "ops_generic"
    CUSTOM = "custom"


class StepType(Enum):
    """Step types.

    Attributes
    ----------
    CP_ILLUM_CALC : "CellPainting: Illumination Calculate"
    CP_ILLUM_APPLY : "CellPainting: Illumination Apply"
    CP_SEG_CHECK : "CellPainting: Segmentation Check"
    CP_ST_CROP : "CellPainting: Stitching and Cropping"
    BC_ILLUM_CALC : "Barcoding: Illumination Calculate"
    BC_ILLUM_APPLY_ALIGN : "Barcoding: Illumination Apply and Alignment"
    BC_PRE : "Barcoding: Preprocessing"
    BC_ST_CROP : "Barcoding: Stitching and Cropping"
    ANALYSIS : "Analysis"
    CUSTOM : "Custom step"

    """

    CP_ILLUM_CALC = "CellPainting: Illumination Calculate"
    CP_ILLUM_APPLY = "CellPainting: Illumination Apply"
    CP_SEG_CHECK = "CellPainting: Segmentation Check"
    CP_ST_CROP = "CellPainting: Stitching and Cropping"
    BC_ILLUM_CALC = "Barcoding: Illumination Calculate"
    BC_ILLUM_APPLY_ALIGN = "Barcoding: Illumination Apply and Alignment"
    BC_PRE = "Barcoding: Preprocessing"
    BC_ST_CROP = "Barcoding: Stitching and Cropping"
    ANALYSIS = "Analysis"
    CUSTOM = "Custom step"


class JobType(Enum):
    """Job types.

    Attributes
    ----------
    GEN_LOADDATA : "Generate LoadData"
    GEN_CP_PIPE : "Generate CellProfiler Pipeline"
    GEN_FIJI : "Generate Fiji Script"

    """

    GEN_LOADDATA = "Generate LoadData"
    GEN_CP_PIPE = "Generate CellProfiler Pipeline"
    GEN_FIJI = "Generate Fiji Script"
