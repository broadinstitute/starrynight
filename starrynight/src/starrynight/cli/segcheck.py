"""Segcheck module cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.segcheck import (
    gen_segcheck_cppipe,
    gen_segcheck_load_data,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-c", "--corr_images", default=None)
@click.option("-n", "--nuclei", default=None)
@click.option("--cell", default=None)
@click.option("-m", "--path_mask", default=None)
@click.option("--use_legacy", is_flag=True, default=False)
@click.option("--exp_config", default=None)
def gen_segcheck_load_data_cli(
    index: str,
    out: str,
    corr_images: str,
    nuclei: str | None,
    cell: str | None,
    path_mask: str | None,
    use_legacy: bool,
    exp_config: str | None,
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
    use_legacy : bool
        Flag for using legacy names in loaddata.
    exp_config : str | None
        Experiment config json path. Can be local or a cloud path.

    """
    # If use_legacy, then exp_config path is required
    if use_legacy:
        assert exp_config is not None
        exp_config = AnyPath(exp_config)
    else:
        assert nuclei and cell is not None

    gen_segcheck_load_data(
        AnyPath(index),
        AnyPath(out),
        path_mask,
        nuclei,
        cell,
        AnyPath(corr_images) if corr_images else None,
        use_legacy,
        exp_config,
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-n", "--nuclei", required=True)
@click.option("-c", "--cell", required=True)
@click.option("--sbs", is_flag=True, default=False)
@click.option("--use_legacy", is_flag=True, default=False)
def gen_segcheck_cppipe_cli(
    loaddata: str,
    out: str,
    workspace: str,
    nuclei: str,
    cell: str,
    sbs: bool,
    use_legacy: bool,
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
    use_legacy : bool
        Flag for using legacy cppipe.

    """
    if use_legacy is False:
        assert cell and nuclei is not None
    gen_segcheck_cppipe(
        AnyPath(loaddata),
        AnyPath(out),
        AnyPath(workspace),
        nuclei,
        cell,
        sbs,
        use_legacy,
    )


@click.group()
def segcheck() -> None:
    """Segcheck commands."""
    pass


segcheck.add_command(gen_segcheck_load_data_cli)
segcheck.add_command(gen_segcheck_cppipe_cli)
