"""PCP Experiment."""
# pyright: reportCallIssue=false

from pathlib import Path

import polars as pl
from cloudpathlib import CloudPath
from pydantic import BaseModel, Field

from starrynight.experiments.common import (
    AcquisitionOrderType,
    Experiment,
    ImageFrameType,
)
from starrynight.utils.dfutils import (
    filter_images,
    get_channels_from_df,
    select_column_unique_vals,
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
    nuclei_channel: str = Field("DNA")
    cell_channel: str = Field("CELL")
    mito_channel: str = Field("MITO")
    custom_channel_map: dict | None = None


class CPConfig(BaseModel):
    """CP Experiment configuration."""

    im_per_well: int = Field(1364)
    img_overlap_pct: int = Field(10)
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    channel_list: list[str]
    acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)
    nuclei_channel: str = Field("DNA")
    cell_channel: str = Field("CELL")
    mito_channel: str = Field("MITO")
    custom_channel_map: dict | None = None


class PCPGenericInitConfig(BaseModel):
    """PCP generic config for auto init from index."""

    barcode_csv_path: Path | CloudPath
    use_legacy: bool = Field(False)
    cp_img_overlap_pct: int = Field(10)
    cp_img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    cp_acquisition_order: AcquisitionOrderType = Field(
        AcquisitionOrderType.SNAKE
    )
    cp_custom_channel_map: dict | None = None
    sbs_img_overlap_pct: int = Field(10)
    sbs_img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    sbs_acquisition_order: AcquisitionOrderType = Field(
        AcquisitionOrderType.SNAKE
    )
    cp_nuclei_channel: str = Field("DNA")
    cp_cell_channel: str = Field("CELL")
    cp_mito_channel: str = Field("MITO")
    sbs_nuclei_channel: str = Field("DNA")
    sbs_cell_channel: str = Field("CELL")
    sbs_mito_channel: str = Field("MITO")
    sbs_custom_channel_map: dict | None = None


class PCPGeneric(Experiment):
    """PCP experiment configuration."""

    sbs_config: SBSConfig
    cp_config: CPConfig
    use_legacy: bool

    # users should not access it directly
    init_config_: PCPGenericInitConfig | None = None

    @staticmethod
    def get_init_config() -> PCPGenericInitConfig:
        return PCPGenericInitConfig(barcode_csv_path=Path())

    @staticmethod
    def from_index(index_path: Path, init_config: dict) -> "PCPGeneric":
        """Configure experiment with index."""
        # HACK: remove later after proper validation in front end canvas ui
        if init_config["sbs_custom_channel_map"] == "":
            init_config["sbs_custom_channel_map"] = None
        if init_config["cp_custom_channel_map"] == "":
            init_config["cp_custom_channel_map"] = None

        init_config_parsed = PCPGenericInitConfig.model_validate(init_config)
        if index_path.name.endswith(".csv"):
            index_df = pl.scan_csv(index_path)
        else:
            index_df = pl.scan_parquet(index_path)

        # Get dataset_id from index
        dataset_id = select_column_unique_vals(index_df, "dataset_id")[0]

        # Filter for CP images
        cp_images_df = filter_images(index_df)

        # Filter for sbs images
        sbs_images_df = filter_images(index_df, True)

        # Construct CP config

        # Extract images per well
        cp_im_per_well = (
            cp_images_df.group_by("batch_id", "plate_id", "well_id")
            .agg(pl.col("key").count())
            .collect()
            .select(pl.col("key"))
            .unique()
            .rows()[0][0]
        )

        # Extract channel list
        cp_channel_list = get_channels_from_df(cp_images_df)

        # Check custom channel map
        if init_config_parsed.cp_custom_channel_map is not None:
            for (
                cp_custom_channel
            ) in init_config_parsed.cp_custom_channel_map.keys():
                assert cp_custom_channel in cp_channel_list

        # Construct SBS config

        # Extract images per well
        sbs_im_per_well = (
            sbs_images_df.group_by(
                "batch_id", "plate_id", "cycle_id", "well_id"
            )
            .agg(pl.col("key").count())
            .collect()
            .select(pl.col("key"))
            .unique()
            .rows()[0][0]
        )
        # Extract number of cycles
        sbs_n_cycles = (
            sbs_images_df.select(pl.col("cycle_id").unique().count())
            .collect()
            .rows()[0][0]
        )

        # Extract channel list
        sbs_channel_list = get_channels_from_df(sbs_images_df)

        # Check custom channel map
        if init_config_parsed.sbs_custom_channel_map is not None:
            for (
                sbs_custom_channel
            ) in init_config_parsed.sbs_custom_channel_map.keys():
                assert sbs_custom_channel in sbs_channel_list

        return PCPGeneric(
            dataset_id=dataset_id,
            index_path=index_path.resolve(),
            use_legacy=init_config_parsed.use_legacy,
            cp_config=CPConfig(
                im_per_well=cp_im_per_well,
                img_overlap_pct=init_config_parsed.cp_img_overlap_pct,
                img_frame_type=init_config_parsed.cp_img_frame_type,
                channel_list=cp_channel_list,
                acquisition_order=init_config_parsed.cp_acquisition_order,
                nuclei_channel=init_config_parsed.cp_nuclei_channel,
                cell_channel=init_config_parsed.cp_cell_channel,
                mito_channel=init_config_parsed.cp_mito_channel,
                custom_channel_map=init_config_parsed.cp_custom_channel_map,
            ),
            sbs_config=SBSConfig(
                n_cycles=sbs_n_cycles,
                im_per_well=sbs_im_per_well,
                img_overlap_pct=init_config_parsed.sbs_img_overlap_pct,
                img_frame_type=init_config_parsed.sbs_img_frame_type,
                channel_list=sbs_channel_list,
                acquisition_order=init_config_parsed.sbs_acquisition_order,
                barcode_csv_path=init_config_parsed.barcode_csv_path,
                nuclei_channel=init_config_parsed.sbs_nuclei_channel,
                cell_channel=init_config_parsed.sbs_cell_channel,
                mito_channel=init_config_parsed.sbs_mito_channel,
                custom_channel_map=init_config_parsed.sbs_custom_channel_map,
            ),
        )
