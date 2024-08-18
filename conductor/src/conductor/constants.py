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


class ParserType(Enum):
    """Project parser types.

    Attributes
    ----------
    OPS_VINCENT : ops vincent parser.

    """

    OPS_VINCENT = "ops_vincent"
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


step_desc_dict = {
    StepType.CP_ILLUM_CALC: "",
    StepType.CP_ILLUM_APPLY: "",
    StepType.CP_SEG_CHECK: "",
    StepType.CP_ST_CROP: "",
    StepType.BC_ILLUM_CALC: "",
    StepType.BC_ILLUM_APPLY_ALIGN: "",
    StepType.BC_PRE: "",
    StepType.BC_ST_CROP: "",
    StepType.ANALYSIS: "",
    StepType.CUSTOM: "",
}


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
    CUSTOM = "Custom job"


job_desc_dict = {
    JobType.GEN_LOADDATA: "",
    JobType.GEN_CP_PIPE: "",
    JobType.GEN_FIJI: "",
    JobType.CUSTOM: "",
}

job_output_dict = {
    JobType.GEN_LOADDATA: {"LoadData CSV": {"type": "csv", "uri": ""}},
    JobType.GEN_CP_PIPE: {"Cellprofiler Pipeline": {"type": "txt", "uri": ""}},
    JobType.GEN_FIJI: {"Fiji Script": {"type": "txt", "uri": ""}},
    JobType.CUSTOM: {},
}


class RunStatus(Enum):
    """Run status.

    Attributes
    ----------
    PENDING : pending
    RUNNING : running
    SUCCESS : success
    FAILED :  failed

    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
