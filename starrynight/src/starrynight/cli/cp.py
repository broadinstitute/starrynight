"""Cellprofiler cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.cp import run_cp_parallel


@click.command(name="cp")
@click.option("-p", "--cppipe", required=True)
@click.option("-l", "--loaddata", required=True)
@click.option("-o", "--out", required=True)
@click.option("-j", "--jobs", default=10)
def invoke_cp(cppipe: str, loaddata: str, out: str, jobs: int) -> None:
    """Invoke cellprofiler.

    Parameters
    ----------
    cppipe : str
        cppipe dir path. Can be local or a cloud path.
    loaddata : str
        loaddata dir path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    jobs : int
        Number of jobs to launch.

    """
    batches = [batch.stem for batch in AnyPath(loaddata).glob("*") if batch.is_dir()]
    cppipe_by_batch = {
        batch: [file for file in AnyPath(cppipe).joinpath(batch).glob("*.cppipe")]
        for batch in batches
    }
    uow = []
    for batch in batches:
        for cfile in cppipe_by_batch[batch]:
            uow.append(
                (
                    cfile.resolve(),
                    AnyPath(loaddata).joinpath(f"{batch}/{cfile.stem}.csv"),
                )
            )
    if len(uow) == 0:
        print("Found 0 cppipe files. No work to be done. Exiting...")
        return
    run_cp_parallel(uow, AnyPath(out), jobs)  # pyright: ignore
