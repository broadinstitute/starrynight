"""Cron job."""

import time
from functools import partial

import schedule

from conductor.database import get_db_session
from conductor.deploy.local.app import AppConfig
from conductor.handlers.cron import update_run_status
from conductor.utils import get_scratch_path

app_config = AppConfig(
    db_uri=f"sqlite+pysqlite:///{get_scratch_path().joinpath('test.db')}"
)
session = partial(get_db_session, app_config.db_uri)

schedule.every(2).seconds.do(update_run_status, db_session=session)

while True:
    schedule.run_pending()
    time.sleep(1)
