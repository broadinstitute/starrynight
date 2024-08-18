"""Job route handlers."""

from collections.abc import Callable
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from conductor.constants import (
    JobType,
    RunStatus,
    StepType,
    job_desc_dict,
    job_output_dict,
)
from conductor.models.job import Job
from conductor.models.run import Run
from conductor.validators.job import Job as PyJob
from conductor.validators.run import Run as PyRun


def create_job(db_session: Callable[[], Session], job: PyJob) -> PyJob:
    """Create job.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    job : PyJob
        Job instance.

    Returns
    -------
    PyJob
        Created job.

    """
    orm_object = Job(**job.model_dump(exclude={"id"}))
    with db_session() as session:
        session.add(orm_object)
        session.commit()
        job = PyJob.model_validate(orm_object)
    return job


def fetch_all_jobs(
    db_session: Callable[[], Session],
    step_id: int | None,
    limit: int = 10,
    offset: int = 0,
) -> list[PyJob]:
    """Fetch all jobs.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    step_id: int | None
        Step id to use as a filter.
    limit: int
        Number of results to return.
    offset: int
        Offset value to use for fetch.

    Returns
    -------
    list[PyJob]
        List of jobs.

    """
    with db_session() as session:
        if step_id is not None:
            jobs = session.scalars(
                select(Job).where(Job.step_id == step_id).limit(limit).offset(offset)
            ).all()
        else:
            jobs = session.scalars(select(Job).limit(limit).offset(offset)).all()
        jobs = [PyJob.model_validate(job) for job in jobs]
    return jobs


def fetch_job_count(db_session: Callable[[], Session], step_id: int | None) -> int:
    """Fetch step count.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    step_id: int | None
        Step id to use as filter.

    Returns
    -------
    int
        Job count

    """
    with db_session() as session:
        if step_id is not None:
            count = session.scalar(
                select(func.count()).select_from(Job).where(Job.step_id == step_id)
            )
        else:
            count = session.scalar(select(func.count()).select_from(Job))

        assert type(count) is int
    return count


def gen_orm_job(job_type: JobType) -> Job:
    """Create loadData job.

    Parameters
    ----------
    job_type : JobType
        Job type instance.

    Returns
    -------
    Job
        Job instance.

    """
    job = Job(
        name=job_type.value,
        type=job_type,
        description=job_desc_dict[job_type],
        outputs=job_output_dict[job_type],
    )
    return job


def create_jobs_for_step(step_type: StepType) -> list[Job]:
    """Create predefined jobs for the step.

    Parameters
    ----------
    step_type : StepType
        Step type instance.

    Returns
    -------
    list[Job]
        List of job instances.

    """
    orm_jobs = []
    if step_type is StepType.CP_ILLUM_CALC:
        orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
        orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
    elif step_type is StepType.CP_ILLUM_APPLY:
        orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
        orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
    elif step_type is StepType.CP_SEG_CHECK:
        orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
        orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
    elif step_type is StepType.CP_ST_CROP:
        orm_jobs.append(gen_orm_job(JobType.GEN_FIJI))
    elif step_type is StepType.BC_ILLUM_CALC:
        orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
        orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
    elif step_type is StepType.BC_ILLUM_APPLY_ALIGN:
        orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
        orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
    elif step_type is StepType.BC_PRE:
        orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
        orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
    elif step_type is StepType.BC_ST_CROP:
        orm_jobs.append(gen_orm_job(JobType.GEN_FIJI))
    elif step_type is StepType.ANALYSIS:
        orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
        orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
    return orm_jobs


def fetch_all_job_types() -> list[str]:
    """Fetch all job types.

    Returns
    -------
    list[str]
        List of job types.

    """
    job_types = [pt.value for pt in JobType]
    return job_types


def execute_job(db_session: Callable[[], Session], job_id: int) -> PyRun:
    """Execute job.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    job_id : int
        ID of the job to execute.

    Returns
    -------
    PyRun
        Instance of PyRun

    """
    with db_session() as session:
        job = session.scalar(select(Job).where(Job.id == job_id))
        assert type(job) is Job
        step = job.step
        project = step.project

        orm_object = Run(
            job_id=job_id,
            name=f"{project.name}-{step.name}-{job.name}-{datetime.now()}",
            status=RunStatus.PENDING,
        )

        session.add(orm_object)
        session.commit()
        run = PyRun.model_validate(orm_object)
    return run
