"""Cellprofiler cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.cp import run_cp_parallel


@click.command(name="cp")
@click.option("-p", "--cppipe", required=True)
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-j", "--jobs", default=50)
@click.option("--sbs", is_flag=True, default=False)
def invoke_cp(cppipe: str, loaddata: str, out: str, jobs: int, sbs: bool) -> None:
    """Invoke cellprofiler.

    Parameters
    ----------
    cppipe : str
        cppipe file path. Can be local or a cloud path.
    loaddata : str
        loaddata dir path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    jobs : int
        Number of jobs to launch.
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    # Check if cppipe path is not a dir
    if AnyPath(cppipe).is_dir():
        raise Exception("CPPIPE path is a dir, please provide path to a file.")

    load_data_files = [file for file in AnyPath(loaddata).glob("**/*.csv")]
    uow = []
    for file in load_data_files:
        uow.append((cppipe.resolve(), file.resolve()))

    if len(uow) == 0:
        print("Found 0 cppipe files. No work to be done. Exiting...")
        return
    run_cp_parallel(uow, AnyPath(out), jobs)  # pyright: ignore
