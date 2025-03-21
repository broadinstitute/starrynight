"""Analysis module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.analysis import (
    gen_analysis_cppipe_by_batch_plate,
    gen_analysis_load_data_by_batch_plate,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-c", "--corr_images", required=True)
@click.option("-p", "--comp_images", required=True)
@click.option("-m", "--path_mask", default=None)
def gen_analysis_load_data(
    index: str,
    out: str,
    corr_images: str,
    comp_images: str,
    path_mask: str | None,
) -> None:
    """Generate analysis loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    corr_images : str
        Corrected painting images dir. Can be local or a cloud path.
    comp_images : str
        Color compensated sbs images dir. Can be local or a cloud path.
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.

    """
    gen_analysis_load_data_by_batch_plate(
        AnyPath(index),
        AnyPath(out),
        path_mask,
        AnyPath(corr_images),
        AnyPath(comp_images),
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-b", "--barcode", required=True)
@click.option("-n", "--nuclei", required=True)
@click.option("-e", "--cell", required=True)
@click.option("-m", "--mito", required=True)
def gen_analysis_cppipe(
    loaddata: str,
    out: str,
    workspace: str,
    barcode: str,
    nuclei: str,
    cell: str,
    mito: str,
) -> None:
    """Generate analysis cppipe file.

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
    cell : str
        Channel to use for cell segmentation
    mito : str
        Channel to use for mito segmentation

    """
    gen_analysis_cppipe_by_batch_plate(
        AnyPath(loaddata),
        AnyPath(out),
        AnyPath(workspace),
        AnyPath(barcode),
        nuclei,
        cell,
        mito,
    )


@click.group()
def analysis() -> None:
    """Analysis commands."""
    pass


analysis.add_command(gen_analysis_load_data)
analysis.add_command(gen_analysis_cppipe)
