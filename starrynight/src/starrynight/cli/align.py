"""Align module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.align import (
    gen_align_cppipe_by_batch_plate,
    gen_align_load_data_by_batch_plate,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-c", "--corr_images", required=True)
@click.option("-n", "--nuclei", required=True)
@click.option("-m", "--path_mask", default=None)
def gen_align_load_data(
    index: str,
    out: str,
    corr_images: str,
    nuclei: str,
    path_mask: str | None,
) -> None:
    """Generate align loaddata file.

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
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.

    """
    gen_align_load_data_by_batch_plate(
        AnyPath(index), AnyPath(out), path_mask, nuclei, AnyPath(corr_images)
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-n", "--nuclei", required=True)
def gen_align_cppipe(loaddata: str, out: str, workspace: str, nuclei: str) -> None:
    """Generate align cppipe file.

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

    """
    gen_align_cppipe_by_batch_plate(
        AnyPath(loaddata), AnyPath(out), AnyPath(workspace), nuclei
    )


@click.group()
def align() -> None:
    """Align commands."""
    pass


align.add_command(gen_align_load_data)
align.add_command(gen_align_cppipe)
