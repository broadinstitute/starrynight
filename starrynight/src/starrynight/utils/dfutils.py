"""Common dataframe operations."""

import json
from pathlib import Path

import polars as pl


def get_batches(df: pl.LazyFrame) -> list[str]:
    batches = (
        df.filter(pl.col("batch_id").is_not_null())
        .select("batch_id")
        .unique()
        .to_series()
        .to_list()
    )
    return batches


def get_plates_by_batch(df: pl.LazyFrame, batch_id: str) -> list[str]:
    plates = (
        df.filter(pl.col("batch_id").eq(batch_id) & pl.col("plate_id").is_not_null())
        .select("plate_id")
        .unique()
        .to_series()
        .to_list()
    )
    return plates


def get_wells_by_batch_plate(
    df: pl.LazyFrame, batch_id: str, plate_id: str
) -> list[str]:
    wells = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("well_id").is_not_null()
        )
        .select("well_id")
        .unique()
        .to_series()
        .to_list()
    )
    return wells


def get_sites_by_batch_plate_well(
    df: pl.LazyFrame, batch_id: str, plate_id: str, well_id: str
) -> list[str]:
    sites = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("well_id").eq(well_id)
            & pl.col("site_id").is_not_null()
        )
        .select("site_id")
        .unique()
        .to_series()
        .to_list()
    )
    return sites


def gen_image_hierarchy(df: pl.LazyFrame) -> dict:
    hierarchy_dict = {}
    batches = get_batches(df)
    for batch in batches:
        plates = get_plates_by_batch(df, batch)
        hierarchy_dict[batch] = {}
        for plate in plates:
            wells = get_wells_by_batch_plate(df, batch, plate)
            hierarchy_dict[batch][plate] = {}
            for well in wells:
                sites = get_sites_by_batch_plate_well(df, batch, plate, well)
                hierarchy_dict[batch][plate][well] = sites
    return hierarchy_dict


def get_channels_by_batch_plate(
    df: pl.LazyFrame, batch_id: str, plate_id: str
) -> list[str]:
    channels = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("channel_dict").is_not_null()
        )
        .select(pl.col("channel_dict").explode().unique(maintain_order=True))
        .to_series()
        .to_list()
    )
    return channels


def get_functional_channel(
    df: pl.LazyFrame,
    batch_id: str,
    plate_id: str,
    function_type: str,
    config_path: Path | None = None,
) -> str:
    """Get the functional channel name for a specific biological function.

    Parameters
    ----------
    df : pl.LazyFrame
        DataFrame containing the image data.
    batch_id : str
        Batch ID to filter by.
    plate_id : str
        Plate ID to filter by.
    function_type : str
        The biological function to get the channel for (e.g., "nuclei", "cell").
    config_path : Optional[Path]
        Path to the channel mapping configuration. If None, uses default.

    Returns
    -------
    str
        The channel name for the requested function, or None if not found.

    """
    # Get all channels for this batch/plate
    available_channels = get_channels_by_batch_plate(df, batch_id, plate_id)

    # Load the channel type mapping
    if config_path is None:
        # Try to locate the default config file
        config_path = Path(__file__).parent.parent / "configs" / "channel_mapping.json"

    if not config_path.exists():
        # If no config, use some sensible defaults
        channel_types = {
            "segmentation": {
                "nuclei": ["DNA"],
                "cell": ["Cell"],
                "junction": ["Junction"],
            },
            "readouts": {
                "dna": ["DNA"],
                "general": ["GFP", "nIR"],
                "sbs": ["SBS_A", "SBS_C", "SBS_G", "SBS_T"],
            },
        }
    else:
        # Load from config
        with open(config_path) as f:
            config = json.load(f)
            channel_types = config.get("channel_types", {})

    # Find the appropriate channel type category (segmentation, readouts, etc.)
    for category, functions in channel_types.items():
        if function_type in functions:
            # This is the category we want
            functional_channels = functions[function_type]

            # Look for a match in available channels
            for func_channel in functional_channels:
                if func_channel in available_channels:
                    return func_channel

    # If no match found, return None
    return None


def get_cycles_by_batch_plate(
    df: pl.LazyFrame, batch_id: str, plate_id: str
) -> list[str]:
    cycles = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("cycle_id").is_not_null()
        )
        .select(pl.col("cycle_id"))
        .unique()
        .to_series()
        .to_list()
    )
    return cycles
