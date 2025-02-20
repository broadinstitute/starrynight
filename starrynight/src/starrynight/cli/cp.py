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
        cppipe dir path. Can be local or a cloud path.
    loaddata : str
        loaddata dir path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    jobs : int
        Number of jobs to launch.
    sbs : str | Mask
        Flag for treating as sbs images.

    """
    batches = [batch.stem for batch in AnyPath(loaddata).glob("*") if batch.is_dir()]
    uow = []
    if not sbs:
        cppipe_by_batch = {
            batch: [file for file in AnyPath(cppipe).joinpath(batch).glob("*.cppipe")]
            for batch in batches
        }
        for batch in batches:
            for cfile in cppipe_by_batch[batch]:
                uow.append(
                    (
                        cfile.resolve(),
                        AnyPath(loaddata).joinpath(f"{batch}/{cfile.stem}.csv"),
                    )
                )

    else:
        for batch in batches:
            plates = [
                plate.stem
                for plate in AnyPath(loaddata).resolve().joinpath(batch).glob("*")
                if plate.is_dir()
            ]

            for plate in plates:
                cppipe_by_batch_plate = {
                    f"{batch}_{plate}": [
                        file
                        for file in AnyPath(cppipe)
                        .joinpath(batch, plate)
                        .glob("*.cppipe")
                    ]
                    for batch in batches
                }
                for cfile in cppipe_by_batch_plate[f"{batch}_{plate}"]:
                    uow.append(
                        (
                            cfile.resolve(),
                            AnyPath(loaddata).joinpath(
                                f"{batch}/{plate}/{cfile.stem}.csv"
                            ),
                        )
                    )
    if len(uow) == 0:
        print("Found 0 cppipe files. No work to be done. Exiting...")
        return
    run_cp_parallel(uow, AnyPath(out), jobs)  # pyright: ignore
