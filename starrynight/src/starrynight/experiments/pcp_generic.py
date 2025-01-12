"""PCP Experiment."""

from collections.abc import Callable
from pathlib import Path
from typing import Self

import polars as pl
from cloudpathlib import CloudPath
from pydantic import BaseModel, Field

from starrynight.experiments.common import (
    AcquisitionOrderType,
    Experiment,
    ImageFrameType,
)
from starrynight.schema import MeasuredInventory


class SBSConfig(BaseModel):
    """SBS experiment configuration."""

    im_per_well: int = Field(320)
    n_cycles: int = Field(12)
    img_overlap_pct: int = Field(10)
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    channel_dict: dict
    acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)
    barcode_csv_path: Path | CloudPath


class CPConfig(BaseModel):
    """CP Experiment configuration."""

    im_per_well: int = Field(1364)
    img_overlap_pct: int = Field(10)
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    channel_dict: dict
    acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)


class PCPGenericInitConfig(BaseModel):
    """PCP generic config for auto init from index."""

    barcode_csv_path: Path | CloudPath


class PCPGeneric(Experiment):
    """PCP experiment configuration."""

    sbs_config: SBSConfig
    cp_config: CPConfig
    # path_parser: Callable[[str], MeasuredInventory] | None

    # users should not access it directly
    init_config_: PCPGenericInitConfig | None = None

    @staticmethod
    def from_index(index_path: Path, init_config: PCPGenericInitConfig) -> Self:
        """Configure experiment with index."""
        if index_path.name.endswith(".csv"):
            index_df = pl.scan_csv(index_path)
        else:
            index_df = pl.scan_parquet(index_path)
