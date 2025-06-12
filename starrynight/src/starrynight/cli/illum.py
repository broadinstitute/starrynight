"""Illum Calculate module cli wrapper."""

from pathlib import Path

import click
from cloudpathlib import AnyPath, CloudPath

from starrynight.algorithms.illum_apply import (
    gen_illum_apply_cppipe,
    gen_illum_apply_load_data,
)
from starrynight.algorithms.illum_apply_sbs import (
    gen_illum_apply_sbs_cppipe,
    gen_illum_apply_sbs_load_data,
)
from starrynight.algorithms.illum_calc import (
    gen_illum_calc_cppipe,
    gen_illum_calc_load_data,
)


@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-m", "--path_mask", default=None)
@click.option("--sbs", is_flag=True, default=False)
@click.option("--use_legacy", is_flag=True, default=False)
@click.option("--exp_config", default=None)
@click.option("--uow", default=None)
def gen_illum_calc_load_data_cli(
    index: str,
    out: str,
    path_mask: str | None,
    sbs: bool,
    use_legacy: bool,
    exp_config: str | None,
    uow: str | None,
) -> None:
    """Generate illum calc loaddata file.

    Parameters
    ----------
    index : str
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    path_mask : str | None
        Path prefix mask to use. Can be local or a cloud path.
    sbs : bool
        Flag for treating as sbs images.
    use_legacy : bool
        Flag for using legacy names in loaddata.
    exp_config : str | None
        Experiment config json path. Can be local or a cloud path.
    uow : list[str] | None
        Unit of work list

    """
    if uow is not None:
        uow = uow.split(",")
    # If use_legacy, then exp_config path is required
    if use_legacy:
        assert exp_config is not None
        exp_config = AnyPath(exp_config)

    gen_illum_calc_load_data(
        AnyPath(index),
        AnyPath(out),
        path_mask,
        sbs,
        use_legacy,
        exp_config,
        uow,
    )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("--sbs", is_flag=True, default=False)
@click.option("--use_legacy", is_flag=True, default=False)
def gen_illum_calc_cppipe_cli(
    loaddata: str, out: str, workspace: str, sbs: bool, use_legacy: bool
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
    sbs : str | Mask
        Flag for treating as sbs images.
    use_legacy : bool
        Flag for using legacy cppipe.

    """
    gen_illum_calc_cppipe(
        AnyPath(loaddata), AnyPath(out), AnyPath(workspace), sbs, use_legacy
    )


# ====== Illum Apply
@click.command(name="loaddata")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("--illum", default=None)
@click.option("-m", "--path_mask", default=None)
@click.option("-n", "--nuclei", default=None)
@click.option("--sbs", is_flag=True, default=False)
@click.option("--use_legacy", is_flag=True, default=False)
@click.option("--exp_config", default=None)
@click.option("--uow", default=None)
def gen_illum_apply_load_data_cli(
    index: str,
    out: str,
    illum: str | Path | CloudPath | None,
    path_mask: str | None,
    nuclei: str | None,
    sbs: bool,
    use_legacy: bool,
    exp_config: str | None,
    uow: str | None,
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
    use_legacy : bool
        Flag for using legacy names in loaddata.
    exp_config : str | None
        Experiment config json path. Can be local or a cloud path.
    uow : list[str] | None
        Unit of work list

    """
    if uow is not None:
        uow = uow.split(",")

    if illum is not None:
        illum = AnyPath(illum)

    # If use_legacy, then exp_config path is required
    if use_legacy:
        assert exp_config is not None
        exp_config = AnyPath(exp_config)

    if not sbs:
        gen_illum_apply_load_data(
            AnyPath(index),
            AnyPath(out),
            path_mask,
            illum,
            use_legacy,
            exp_config,
            uow,
        )
    else:
        if use_legacy is False:
            assert nuclei is not None
        gen_illum_apply_sbs_load_data(
            AnyPath(index),
            AnyPath(out),
            path_mask,
            nuclei,
            illum,
            use_legacy,
            exp_config,
            uow,
        )


@click.command(name="cppipe")
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", required=True)
@click.option("-n", "--nuclei", default=None)
@click.option("-c", "--cell", default=None)
@click.option("--sbs", is_flag=True, default=False)
@click.option("--use_legacy", is_flag=True, default=False)
def gen_illum_apply_cppipe_cli(
    loaddata: str,
    out: str,
    workspace: str,
    nuclei: str | None,
    cell: str | None,
    sbs: bool,
    use_legacy: bool,
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
    nuclei : str | None
        Channel to use for nuceli
    cell : str
        Channel to use for cell
    sbs : str | Mask
        Flag for treating as sbs images.
    use_legacy : bool
        Flag for using legacy cppipe.

    """
    if not sbs:
        if use_legacy is False:
            assert cell and nuclei is not None
        gen_illum_apply_cppipe(
            AnyPath(loaddata),
            AnyPath(out),
            AnyPath(workspace),
            nuclei,
            cell,
            use_legacy,
        )
    else:
        if use_legacy is False:
            assert nuclei is not None
        gen_illum_apply_sbs_cppipe(
            AnyPath(loaddata),
            AnyPath(out),
            AnyPath(workspace),
            nuclei,
            use_legacy,
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


calc.add_command(gen_illum_calc_load_data_cli)
calc.add_command(gen_illum_calc_cppipe_cli)
apply.add_command(gen_illum_apply_load_data_cli)
apply.add_command(gen_illum_apply_cppipe_cli)

illum.add_command(calc)
illum.add_command(apply)
