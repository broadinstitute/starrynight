"""Cellprofiler cli wrapper."""

from pathlib import Path

import click
from cloudpathlib import AnyPath, CloudPath

from starrynight.algorithms.cp import run_cp_parallel


@click.command(name="cp")
@click.option("-p", "--cppipe", required=True)
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-d", "--plugin_dir", default=None)
@click.option("-j", "--jobs", default=180)
@click.option("--sbs", is_flag=True, default=False)
def invoke_cp(
    cppipe: str | Path | CloudPath,
    loaddata: str | Path | CloudPath,
    out: str,
    plugin_dir: str | Path | None,
    jobs: int,
    sbs: bool,
) -> None:
    """Invoke cellprofiler.

    Parameters
    ----------
    cppipe : str
        cppipe file path. Can be local or a cloud path.
    loaddata : str
        loaddata dir path or file path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    plugin_dir : str
        Path to cellprofiler plugin directory.
    jobs : int
        Number of jobs to launch.
    sbs : bool
        Flag for treating as sbs images.

    """
    # Check if cppipe path is not a dir
    cppipe = AnyPath(cppipe)
    loaddata = AnyPath(loaddata)
    if cppipe.is_dir():
        raise Exception("CPPIPE path is a dir, please provide path to a file.")

    # Check if plugin_dir is passed
    if plugin_dir is not None:
        plugin_dir = Path(plugin_dir)

    if not loaddata.is_dir():
        load_data_files = [loaddata]
    load_data_files = [file for file in loaddata.glob("**/*.csv")]
    uow = []
    for file in load_data_files:
        uow.append((cppipe.resolve(), file.resolve()))

    if len(uow) == 0:
        print("Found 0 cppipe files. No work to be done. Exiting...")
        return
    run_cp_parallel(uow, AnyPath(out), plugin_dir, jobs)  # pyright: ignore
