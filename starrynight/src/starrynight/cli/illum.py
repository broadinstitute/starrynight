"""Illum Calculate module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.illum_apply import (
    gen_illum_apply_cppipe_by_batch_plate,
    gen_illum_apply_load_data_by_batch_plate,
)
from starrynight.algorithms.illum_calc import (
    gen_illum_calc_load_data_by_batch_plate,
    gen_illum_calculate_cppipe_by_batch_plate,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-m", "--path_mask", default=None)
@click.option("--sbs", is_flag=True, default=False)
def gen_illum_calc_load_data(
    index: str, out: str, path_mask: str | None, sbs: bool
) -> None:
    """Generate illum calc loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    gen_illum_calc_load_data_by_batch_plate(
        AnyPath(index), AnyPath(out), path_mask, sbs
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("--sbs", is_flag=True, default=False)
def gen_illum_calc_cppipe(loaddata: str, out: str, workspace: str, sbs: bool) -> None:
    """Generate illum calc cppipe file.

    Parameters
    ----------
    loaddata : str
        Loaddata dir path. Can be local or a cloud path.
    out : str
        Path to output directory. Can be local or a cloud path.
    workspace : str
        Path to workspace directory. Can be local or a cloud path.
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    gen_illum_calculate_cppipe_by_batch_plate(
        AnyPath(loaddata), AnyPath(out), AnyPath(workspace), sbs
    )


# ====== Illum Apply
@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("--illum", default=None)
@click.option("-m", "--path_mask", default=None)
@click.option("--sbs", is_flag=True, default=False)
def gen_illum_apply_load_data(
    index: str, out: str, illum: str, path_mask: str | None, sbs: bool
) -> None:
    """Generate illum apply loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    illum : str | None
        Illum dir. Can be local or a cloud path.
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    if illum is not None:
        illum = AnyPath(illum)
    gen_illum_apply_load_data_by_batch_plate(
        AnyPath(index), AnyPath(out), illum, path_mask, sbs
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("--sbs", is_flag=True, default=False)
def gen_illum_apply_cppipe(loaddata: str, out: str, workspace: str, sbs: bool) -> None:
    """Generate illum apply cppipe file.

    Parameters
    ----------
    loaddata : str
        Loaddata dir path. Can be local or a cloud path.
    out : str
        Path to output directory. Can be local or a cloud path.
    workspace : str
        Path to workspace directory. Can be local or a cloud path.
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    gen_illum_apply_cppipe_by_batch_plate(
        AnyPath(loaddata), AnyPath(out), AnyPath(workspace), sbs
    )


@click.group()
def calc() -> None:
    """Illum calc commands."""
    pass


@click.group()
def apply() -> None:
    """Illum apply commands."""
    pass


@click.group()
def illum() -> None:
    """Illum commands."""
    pass


calc.add_command(gen_illum_calc_load_data)
calc.add_command(gen_illum_calc_cppipe)
apply.add_command(gen_illum_apply_load_data)
apply.add_command(gen_illum_apply_cppipe)

illum.add_command(calc)
illum.add_command(apply)
