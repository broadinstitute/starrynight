"""Segcheck module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.segcheck import (
    gen_segcheck_cppipe_by_batch_plate,
    gen_segcheck_load_data_by_batch_plate,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-c", "--corr_images", required=True)
@click.option("-n", "--nuclei", required=True)
@click.option("--cell", required=True)
@click.option("-m", "--path_mask", default=None)
@click.option("--sbs", is_flag=True, default=False)
def gen_segcheck_load_data(
    index: str,
    out: str,
    corr_images: str,
    nuclei: str,
    cell: str,
    path_mask: str | None,
    sbs: bool,
) -> None:
    """Generate segcheck loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    corr_images : str
        Corrected images dir. Can be local or a cloud path.
    nuclei : str
        Channel to use for nuceli segmentation
    cell : str
        Channel to use for cell segmentation
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    gen_segcheck_load_data_by_batch_plate(
        AnyPath(index), AnyPath(out), path_mask, nuclei, cell, AnyPath(corr_images), sbs
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-n", "--nuclei", required=True)
@click.option("-c", "--cell", required=True)
@click.option("--sbs", is_flag=True, default=False)
def gen_segcheck_cppipe(
    loaddata: str, out: str, workspace: str, nuclei: str, cell: str, sbs: bool
) -> None:
    """Generate segcheck cppipe file.

    Parameters
    ----------
    loaddata : str
        Loaddata dir path. Can be local or a cloud path.
    out : str
        Path to output directory. Can be local or a cloud path.
    workspace : str
        Path to workspace directory. Can be local or a cloud path.
    nuclei : str
        Channel to use for nuceli segmentation
    cell : str
        Channel to use for cell segmentation
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    gen_segcheck_cppipe_by_batch_plate(
        AnyPath(loaddata), AnyPath(out), AnyPath(workspace), nuclei, cell, sbs
    )


@click.group()
def segcheck() -> None:
    """Pre segcheck commands."""
    pass


segcheck.add_command(gen_segcheck_load_data)
segcheck.add_command(gen_segcheck_cppipe)
