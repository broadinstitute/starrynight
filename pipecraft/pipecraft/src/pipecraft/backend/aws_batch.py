"""AWS Batch Backend for Pipeline execution."""

from pathlib import Path
from types import NotImplementedType

from cloudpathlib import CloudPath
from mako.template import Template

from pipecraft.backend.base import Backend
from pipecraft.node import (
    Container,
    Gather,
    InvokeShell,
    ParContainer,
    PyFunction,
    Scatter,
)
from pipecraft.pipeline import Pipeline


class AwsBatchConfig:
    """AwsBatch backend config."""

    pass


class AwsBatchBackend(Backend):
    """AwsBatch backend.

    Attributes
    ----------
    pipeline : Pipeline
    config : AwsBatchConfig

    """

    def __init__(
        self, pipeline: Pipeline, config: AwsBatchConfig, output_dir: Path | CloudPath
    ) -> None:
        """AwsBatchBackend.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline to compile.
        config : AwsBatchConfig
            AwsBatch backend config.
        output_dir : Path | CloudPath
            SnakeMake output dir.

        """
        self.pipeline = pipeline
        self.pipeline.compile()
        self.config = config
        self.output_dir = output_dir
        self.template = Template(
            text=Path(__file__).parent.joinpath("templates/aws_batch.mako").read_text(),
            output_encoding="utf-8",
        )

    def compile(self) -> None:
        """Compile AwsBatch pipeline."""
        containers = []
        pyfunctions = []
        invoke_shells = []

        for node in self.pipeline.pipeline.nodes:
            if isinstance(node, PyFunction):
                pyfunctions.append(node)
            elif isinstance(node, InvokeShell):
                invoke_shells.append(node)
            elif isinstance(node, Container):
                containers.append(node)
            elif isinstance(node, ParContainer):
                for container in node.containers:
                    containers.append(container)
            elif isinstance(node, Scatter):
                print(node)
            elif isinstance(node, Gather):
                print(node)
            else:
                raise NotImplementedType
        with self.output_dir.joinpath("aws_batch.py").open("w") as f:
            aws_batch = self.template.render(
                containers=containers,
                pyfunctions=pyfunctions,
                invoke_shells=invoke_shells,
            )
            assert type(aws_batch) is bytes
            aws_batch = aws_batch.decode("utf-8")
            f.writelines(aws_batch)
