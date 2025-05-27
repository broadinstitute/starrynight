"""Job route handlers."""

from collections.abc import Callable
from pathlib import Path

from cloudpathlib import AnyPath
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starrynight.experiments.common import DummyExperiment
from starrynight.experiments.registry import EXPERIMENT_REGISTRY
from starrynight.modules.common import StarrynightModule
from starrynight.modules.registry import MODULE_REGISTRY
from starrynight.pipelines.registry import PIPELINE_REGISTRY
from starrynight.schema import DataConfig

from conductor.constants import (
    ExecutorType,
    JobType,
    StepType,
    job_desc_dict,
    job_input_dict,
    job_output_dict,
)
from conductor.handlers.execute import submit_job
from conductor.models.job import Job
from conductor.models.project import Project
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


def update_job(db_session: Callable[[], Session], job: PyJob) -> PyJob:
    """Update job.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    job : PyJob
        Job instance.

    Returns
    -------
    PyJob
        Updated job.

    """
    orm_object = Job(**job.model_dump())
    with db_session() as session:
        session.merge(orm_object)
        session.commit()
        job = PyJob.model_validate(orm_object)
    return job


def fetch_all_jobs(
    db_session: Callable[[], Session],
    project_id: int | None,
    limit: int = 10,
    offset: int = 0,
) -> list[PyJob]:
    """Fetch all jobs.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    project_id: int | None
        Project id to use as a filter.
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
        if project_id is not None:
            jobs = session.scalars(
                select(Job)
                .where(Job.project_id == project_id)
                .limit(limit)
                .offset(offset)
            ).all()
        else:
            jobs = session.scalars(select(Job).limit(limit).offset(offset)).all()
        jobs = [PyJob.model_validate(job) for job in jobs]
    return jobs


def fetch_job_count(db_session: Callable[[], Session], project_id: int | None) -> int:
    """Fetch step count.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    project_id: int | None
        Project id to use as filter.

    Returns
    -------
    int
        Job count

    """
    with db_session() as session:
        if project_id is not None:
            count = session.scalar(
                select(func.count())
                .select_from(Job)
                .where(Job.project_id == project_id)
            )
        else:
            count = session.scalar(select(func.count()).select_from(Job))

        assert type(count) is int
    return count


def gen_orm_job(job_type: JobType, job: Job | None = None) -> Job:
    """Create loadData job.

    Parameters
    ----------
    job_type : JobType
        Job type instance.
    job: Job | None
        Job instance.

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
        inputs=job_input_dict[job_type],
    )
    return job


# def create_jobs_for_step(
#     step_type: StepType, step: Step | None = None, project: Project | None = None
# ) -> list[Job]:
#     """Create predefined jobs for the step.
#
#     Parameters
#     ----------
#     step_type : StepType
#         Step type instance.
#     step : Step | None
#         Step instance.
#     project : Project | None
#         Project instance.
#
#     Returns
#     -------
#     list[Job]
#         List of job instances.
#
#     """
#     orm_jobs = []
#     if step_type is StepType.GEN_INDEX:
#         assert project is not None
#         # Generate Inventory job
#         gen_inv_job = gen_orm_job(JobType.GEN_INVENTORY)
#         gen_inv_job.inputs["dataset_path"] = {
#             "type": "path",
#             "value": project.dataset_uri,
#         }
#         inventory_path = (
#             AnyPath(project.workspace_uri)
#             .joinpath("gen_index/inventory.parquet")
#             .__str__()
#         )
#         gen_inv_job.outputs["inventory"]["uri"] = inventory_path
#         orm_jobs.append(gen_inv_job)
#
#         # Generate Index job
#         gen_index_job = gen_orm_job(JobType.GEN_INDEX)
#         gen_index_job.inputs["inventory_path"] = {
#             "type": "path",
#             "value": inventory_path,
#         }
#         gen_index_job.outputs["index"]["uri"] = (
#             AnyPath(project.workspace_uri).joinpath("gen_index/index.parquet").__str__()
#         )
#         orm_jobs.append(gen_index_job)
#     if step_type is StepType.CP_ILLUM_CALC:
#         assert project is not None
#         # Generate load data job
#         gen_loaddata_job = gen_orm_job(JobType.GEN_LOADDATA)
#         gen_loaddata_job.inputs["index"] = {
#             "type": "path",
#             "value": AnyPath(project.workspace_uri)
#             .joinpath("index/index.parquet")
#             .__str__(),
#         }
#         loaddata_path = (
#             AnyPath(project.workspace_uri).joinpath("illum/loaddata.csv").__str__()
#         )
#         gen_loaddata_job.outputs["loaddata"]["uri"] = loaddata_path
#         orm_jobs.append(gen_loaddata_job)
#
#         # Generate cppipe job
#         gen_cppipe_job = gen_orm_job(JobType.GEN_CP_PIPE)
#         gen_cppipe_job.inputs["load_data_path"] = {
#             "type": "path",
#             "value": AnyPath(project.workspace_uri)
#             .joinpath("illum/loaddata.csv")
#             .__str__(),
#         }
#         cppipe_path = (
#             AnyPath(project.workspace_uri).joinpath("illum/illum_calc.cppipe").__str__()
#         )
#         gen_cppipe_job.outputs["cppipe"]["uri"] = cppipe_path
#         orm_jobs.append(gen_cppipe_job)
#     elif step_type is StepType.CP_ILLUM_APPLY:
#         orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
#         orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
#     elif step_type is StepType.CP_SEG_CHECK:
#         orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
#         orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
#     elif step_type is StepType.CP_ST_CROP:
#         orm_jobs.append(gen_orm_job(JobType.GEN_FIJI))
#     elif step_type is StepType.BC_ILLUM_CALC:
#         orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
#         orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
#     elif step_type is StepType.BC_ILLUM_APPLY_ALIGN:
#         orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
#         orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
#     elif step_type is StepType.BC_PRE:
#         orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
#         orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
#     elif step_type is StepType.BC_ST_CROP:
#         orm_jobs.append(gen_orm_job(JobType.GEN_FIJI))
#     elif step_type is StepType.ANALYSIS:
#         orm_jobs.append(gen_orm_job(JobType.GEN_LOADDATA))
#         orm_jobs.append(gen_orm_job(JobType.GEN_CP_PIPE))
#     return orm_jobs


def fetch_all_job_types() -> list[str]:
    """Fetch all job types.

    Returns
    -------
    list[str]
        List of job types.

    """
    job_types = [pt.value for pt in JobType]
    return job_types


def execute_job(
    db_session: Callable[[], Session],
    job_id: int,
    executor_type: ExecutorType = ExecutorType.LOCAL,
) -> PyRun:
    """Execute job.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    job_id : int
        ID of the job to execute.
    executor_type : ExecutorType
        Type to executor to use.

    Returns
    -------
    PyRun
        Instance of PyRun

    """
    run = submit_job(db_session, job_id, executor_type)
    return run


def gen_orm_job_from_module(module: StarrynightModule) -> Job:
    """Generate ORM job from starrynight module."""
    job = Job(
        name=module.spec.citations.algorithm[0].name,
        uid=module.module_name(),
        description=module.spec.citations.algorithm[0].description,
        spec=module.spec.model_dump(),
        outputs={},
        inputs={},
    )
    return job


def create_indexing_jobs_for_project(project: Project) -> list[Job]:
    """Create predefined indexing jobs for the project.

    Parameters
    ----------
    project: Project
        Project instance.

    Returns
    -------
    list[Job]
        List of job instances.

    """
    orm_jobs = []

    # Setup a dummy experiment and init the pipeline
    data = DataConfig(
        dataset_path=Path(project.dataset_uri),
        storage_path=Path(project.storage_uri),
        workspace_path=Path(project.workspace_uri),
    )
    indexing_pipeline = PIPELINE_REGISTRY["Indexing"]
    indexing_modules, indexing_pipeline = indexing_pipeline(data)

    # Extract the modules from the pipeline
    indexing_pipeline.compile()
    for module in indexing_modules:
        orm_jobs.append(gen_orm_job_from_module(module))
    return orm_jobs


def create_pipeline_jobs_for_project(project: Project, index_path: str) -> list[Job]:
    """Create pipelilne jobs for the project during the configure stage.

    Parameters
    ----------
    project: Project
        Project instance.
    index_path: str
        Path to the generated index.

    Returns
    -------
    list[Job]
        List of job instances.

    """
    orm_jobs = []

    # Setup the experiment and init the pipeline

    # fetch the experiment module and init using the index
    experiment = EXPERIMENT_REGISTRY[project.type]
    experiment = experiment.from_index(
        index_path=AnyPath(index_path), init_config=project.init_config
    )

    data = DataConfig(
        dataset_path=Path(project.dataset_uri),
        storage_path=Path(project.storage_uri),
        workspace_path=Path(project.workspace_uri),
    )
    project_pipeline = PIPELINE_REGISTRY[project.type]
    project_modules, project_pipeline = project_pipeline(data, experiment, {})

    # Extract the modules from the pipeline
    for module in project_modules:
        orm_jobs.append(gen_orm_job_from_module(module))
    return orm_jobs
