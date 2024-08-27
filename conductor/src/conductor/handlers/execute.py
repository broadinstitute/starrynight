"""Execute handler."""

from collections.abc import Callable
from pathlib import Path
from time import time

from cloudpathlib import AnyPath, CloudPath
from pipecraft.backend.base import Backend
from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig
from pipecraft.pipeline import Pipeline, Seq
from sqlalchemy import select
from sqlalchemy.orm import Session
from starrynight.modules.gen_index.pipe import (
    create_pipe_gen_index,
    create_pipe_gen_inv,
)
from starrynight.modules.illum_calc.pipe import create_pipe_illum_calc

from conductor.constants import (
    ExecutorType,
    JobType,
    RunStatus,
    StepType,
)
from conductor.models.job import Job
from conductor.models.run import Run
from conductor.utils import get_scratch_path
from conductor.validators.run import Run as PyRun


def create_pipe_for_job(job: Job) -> Pipeline:
    """Create pipeline for job.

    Parameters
    ----------
    job : Job
        Job instance.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    print(f"Job: {job}")
    if job.step.type is StepType.GEN_INDEX:
        if job.type is JobType.GEN_INVENTORY:
            pipe = create_pipe_gen_inv(
                AnyPath(job.inputs["dataset_path"]["value"]),
                AnyPath(job.outputs["inventory"]["uri"]).parent,
            )
            return pipe
        if job.type is JobType.GEN_INDEX:
            pipe = create_pipe_gen_index(
                AnyPath(job.inputs["inventory_path"]["value"]),
                AnyPath(job.outputs["index"]["uri"]).parent,
            )
            return pipe
    if job.step.type is StepType.CP_ILLUM_CALC:
        if job.type is JobType.RUN_CP:
            load_data_path = job.inputs["load_data_path"]["path"]
            illum_cppipe_path = job.inputs["load_data_path"]["path"]
            pipe = create_pipe_illum_calc(load_data_path, illum_cppipe_path)
            return pipe
        else:
            pipe = Seq([])
            return pipe
    else:
        pipe = Seq([])
        return pipe


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
        pipe = create_pipe_for_job(job)

        # Create a backend for execution
        executor = create_backend_for_pipe(
            pipe,
            executor_type,
            AnyPath(job.step.project.workspace_uri).joinpath("runs"),
        )
        executor.compile()

        # Execute the pipeline
        log_path = executor.run()

        # Add a run record to DB
        run = Run(
            name=f"{job.step.project.name} | {job.step.name} | {job.name} | {int(time())}",
            job_id=job.id,
            log_path=str(log_path.resolve()),
            executor_type=executor_type,
            run_status=RunStatus.RUNNING,
            inputs=job.inputs,
            outputs=job.outputs,
        )
        session.add(run)
        session.commit()

        pyrun = PyRun.model_validate(run)
    return pyrun
