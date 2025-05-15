"""Analysis module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.analysis import (
    gen_analysis_cppipe,
    gen_analysis_load_data,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-c", "--corr_images", required=True)
@click.option("-p", "--comp_images", required=True)
@click.option("-m", "--path_mask", default=None)
@click.option("--use_legacy", is_flag=True, default=False)
@click.option("--exp_config", default=None)
def gen_analysis_load_data_cli(
    index: str,
    out: str,
    corr_images: str,
    comp_images: str,
    path_mask: str | None,
    use_legacy: bool,
    exp_config: str | None,
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
    use_legacy : bool
        Flag for using legacy names in loaddata.
    exp_config : str | None
        Experiment config json path. Can be local or a cloud path.

    """
    if use_legacy:
        assert exp_config is not None
        exp_config = AnyPath(exp_config)

    gen_analysis_load_data(
        AnyPath(index),
        AnyPath(out),
        path_mask,
        AnyPath(corr_images),
        AnyPath(comp_images),
        use_legacy,
        exp_config,
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-b", "--barcode", required=True)
@click.option("-n", "--nuclei", default=None)
@click.option("-e", "--cell", default=None)
@click.option("-m", "--mito", default=None)
@click.option("--use_legacy", is_flag=True, default=False)
def gen_analysis_cppipe_cli(
    loaddata: str,
    out: str,
    workspace: str,
    barcode: str,
    nuclei: str | None,
    cell: str | None,
    mito: str | None,
    use_legacy: bool,
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
    nuclei : str | None
        Channel to use for nuceli segmentation
    cell : str | None
        Channel to use for cell segmentation
    mito : str | None
        Channel to use for mito segmentation
    use_legacy : bool
        Flag for using legacy cppipe.

    """
    if use_legacy is False:
        assert nuclei and cell and mito is not None

    gen_analysis_cppipe(
        AnyPath(loaddata),
        AnyPath(out),
        AnyPath(workspace),
        AnyPath(barcode),
        nuclei,
        cell,
        mito,
        use_legacy,
    )


@click.group()
def analysis() -> None:
    """Analysis commands."""
    pass


analysis.add_command(gen_analysis_load_data_cli)
analysis.add_command(gen_analysis_cppipe_cli)
