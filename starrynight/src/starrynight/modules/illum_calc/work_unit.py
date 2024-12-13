"""Create unit of work for Illumination Calculate step."""

from pathlib import Path

import polars as pl
from pipecraft.node import UnitOfWork


def create_work_unit_illum_calc(
    load_data_path: Path, illum_cppipe_path: Path
) -> list[UnitOfWork]:
    """Create units of work for Illumination Calculate step.

    Parameters
    ----------
    load_data_path : Path
        Path to load data csv.
    illum_cppipe_path : Path
        Path to illum cppipe file.

    Returns
    -------
    list[UnitOfWork]
        List of unit of work.

    """
    uow_list = [UnitOfWork(inputs={}, outputs={})]
    df = pl.read_csv(load_data_path)
    for i, plate_df in enumerate(df.partition_by("Plate")):
        pass

    return uow_list
