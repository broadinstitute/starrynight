"""Backends for Pipeline execution."""

from abc import ABC, abstractmethod
from pathlib import Path

from cloudpathlib import CloudPath
from pydantic import BaseModel

from pipecraft.pipeline import Pipeline


class BackendConfig(ABC, BaseModel):
    """Backend config."""

    background: bool = True


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
    def run(self) -> Path:
        """Run pipeline.

        Returns immediately after starting the backend.
        Use polling to check the progress of the run.

        Returns
        -------
        Path:
            Path to run log file.

        """
        pass
