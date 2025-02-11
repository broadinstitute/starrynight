"""PCP Experiment."""

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


class SBSConfig(BaseModel):
    """SBS experiment configuration."""

    im_per_well: int = Field(320)
    n_cycles: int = Field(12)
    img_overlap_pct: int = Field(10)
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    channel_list: list[str]
    acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)
    barcode_csv_path: Path | CloudPath


class CPConfig(BaseModel):
    """CP Experiment configuration."""

    im_per_well: int = Field(1364)
    img_overlap_pct: int = Field(10)
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    channel_list: list[str]
    acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)


class PCPGenericInitConfig(BaseModel):
    """PCP generic config for auto init from index."""

    barcode_csv_path: Path | CloudPath
    cp_img_overlap_pct: int = Field(10)
    cp_img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    cp_acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)
    sbs_img_overlap_pct: int = Field(10)
    sbs_img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    sbs_acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)


class PCPGeneric(Experiment):
    """PCP experiment configuration."""

    sbs_config: SBSConfig
    cp_config: CPConfig

    # users should not access it directly
    init_config_: PCPGenericInitConfig | None = None

    @staticmethod
    def from_index(index_path: Path, init_config: dict) -> Self:
        """Configure experiment with index."""
        init_config_parsed = PCPGenericInitConfig.model_validate(init_config)
        if index_path.name.endswith(".csv"):
            index_df = pl.scan_csv(index_path)
        else:
            index_df = pl.scan_parquet(index_path)

        # Get dataset_id from index
        dataset_id = (
            index_df.select(pl.col("dataset_id")).unique().collect().rows()[0][0]
        )

        # Filter for CP images
        cp_images_df = index_df.filter(
            pl.col("is_sbs_image").ne(True), pl.col("is_image").eq(True)
        )

        # Filter for sbs images
        sbs_images_df = index_df.filter(
            pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True)
        )

        # Construct CP config

        # Extract images per well
        cp_im_per_well = (
            cp_images_df.group_by(pl.col("well_id"))
            .agg(pl.col("key").count())
            .collect()
            .select(pl.col("key"))
            .unique()
            .rows()[0][0]
        )

        # Extract channel list
        cp_channel_lists = (
            cp_images_df.select(pl.col("channel_dict"))
            .collect()
            .to_dict()["channel_dict"]
        )
        # unique list of list adapted from https://stackoverflow.com/questions/3724551/uniqueness-for-list-of-lists
        cp_channel_list = [list(x) for x in set(tuple(x) for x in cp_channel_lists)]

        # Construct SBS config

        # Extract images per well
        sbs_im_per_well = (
            sbs_images_df.group_by(pl.col("well_id"))
            .agg(pl.col("key").count())
            .collect()
            .select(pl.col("key"))
            .unique()
            .rows()[0][0]
        )

        # Extract channel list
        sbs_channel_lists = (
            cp_images_df.select(pl.col("channel_dict"))
            .collect()
            .to_dict()["channel_dict"]
        )
        # unique list of list adapted from https://stackoverflow.com/questions/3724551/uniqueness-for-list-of-lists
        sbs_channel_list = [list(x) for x in set(tuple(x) for x in sbs_channel_lists)]
        return PCPGeneric(
            dataset_id=dataset_id,
            index_path=index_path,
            cp_config=CPConfig(
                im_per_well=cp_im_per_well,
                img_overlap_pct=init_config_parsed.cp_img_overlap_pct,
                img_frame_type=init_config_parsed.cp_img_frame_type,
                channel_list=cp_channel_list[0],
                acquisition_order=init_config_parsed.cp_acquisition_order,
            ),
            sbs_config=SBSConfig(
                im_per_well=sbs_im_per_well,
                img_overlap_pct=init_config_parsed.sbs_img_overlap_pct,
                img_frame_type=init_config_parsed.sbs_img_frame_type,
                channel_list=sbs_channel_list[0],
                acquisition_order=init_config_parsed.sbs_acquisition_order,
                barcode_csv_path=init_config_parsed.barcode_csv_path,
            ),
        )
