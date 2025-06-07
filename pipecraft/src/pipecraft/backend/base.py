"""Backends for Pipeline execution."""

from abc import ABC, abstractmethod
from pathlib import Path
from pprint import pprint
from subprocess import Popen

from cloudpathlib import CloudPath
from pydantic import BaseModel, ConfigDict, SkipValidation

from pipecraft.pipeline import Pipeline


class BackendConfig(ABC, BaseModel):
    """Backend config."""

    background: bool = True


class BaseBackendRun(ABC, BaseModel):
    """Abstract class for backend runs.

    Attributes
    ----------
    pid : int
    log_path: Path | CloudPath

    """

    pid: int
    log_path: Path | CloudPath
    process: SkipValidation[Popen]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def terminate(self) -> None:
        """Terminate the run."""
        pass

    @abstractmethod
    def kill(self) -> None:
        """Kill the run."""
        pass

    def get_log(self) -> list[str]:
        """Get run log."""
        with self.log_path.open() as f:
            return f.readlines()

    def print_log(self) -> None:
        """Print run log."""
        with self.log_path.open() as f:
            pprint(f.readlines())

    def wait(self, log: bool = False) -> None:
        """Wait for execution to complete."""
        self.process.wait()


class Backend(ABC):
    """Abstract class for backends.

    Attributes
    ----------
    pipeline : Pipeline
    config : BackendConfig
    output_dir : Path

    """

    def __init__(
        self, pipeline: Pipeline, config: BackendConfig, output_dir: Path | CloudPath
    ) -> None:
        """SbnakeMakeBackend.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline to compile.
        config : BackendConfig
            Backend config.
        output_dir : Path | CloudPath
            Backend output dir.

        """
        self.pipeline = pipeline
        self.config = config

    @abstractmethod
    def compile(self) -> None:
        """Compile pipeline."""
        pass

    @abstractmethod
    def run(self) -> BaseBackendRun:
        """Run pipeline.

        Returns immediately after starting the backend.
        Use polling to check the progress of the run.

        Returns
        -------
        BaseBackendRun:
            Backend run object.

        """
        pass
