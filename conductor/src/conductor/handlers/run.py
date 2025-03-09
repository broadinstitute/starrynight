"""Run route handlers."""

from collections.abc import Callable

from cloudpathlib import AnyPath
from pipecraft.backend.snakemake import SnakeMakeBackendRun
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from conductor.constants import ExecutorType, RunStatus
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
    orm_object = Run(
        **run.model_dump(exclude={"id", "run_status"}), run_status=RunStatus.PENDING
    )
    with db_session() as session:
        session.add(orm_object)
        session.commit()
        run = PyRun.model_validate(orm_object)
    return run


def update_run(db_session: Callable[[], Session], run: PyRun) -> PyRun:
    """Update run.

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
    orm_object = Run(**run.model_dump())
    with db_session() as session:
        session.merge(orm_object)
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


def fetch_all_unconcluded_runs(
    db_session: Callable[[], Session],
    limit: int = 10,
    offset: int = 0,
) -> list[PyRun]:
    """Fetch all unconcluded runs.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
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
        runs = session.scalars(
            select(Run)
            .where(Run.run_status.in_([RunStatus.PENDING, RunStatus.RUNNING]))
            .limit(limit)
            .offset(offset)
        ).all()
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


def fetch_run_log(
    db_session: Callable[[], Session], run_id: int, offset: int = 500
) -> list[str]:
    """Fetch step count.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    run_id: int
        Run id.
    offset: int
        Log read offset.

    Returns
    -------
    list[str]
        Run log

    """
    with db_session() as session:
        run = session.scalar(select(Run).where(Run.id == run_id))
        assert run is not None
        assert run.log_path is not None
        log_path = AnyPath(run.log_path)
        log_lines = []
        with log_path.open() as f:
            for line in f.readlines()[-offset:]:
                log_lines.append(line)
    return log_lines


def kill_run(
    db_session: Callable[[], Session],
    run_id: int,
) -> PyRun:
    """Fetch all runs.

    Parameters
    ----------
    db_session : Callable[[], Session]
        Configured callable to create a db session.
    run_id: int
        run id to kill.

    Returns
    -------
    PyRun
        Run object.

    """
    with db_session() as session:
        orm_run = session.scalar(select(Run).where(Run.id == run_id))
        run = PyRun.model_validate(orm_run)
        if run.executor_type is ExecutorType.SNAKEMAKE:
            exec_run = SnakeMakeBackendRun(**run.backend_run)
            exec_run.kill()
            orm_run.run_status = RunStatus.FAILED
            session.add(orm_run)
            session.commit()
        # updated run
        run = PyRun.model_validate(orm_run)
    return run
