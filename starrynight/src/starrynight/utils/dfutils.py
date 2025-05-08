"""Common dataframe operations."""

import polars as pl

HIERARCHY_COLUMN_MAP_CP = {
    0: "batch_id",
    1: "plate_id",
    2: "well_id",
    3: "site_id",
}

HIERARCHY_COLUMN_MAP_SBS = {
    0: "batch_id",
    1: "plate_id",
    2: "cycle_id",
    3: "well_id",
    4: "site_id",
}


def gen_legacy_channel_map(
    plate_channel_list: list[str],
    exp_config: dict,
) -> dict:
    return {
        exp_config["cp_config"]["nuclei_channel"]: "DNA",
        exp_config["cp_config"]["cell_channel"]: "Phalloidin",
        exp_config["cp_config"]["mito_channel"]: "ZO1",
        "A": "A",
        "T": "T",
        "G": "G",
        "C": "C",
    }


def filter_images(df: pl.LazyFrame, for_sbs: bool = False) -> pl.LazyFrame:
    """Filter images based on whether they are for sbs or not.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    for_sbs : bool, optional
        Whether to filter for sbs images or not. Defaults to False.

    Returns
    -------
    pl.LazyFrame
        The filtered Polars LazyFrame.

    """
    if not for_sbs:
        return df.filter(
            pl.col("is_sbs_image").ne(True), pl.col("is_image").eq(True)
        )
    else:
        return df.filter(
            pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True)
        )


def filter_df_by_hierarchy_cp(
    df: pl.LazyFrame, levels: list[str]
) -> pl.LazyFrame:
    for i, level in enumerate(levels):
        df = df.filter(pl.col(HIERARCHY_COLUMN_MAP_CP[i]).eq(level))
    return df


def filter_df_by_hierarchy_sbs(
    df: pl.LazyFrame, levels: list[str]
) -> pl.LazyFrame:
    for i, level in enumerate(levels):
        df = df.filter(pl.col(HIERARCHY_COLUMN_MAP_SBS[i]).eq(level))
    return df


def filter_df_by_hierarchy(
    df: pl.LazyFrame, levels: list[str], for_sbs: bool = False
) -> pl.LazyFrame:
    if not for_sbs:
        return filter_df_by_hierarchy_cp(df, levels)
    else:
        return filter_df_by_hierarchy_sbs(df, levels)


def get_batches(df: pl.LazyFrame) -> list[str]:
    """Extract a list of unique batch IDs from a Polars LazyFrame.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.

    Returns
    -------
    list[str]
        A list of unique batch IDs.

    """
    batches = (
        df.filter(pl.col("batch_id").is_not_null())
        .select("batch_id")
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return batches


def filter_df_by_column_val(
    df: pl.LazyFrame, column: str, val: str
) -> pl.LazyFrame:
    filtered_df = df.filter(pl.col(column).eq(val))
    return filtered_df


def select_column_unique_vals(df: pl.LazyFrame, column: str) -> list[str]:
    """Extract a list of unique values for the given column from a Polars LazyFrame.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    column: str
        LazyFrame column

    Returns
    -------
    list[str]
        A list of unique batch IDs.

    """
    col_vals = (
        df.filter(pl.col(column).is_not_null())
        .select(column)
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return col_vals


def get_plates_by_batch(df: pl.LazyFrame, batch_id: str) -> list[str]:
    """Extract a list of unique plate IDs for a given batch ID.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    batch_id : str
        The batch ID to filter by.

    Returns
    -------
    list[str]
        A list of unique plate IDs for the given batch ID.

    """
    plates = (
        df.filter(
            pl.col("batch_id").eq(batch_id) & pl.col("plate_id").is_not_null()
        )
        .select("plate_id")
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return plates


def get_wells_by_batch_plate(
    df: pl.LazyFrame, batch_id: str, plate_id: str
) -> list[str]:
    """Extract a list of unique well IDs for a given batch and plate ID.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    batch_id : str
        The batch ID to filter by.
    plate_id : str
        The plate ID to filter by.

    Returns
    -------
    list[str]
        A list of unique well IDs for the given batch and plate ID.

    """
    wells = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("well_id").is_not_null()
        )
        .select("well_id")
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return wells


def get_wells_by_batch_plate_cycle(
    df: pl.LazyFrame, batch_id: str, plate_id: str, cycle_id: str
) -> list[str]:
    """Extract a list of unique well IDs for a given batch and plate ID.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    batch_id : str
        The batch ID to filter by.
    plate_id : str
        The plate ID to filter by.
    cycle_id : str
        The cycle ID to filter by.

    Returns
    -------
    list[str]
        A list of unique well IDs for the given batch and plate ID.

    """
    wells = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("cycle_id").eq(cycle_id)
            & pl.col("well_id").is_not_null()
        )
        .select("well_id")
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return wells


def get_sites_by_batch_plate_well(
    df: pl.LazyFrame, batch_id: str, plate_id: str, well_id: str
) -> list[str]:
    """Extract a list of unique site IDs for a given batch, plate, and well ID.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    batch_id : str
        The batch ID to filter by.
    plate_id : str
        The plate ID to filter by.
    well_id : str
        The well ID to filter by.

    Returns
    -------
    list[str]
        A list of unique site IDs for the given batch, plate, and well ID.

    """
    sites = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("well_id").eq(well_id)
            & pl.col("site_id").is_not_null()
        )
        .select("site_id")
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return sites


def get_sites_by_batch_plate_cycle_well(
    df: pl.LazyFrame, batch_id: str, plate_id: str, cycle_id: str, well_id: str
) -> list[str]:
    """Extract a list of unique site IDs for a given batch, plate, and well ID.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    batch_id : str
        The batch ID to filter by.
    plate_id : str
        The plate ID to filter by.
    cycle_id : str
        The cycle ID to filter by.
    well_id : str
        The well ID to filter by.

    Returns
    -------
    list[str]
        A list of unique site IDs for the given batch, plate, and well ID.

    """
    sites = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("cycle_id").eq(cycle_id)
            & pl.col("well_id").eq(well_id)
            & pl.col("site_id").is_not_null()
        )
        .select("site_id")
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return sites


def gen_image_hierarchy(
    df: pl.LazyFrame, levels: list[str]
) -> dict[str, dict] | list[str]:
    """Generate a hierarchical dictionary representing the image structure.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.

    levels : list[str]
        List of levels to recurse.

    Returns
    -------
    dict[str, dict] | list[str]
        A hierarchical dictionary. For example, keys can be batch IDs, then plate IDs,
        then cycle IDs, then well IDs, and values are lists of site IDs.

    """
    # No levels to recurse, return empty dict
    if len(levels) == 0:
        return []

    # get the current level values
    current_level_vals = select_column_unique_vals(df, levels[0])

    # If only one level, then last level to recurse, return a list
    if len(levels) == 1:
        hierarchy = current_level_vals

    # Multiple levels to recurse, return a dict
    else:
        hierarchy = {}
        for val in current_level_vals:
            next_level_df = filter_df_by_column_val(df, levels[0], val)
            hierarchy[val] = gen_image_hierarchy(next_level_df, levels[1:])
    return hierarchy


def get_channels_by_batch_plate(
    df: pl.LazyFrame, batch_id: str, plate_id: str
) -> list[str]:
    """Extract a list of unique channels for a given batch and plate ID.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    batch_id : str
        The batch ID to filter by.
    plate_id : str
        The plate ID to filter by.

    Returns
    -------
    list[str]
        A list of unique channels for the given batch and plate ID.

    """
    channels = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("channel_dict").is_not_null()
        )
        .select(pl.col("channel_dict").explode().unique(maintain_order=True))
        .collect()
        .to_series()
        .to_list()
    )
    return channels


def get_channels_from_df(df: pl.LazyFrame) -> list[str]:
    """Extract a list of unique channels for a LazyFrame.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.

    Returns
    -------
    list[str]
        A list of unique channels for the given LazyFrame.

    """
    channels = (
        df.filter(pl.col("channel_dict").is_not_null())
        .select(pl.col("channel_dict").explode().unique(maintain_order=True))
        .collect()
        .to_series()
        .to_list()
    )
    return channels


def get_cycles_from_df(df: pl.LazyFrame) -> list[str]:
    """Extract a list of unique cycle IDs for a given LazyFrame.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.

    Returns
    -------
    list[str]
        A list of unique cycle IDs for the given LazyFrame.

    """
    cycles = (
        df.filter(pl.col("cycle_id").is_not_null())
        .select(pl.col("cycle_id"))
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return cycles


def get_cycles_by_batch_plate(
    df: pl.LazyFrame, batch_id: str, plate_id: str
) -> list[str]:
    """Extract a list of unique cycle IDs for a given batch and plate ID.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.
    batch_id : str
        The batch ID to filter by.
    plate_id : str
        The plate ID to filter by.

    Returns
    -------
    list[str]
        A list of unique cycle IDs for the given batch and plate ID.

    """
    cycles = (
        df.filter(
            pl.col("batch_id").eq(batch_id)
            & pl.col("plate_id").eq(plate_id)
            & pl.col("cycle_id").is_not_null()
        )
        .select(pl.col("cycle_id"))
        .unique()
        .collect()
        .to_series()
        .to_list()
    )
    return cycles


def get_default_path_prefix(df: pl.LazyFrame) -> str:
    """Extract the default path prefix from a Polars LazyFrame.

    Parameters
    ----------
    df : pl.LazyFrame
        The input Polars LazyFrame.

    Returns
    -------
    str
        The default path prefix for the given dataframe.

    """
    default_path_prefix = (
        df.select(pl.col("prefix")).unique().collect().to_series().to_list()[0]
    )
    return default_path_prefix
