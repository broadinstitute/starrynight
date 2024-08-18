"""Job route handlers."""

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from conductor.constants import JobType, StepType
from conductor.models.job import Job
from conductor.validators.job import Job as PyJob


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
        orm_jobs.append(
            Job(
                name=JobType.GEN_LOADDATA.value,
                type=JobType.GEN_LOADDATA,
                description="",
            )
        )
        orm_jobs.append(
            Job(
                name=JobType.GEN_CP_PIPE.value, type=JobType.GEN_CP_PIPE, description=""
            )
        )
    if step_type is StepType.CP_ILLUM_APPLY:
        orm_jobs.append(
            Job(
                name=JobType.GEN_LOADDATA.value,
                type=JobType.GEN_LOADDATA,
                description="",
            )
        )
        orm_jobs.append(
            Job(
                name=JobType.GEN_CP_PIPE.value, type=JobType.GEN_CP_PIPE, description=""
            )
        )
    if step_type is StepType.CP_SEG_CHECK:
        orm_jobs.append(
            Job(
                name=JobType.GEN_LOADDATA.value,
                type=JobType.GEN_LOADDATA,
                description="",
            )
        )
        orm_jobs.append(
            Job(
                name=JobType.GEN_CP_PIPE.value, type=JobType.GEN_CP_PIPE, description=""
            )
        )
    if step_type is StepType.CP_ST_CROP:
        orm_jobs.append(
            Job(name=JobType.GEN_FIJI.value, type=JobType.GEN_FIJI, description="")
        )
    if step_type is StepType.BC_ILLUM_CALC:
        orm_jobs.append(
            Job(
                name=JobType.GEN_LOADDATA.value,
                type=JobType.GEN_LOADDATA,
                description="",
            )
        )
        orm_jobs.append(
            Job(
                name=JobType.GEN_CP_PIPE.value, type=JobType.GEN_CP_PIPE, description=""
            )
        )
    if step_type is StepType.BC_ILLUM_APPLY_ALIGN:
        orm_jobs.append(
            Job(
                name=JobType.GEN_LOADDATA.value,
                type=JobType.GEN_LOADDATA,
                description="",
            )
        )
        orm_jobs.append(
            Job(
                name=JobType.GEN_CP_PIPE.value, type=JobType.GEN_CP_PIPE, description=""
            )
        )
    if step_type is StepType.BC_PRE:
        orm_jobs.append(
            Job(
                name=JobType.GEN_LOADDATA.value,
                type=JobType.GEN_LOADDATA,
                description="",
            )
        )
        orm_jobs.append(
            Job(
                name=JobType.GEN_CP_PIPE.value, type=JobType.GEN_CP_PIPE, description=""
            )
        )
    if step_type is StepType.BC_ST_CROP:
        orm_jobs.append(
            Job(name=JobType.GEN_FIJI.value, type=JobType.GEN_FIJI, description="")
        )
    if step_type is StepType.ANALYSIS:
        orm_jobs.append(
            Job(
                name=JobType.GEN_LOADDATA.value,
                type=JobType.GEN_LOADDATA,
                description="",
            )
        )
        orm_jobs.append(
            Job(
                name=JobType.GEN_CP_PIPE.value, type=JobType.GEN_CP_PIPE, description=""
            )
        )
    return orm_jobs
