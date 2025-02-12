"""Common dataframe operations."""

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
