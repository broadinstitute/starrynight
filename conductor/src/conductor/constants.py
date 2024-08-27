"""Starrynight constants."""

from enum import Enum

from pydantic import BaseModel


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
    GEN_INDEX : "Generate file index."
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

    GEN_INDEX = "Generate file index"
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
    StepType.GEN_INDEX: (
        """
        This step generates an index and an inventory of the data.
        All Other steps depend on this step.
        """
    ),
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

    RUN_STARRYNIGHT = "Run starrynight cli"
    GEN_INVENTORY = "Generate Inventory"
    GEN_INDEX = "Generate Index"
    GEN_LOADDATA = "Generate LoadData"
    GEN_CP_PIPE = "Generate CellProfiler Pipeline"
    RUN_CP = "Run CellProfiler Pipeline"
    GEN_FIJI = "Generate Fiji Script"
    RUN_FIJI = "Run Fiji Script"
    CUSTOM = "Custom job"


class JobInputType(Enum):
    """Job input types."""

    PATH = "path"
    PARQUET = "parquet"
    FILE_UPLOAD = "file_upload"


class JobInputSchema(BaseModel, use_enum_values=True):
    """Job input schema."""

    type: JobInputType
    value: str


class JobOutputType(Enum):
    """Job output types."""

    CSV = "csv"
    TXT = "txt"
    PARQUET = "parquet"


class JobOutputSchema(BaseModel, use_enum_values=True):
    """Job output schema."""

    type: JobOutputType
    uri: str


job_desc_dict = {
    JobType.RUN_STARRYNIGHT: "",
    JobType.GEN_INVENTORY: "",
    JobType.GEN_INDEX: "",
    JobType.GEN_LOADDATA: "",
    JobType.GEN_CP_PIPE: "",
    JobType.GEN_FIJI: "",
    JobType.CUSTOM: "",
}

job_output_dict = {
    JobType.RUN_STARRYNIGHT: {},
    JobType.GEN_INVENTORY: {"inventory": {"type": "parquet", "uri": ""}},
    JobType.GEN_INDEX: {"index": {"type": "parquet", "uri": ""}},
    JobType.GEN_LOADDATA: {"LoadData CSV": {"type": "csv", "uri": ""}},
    JobType.GEN_CP_PIPE: {"Cellprofiler Pipeline": {"type": "txt", "uri": ""}},
    JobType.GEN_FIJI: {"Fiji Script": {"type": "txt", "uri": ""}},
    JobType.CUSTOM: {},
}

job_input_dict = {
    JobType.RUN_STARRYNIGHT: {"cmd": {"type": "str", "value": ""}},
    JobType.GEN_INVENTORY: {"dataset_path": {"type": "path", "value": ""}},
    JobType.GEN_INDEX: {"inventory_path": {"type": "path", "value": ""}},
    JobType.GEN_LOADDATA: {"index_path": {"type": "path", "value": ""}},
    JobType.GEN_CP_PIPE: {"index_path": {"type": "path", "value": ""}},
    JobType.GEN_FIJI: {},
    JobType.RUN_CP: {
        "load_data_path": {"type": "path", "path": ""},
        "cp_pipe_path": {"type": "path", "path": ""},
    },
    JobType.RUN_FIJI: {"load_data_path": {"type": "path", "path": ""}},
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


class ExecutorType(Enum):
    """Executor type.

    Attributes
    ----------
    LOCAL : local
    AWS_BATCH : aws_batch

    """

    LOCAL = "local"
    AWS_BATCH = "aws_batch"
