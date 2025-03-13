"""Preprocess module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.preprocess import (
    gen_preprocess_cppipe_by_batch_plate,
    gen_preprocess_load_data_by_batch_plate,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-c", "--corr_images", required=True)
@click.option("-a", "--align_images", required=True)
@click.option("-n", "--nuclei", required=True)
@click.option("-m", "--path_mask", default=None)
def gen_preprocess_load_data(
    index: str,
    out: str,
    corr_images: str,
    align_images: str,
    nuclei: str,
    path_mask: str | None,
) -> None:
    """Generate preprocess loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    corr_images : str
        Corrected images dir. Can be local or a cloud path.
    align_images : str
        Aligned images dir. Can be local or a cloud path.
    nuclei : str
        Channel to use for nuceli segmentation
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.

    """
    gen_preprocess_load_data_by_batch_plate(
        AnyPath(index),
        AnyPath(out),
        path_mask,
        nuclei,
        AnyPath(corr_images),
        AnyPath(align_images),
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-b", "--barcode", required=True)
@click.option("-n", "--nuclei", required=True)
def gen_preprocess_cppipe(
    loaddata: str, out: str, workspace: str, barcode: str, nuclei: str
) -> None:
    """Generate preprocess cppipe file.

    Parameters
    ----------
    loaddata : str
        Loaddata dir path. Can be local or a cloud path.
    out : str
        Path to output directory. Can be local or a cloud path.
    workspace : str
        Path to workspace directory. Can be local or a cloud path.
    barcode : str
        Path to barcode csv. Can be local or a cloud path.
    nuclei : str
        Channel to use for nuceli segmentation

    """
    gen_preprocess_cppipe_by_batch_plate(
        AnyPath(loaddata), AnyPath(out), AnyPath(workspace), AnyPath(barcode), nuclei
    )


@click.group()
def preprocess() -> None:
    """Preprocess commands."""
    pass


preprocess.add_command(gen_preprocess_load_data)
preprocess.add_command(gen_preprocess_cppipe)
