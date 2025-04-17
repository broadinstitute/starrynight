"""Illum Calculate module cli wrapper."""

from pathlib import Path

import click
from cloudpathlib import AnyPath, CloudPath

from starrynight.algorithms.illum_apply import (
    gen_illum_apply_cppipe_by_batch_plate,
    gen_illum_apply_load_data_by_batch_plate,
)
from starrynight.algorithms.illum_apply_sbs import (
    gen_illum_apply_sbs_cppipe_by_batch_plate,
    gen_illum_apply_sbs_load_data_by_batch_plate,
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
@click.option("-n", "--nuclei", default=None)
@click.option("--sbs", is_flag=True, default=False)
def gen_illum_apply_load_data(
    index: str,
    out: str,
    illum: str | Path | CloudPath | None,
    path_mask: str | None,
    nuclei: str | None,
    sbs: bool,
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
    nuclei : str
        Channel to use for nuceli in sbs pipeline
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    if illum is not None:
        illum = AnyPath(illum)
    if not sbs:
        gen_illum_apply_load_data_by_batch_plate(
            AnyPath(index), AnyPath(out), path_mask, illum
        )
    else:
        assert nuclei is not None
        gen_illum_apply_sbs_load_data_by_batch_plate(
            AnyPath(index), AnyPath(out), path_mask, nuclei, illum
        )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-n", "--nuclei", required=True)
@click.option("-c", "--cell", default=None)
@click.option("--sbs", is_flag=True, default=False)
def gen_illum_apply_cppipe(
    loaddata: str, out: str, workspace: str, nuclei: str, cell: str | None, sbs: bool
) -> None:
    """Generate illum apply cppipe file.

    Parameters
    ----------
    loaddata : str
        Loaddata dir path. Can be local or a cloud path.
    out : str
        Path to output directory. Can be local or a cloud path.
    workspace : str
        Path to workspace directory. Can be local or a cloud path.
    nuclei : str
        Channel to use for nuceli
    cell : str
        Channel to use for cell
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    if not sbs:
        assert cell is not None
        gen_illum_apply_cppipe_by_batch_plate(
            AnyPath(loaddata), AnyPath(out), AnyPath(workspace), nuclei, cell
        )
    else:
        gen_illum_apply_sbs_cppipe_by_batch_plate(
            AnyPath(loaddata), AnyPath(out), AnyPath(workspace), nuclei
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
