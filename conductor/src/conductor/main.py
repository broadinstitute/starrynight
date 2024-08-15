"""FastAPI server entrypoint."""

# ruff: noqa: D103
from conductor.deploy.local.app import AppConfig, create_app
from conductor.utils import get_scratch_path

app_config = AppConfig(
    db_uri=f"sqlite+pysqlite:///{get_scratch_path().joinpath('test.db')}"
)
app = create_app(app_config)
