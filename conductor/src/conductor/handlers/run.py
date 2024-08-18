"""Run route handlers."""

from collections.abc import Callable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from conductor.models.run import Run
from conductor.validators.run import Run as PyRun


def create_run(db_session: Callable[[], Session], run: PyRun) -> PyRun:
    """Create run.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.
    run : PyRun
        Run instance.

    Returns
    -------
    PyRun
        Created run.

    """
    orm_object = Run(**run.model_dump(exclude={"id"}))
    with db_session() as session:
        session.add(orm_object)
        session.commit()
        run = PyRun.model_validate(orm_object)
    return run


def fetch_all_runs(
    db_session: Callable[[], Session],
    job_id: int | None,
    limit: int = 10,
    offset: int = 0,
) -> list[PyRun]:
    """Fetch all runs.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    job_id: int | None
        Job id to use as a filter.
    limit: int
        Number of results to return.
    offset: int
        Offset value to use for fetch.

    Returns
    -------
    list[PyRun]
        List of runs.

    """
    with db_session() as session:
        if job_id is not None:
            runs = session.scalars(
                select(Run).where(Run.job_id == job_id).limit(limit).offset(offset)
            ).all()
        else:
            runs = session.scalars(select(Run).limit(limit).offset(offset)).all()
        runs = [PyRun.model_validate(run) for run in runs]
    return runs


def fetch_run_count(db_session: Callable[[], Session], job_id: int | None) -> int:
    """Fetch step count.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    job_id: int | None
        Job id to use as filter.

    Returns
    -------
    int
        Run count

    """
    with db_session() as session:
        if job_id is not None:
            count = session.scalar(
                select(func.count()).select_from(Run).where(Run.job_id == job_id)
            )
        else:
            count = session.scalar(select(func.count()).select_from(Run))

        assert type(count) is int
    return count
