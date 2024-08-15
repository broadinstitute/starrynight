"""Schema for specifying experiment variables and generated outputs."""

from abc import ABC
from collections.abc import Callable
from enum import Enum

from pydantic import BaseModel, Field

from starrynight.schema import MeasuredInventory


class ImageMetadataGeneric(BaseModel):
    name: str
    batch_id: str
    plate_id: str
    site_id: str
    img_format: str
    assay_type: str
    channel_dict: dict


class ImageFrameType(Enum):
    ROUND = "round"
    SQUARE = "square"


class AcqusitionOrderType(Enum):
    SNAKE = "snake"
    ROWS = "rows"


class Experiment(BaseModel, ABC):
    dataset_id: str
    data_production_contact: str | None = None
    data_processing_contact: str | None = None


class SBSConfig(BaseModel):
    im_per_well: int = Field(320)
    n_cycles: int = Field(12)
    img_overlap_pct: int = Field(10)
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    channel_dict: dict
    acquisition_order: AcqusitionOrderType = Field(AcqusitionOrderType.SNAKE)


class CPConfig(BaseModel):
    im_per_well: int = Field(1364)
    img_overlap_pct: int = Field(10)
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    channel_dict: dict
    acquisition_order: AcqusitionOrderType = Field(AcqusitionOrderType.SNAKE)


class PCPGeneric(Experiment):
    path_parser: Callable[[str], MeasuredInventory]
    sbs_config: SBSConfig
    cp_config: CPConfig
