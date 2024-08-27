"""Create unit of work for gen index."""

from pathlib import Path

from cloudpathlib import CloudPath
from pipecraft.node import UnitOfWork


def create_work_unit_gen_inv(out_dir: Path | CloudPath) -> list[UnitOfWork]:
    """Create units of work for Generate Inv step.

    Parameters
    ----------
    out_dir : Path | CloudPath
        Path to load data csv. Can be local or cloud.

    Returns
    -------
    list[UnitOfWork]
        List of unit of work.

    """
    uow_list = [
        UnitOfWork(
            inputs={},
            outputs={
                "inventory": [out_dir.joinpath("inventory.parquet").resolve().__str__()]
            },
        )
    ]

    return uow_list


def create_work_unit_gen_index(out_dir: Path | CloudPath) -> list[UnitOfWork]:
    """Create units of work for Generate Index step.

    Parameters
    ----------
    out_dir : Path | CloudPath
        Path to load data csv. Can be local or cloud.

    Returns
    -------
    list[UnitOfWork]
        List of unit of work.

    """
    uow_list = [
        UnitOfWork(
            inputs={
                "inventory": [out_dir.joinpath("inventory.parquet").resolve().__str__()]
            },
            outputs={"index": [out_dir.joinpath("index.parquet").resolve().__str__()]},
        )
    ]

    return uow_list
