"""Step route handlers."""

from collections.abc import Callable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from conductor.constants import ProjectType, StepType, step_desc_dict
from conductor.handlers.job import create_jobs_for_step
from conductor.models.project import Project
from conductor.models.step import Step
from conductor.validators.step import Step as PyStep


def create_step(db_session: Callable[[], Session], step: PyStep) -> PyStep:
    """Create step.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    step : PyStep
        Step instance.

    Returns
    -------
    PyStep
        Created step.

    """
    orm_object = Step(**step.model_dump(exclude={"id"}))
    with db_session() as session:
        session.add(orm_object)
        session.commit()
        step = PyStep.model_validate(orm_object)
    return step


def fetch_all_steps(
    db_session: Callable[[], Session],
    project_id: int | None,
    limit: int = 10,
    offset: int = 0,
) -> list[PyStep]:
    """Fetch all step.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    project_id: int | None
        Project id to use as filter.
    limit: int
        Number of results to return.
    offset: int
        Offset value to use for fetch.

    Returns
    -------
    list[PyStep]
        List of steps.

    """
    with db_session() as session:
        if project_id is not None:
            steps = session.scalars(
                select(Step)
                .where(Step.project_id == project_id)
                .limit(limit)
                .offset(offset)
            ).all()
        else:
            steps = session.scalars(select(Step).limit(limit).offset(offset)).all()
        steps = [PyStep.model_validate(step) for step in steps]
    return steps


def fetch_step_count(db_session: Callable[[], Session], project_id: int | None) -> int:
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
        Step count

    """
    with db_session() as session:
        if project_id is not None:
            count = session.scalar(
                select(func.count())
                .select_from(Step)
                .where(Step.project_id == project_id)
            )
        else:
            count = session.scalar(select(func.count()).select_from(Step))

        assert type(count) is int
    return count


def create_steps_for_project(project_type: ProjectType, project: Project) -> list[Step]:
    """Create predefined steps for the project.

    Parameters
    ----------
    project_type : ProjectType
        Project type instance.
    project: Project
        Project instance.

    Returns
    -------
    list[Step]
        List of step instances.

    """
    orm_steps = []
    if project_type is ProjectType.OPS_GENERIC:
        orm_steps.append(
            Step(
                name=StepType.GEN_INDEX.value,
                description=step_desc_dict[StepType.GEN_INDEX],
                type=StepType.GEN_INDEX,
                jobs=create_jobs_for_step(StepType.GEN_INDEX, project=project),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.CP_ILLUM_CALC.value,
                description=step_desc_dict[StepType.CP_ILLUM_CALC],
                type=StepType.CP_ILLUM_CALC,
                jobs=create_jobs_for_step(StepType.CP_ILLUM_CALC, project=project),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.CP_ILLUM_APPLY.value,
                description="",
                type=StepType.CP_ILLUM_APPLY,
                jobs=create_jobs_for_step(StepType.CP_ILLUM_APPLY),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.CP_SEG_CHECK.value,
                description="",
                type=StepType.CP_SEG_CHECK,
                jobs=create_jobs_for_step(StepType.CP_SEG_CHECK),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.CP_ST_CROP.value,
                description="",
                type=StepType.CP_ST_CROP,
                jobs=create_jobs_for_step(StepType.CP_ILLUM_APPLY),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.BC_ILLUM_CALC.value,
                description="",
                type=StepType.BC_ILLUM_CALC,
                jobs=create_jobs_for_step(StepType.BC_ILLUM_CALC),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.BC_ILLUM_APPLY_ALIGN.value,
                description="",
                type=StepType.BC_ILLUM_APPLY_ALIGN,
                jobs=create_jobs_for_step(StepType.BC_ILLUM_APPLY_ALIGN),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.BC_PRE.value,
                description="",
                type=StepType.BC_PRE,
                jobs=create_jobs_for_step(StepType.BC_PRE),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.BC_ST_CROP.value,
                description="",
                type=StepType.BC_ST_CROP,
                jobs=create_jobs_for_step(StepType.BC_ST_CROP),
            )
        )
        orm_steps.append(
            Step(
                name=StepType.ANALYSIS.value,
                description="",
                type=StepType.ANALYSIS,
                jobs=create_jobs_for_step(StepType.ANALYSIS),
            )
        )
    return orm_steps


def fetch_all_step_types() -> list[str]:
    """Fetch all step types.

    Returns
    -------
    list[str]
        List of step types.

    """
    step_types = [pt.value for pt in StepType]
    return step_types
