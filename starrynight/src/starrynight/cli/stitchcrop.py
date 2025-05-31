"""Stitchcrop module cli wrapper."""

import click
from cloudpathlib import AnyPath
from conductor.handlers.job import Path

from starrynight.algorithms.stitchcrop_legacy import (
    gen_stitchcrop_pipeline,
    run_fiji_parallel,
)


@click.command(name="pipeline")
@click.option("-i", "--index", required=True)
@click.option("-o", "--out", required=True)
@click.option("-w", "--workspace", default=None)
@click.option("--images", default=None)
@click.option("--exp_config", default=None)
@click.option("-m", "--path_mask", default=None)
@click.option("--use_legacy", is_flag=True, default=False)
@click.option("--sbs", is_flag=True, default=False)
def gen_stitchcrop_pipeline_cli(
    index: str,
    out: str,
    workspace: str,
    images: str,
    exp_config: str | None,
    path_mask: str | None,
    use_legacy: bool,
    sbs: bool,
) -> None:
    """Generate preprocess loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output dir. Can be local or a cloud path.
    workspace : str
        Workspace dir. Can be local or a cloud path.
    images : str
        Images dir. Can be local or a cloud path.
    exp_config : str | None
        Experiment config json path. Can be local or a cloud path.
    path_mask : str | Mask
        Path prefix mask to use. Can be local or a cloud path.
    use_legacy : bool
        Flag for using legacy names in loaddata.
    sbs : bool
        Flag for using sbs images.

    """
    # If use_legacy, then exp_config path is required
    if use_legacy:
        assert exp_config is not None
        exp_config = AnyPath(exp_config)

    gen_stitchcrop_pipeline(
        AnyPath(index),
        AnyPath(out),
        AnyPath(workspace),
        AnyPath(images),
        path_mask,
        use_legacy,
        exp_config,
        sbs,
    )


@click.command(name="fiji")
@click.option("-p", "--pipeline", required=True)
@click.option("-f", "--fiji", default=None)
@click.option("-j", "--jobs", default=20)
def run_stitchcrop_legacy_cli(
    pipeline: str,
    fiji: str | None,
    jobs: int,
) -> None:
    """Run fiji with pipeline.

    Parameters
    ----------
    pipeline : str
        Pipeline dir path. Can be local or a cloud path.
    fiji_path : Path
        Path to fiji executable.
    jobs : int, optional
        Number of parallel jobs to use (default is 20).

    """
    if fiji is not None:
        fiji = Path(fiji)
    pipeline_files = [file for file in AnyPath(pipeline).glob("**/*.py")]
    if len(pipeline_files) == 0:
        print("Found 0 pipeline files. No work to be done. Exiting...")
        return
    run_fiji_parallel(pipeline_files, fiji, jobs)


@click.group()
def stitchcrop() -> None:
    """Stitch crop commands."""
    pass


stitchcrop.add_command(gen_stitchcrop_pipeline_cli)
stitchcrop.add_command(run_stitchcrop_legacy_cli)
