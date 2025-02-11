"""Illum Calculate module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.illum_calc import (
    gen_illum_calc_load_data_by_plate,
    gen_illum_calculate_cppipe,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-m", "--path_mask", default=None)
def gen_illum_calc_load_data(index: str, out: str, path_mask: str | None) -> None:
    """Generate illum calc loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.

    """
    gen_illum_calc_load_data_by_plate(AnyPath(index), AnyPath(out), path_mask)


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
def gen_illum_calc_cppipe(
    loaddata: str,
    out: str,
    workspace: str,
) -> None:
    """Generate illum calc cppipe file.

    Parameters
    ----------
    loaddata : str
        Loaddata dir path. Can be local or a cloud path.
    out : str
        Path to output directory. Can be local or a cloud path.
    workspace : str
        Path to workspace directory. Can be local or a cloud path.

    """
    gen_illum_calculate_cppipe(AnyPath(loaddata), AnyPath(out), AnyPath(workspace))


@click.group()
def calc() -> None:
    """Illum commands."""
    pass


@click.group()
def illum() -> None:
    """Illum commands."""
    pass


calc.add_command(gen_illum_calc_load_data)
calc.add_command(gen_illum_calc_cppipe)

illum.add_command(calc)
