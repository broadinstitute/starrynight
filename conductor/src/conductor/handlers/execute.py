"""Execute handler."""

from collections.abc import Callable
from pathlib import Path
from time import time

from cloudpathlib import AnyPath, CloudPath
from pipecraft.backend.base import Backend
from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig
from pipecraft.pipeline import Pipeline
from sqlalchemy import select
from sqlalchemy.orm import Session
from starrynight.modules import MODULE_REGISTRY
from starrynight.modules.common import DataConfig
from starrynight.modules.schema import SpecContainer

from conductor.constants import (
    ExecutorType,
    RunStatus,
)
from conductor.models.job import Job
from conductor.models.run import Run
from conductor.utils import get_scratch_path
from conductor.validators.run import Run as PyRun


def create_backend_for_pipe(
    pipe: Pipeline, executor: ExecutorType, runs_dir: Path | CloudPath
) -> Backend:
    """Create backend for pipeline.

    Parameters
    ----------
    pipe : Pipeline
        Pipeline instance.
    executor : ExecutorType
        Type of the executor.
    runs_dir : Path | CloudPath
        Path to save runs.

    Returns
    -------
    Backend
        Backend instance.

    """
    run_folder = f"run_{int(time())}"
    output_dir = runs_dir.joinpath(run_folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    scratch_dir = get_scratch_path().joinpath(run_folder)
    print(pipe.node_list)
    return SnakeMakeBackend(pipe, SnakeMakeConfig(), output_dir, scratch_dir)


def submit_job(
    db_session: Callable[[], Session],
    job_id: int,
    executor_type: ExecutorType = ExecutorType.LOCAL,
) -> PyRun:
    """Execute job.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    job_id: int
        Job ID.
    executor_type: ExecutorType
        Type of the executor.

    Returns
    -------
    PyRun
        Created run.

    """
    with db_session() as session:
        # Ensure the job exists
        job = session.scalar(select(Job).where(Job.id == job_id))
        assert job is not None

        # Create a pipecraft pipeline
        data = DataConfig(
            dataset_path=job.project.dataset_uri,
            storage_path=job.project.storage_uri,
            workspace_path=job.project.workspace_uri,
        )
        pipe = MODULE_REGISTRY[job.uid](
            data_config=data, spec=SpecContainer.model_validate(job.spec)
        ).pipe

        # Create a backend for execution
        executor = create_backend_for_pipe(
            pipe,
            executor_type,
            AnyPath(job.project.workspace_uri).joinpath("runs"),
        )
        executor.compile()

        # Execute the pipeline
        exec_run = executor.run()

        # prepare the dict, PosixPath are not JSON serializable
        exec_run_dict = exec_run.model_dump(exclude={"process"})
        exec_run_dict["log_path"] = str(exec_run.log_path)

        # Add a run record to DB
        run = Run(
            name=f"{job.name} | {executor.scratch_path.stem.split('_')[1]}",
            job_id=job.id,
            log_path=str(exec_run.log_path.resolve()),
            executor_type=executor_type,
            run_status=RunStatus.RUNNING,
            inputs=job.inputs,
            outputs=job.outputs,
            spec=job.spec,
            backend_run=exec_run_dict,
        )
        session.add(run)
        session.commit()

        pyrun = PyRun.model_validate(run)
    return pyrun
