"""Cron job handlers."""

from collections.abc import Callable

from cloudpathlib import AnyPath
from sqlalchemy.orm import Session

from conductor.handlers.run import fetch_all_unconcluded_runs, update_run
from conductor.validators.run import Run, RunStatus


def fetch_run_status(run: Run) -> RunStatus | None:
    """Fetch run status.

    Parameters
    ----------
    run : Run
        Run instance.

    Returns
    -------
    RunStatus | None
        Run status if changed.

    """
    log_path = run.log_path
    assert log_path is not None
    run_path = AnyPath(log_path).parent
    completed_file = run_path.joinpath("completed.txt")
    nohup_file = run_path.joinpath("nohup.out")
    if completed_file.exists() and completed_file.is_file():
        return RunStatus.SUCCESS
    else:
        # Check for SnakeMake erroe
        if nohup_file.read_text().find("WorkflowError") != -1:
            return RunStatus.FAILED
        if nohup_file.read_text().find("SyntaxError") != -1:
            return RunStatus.FAILED
        # Check nextflow error
        if nohup_file.read_text().find("ERROR") != -1:
            return RunStatus.FAILED
        return None


def update_run_status(db_session: Callable[[], Session]) -> None:
    """Update run status.

    Parameters
    ----------
    db_session: Callable[[], Session]
        Configured callable to create a db session.

    """
    unconcluded_runs = fetch_all_unconcluded_runs(db_session)
    print("runs fetched")
    print(unconcluded_runs)
    for run in unconcluded_runs:
        status = fetch_run_status(run)
        if status is not None:
            run.run_status = status
            update_run(db_session, run)
