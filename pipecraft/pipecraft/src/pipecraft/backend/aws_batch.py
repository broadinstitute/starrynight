"""AWS Batch Backend for Pipeline execution."""

from pathlib import Path
from types import NotImplementedType

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
    """SnakeMake backend config."""

    pass


class AwsBatchBackend(Backend):
    """AwsBatch backend.

    Attributes
    ----------
    pipeline : Pipeline
    config : SnakeMakeConfig
    sm_file_blocks : List[str]

    """

    def __init__(self, pipeline: Pipeline, config: AwsBatchConfig) -> None:
        """AwsBatchBackend.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline to compile.
        config : AwsBatchConfig
            AwsBatch backend config.

        """
        self.pipeline = pipeline
        self.pipeline.compile()
        self.config = config
        self.template = Template(
            text=Path(__file__).parent.joinpath("templates/aws_batch.mako").read_text(),
            output_encoding="utf-8",
        )

    def compile(self, output_dir: Path) -> None:
        """Compile SnakeMake pipeline.

        Parameters
        ----------
        output_dir : Path
            Path to save output files.

        """
        self.sm_file_blocks = []
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
        with output_dir.joinpath("Snakefile").open("w") as f:
            snakefile = self.template.render(
                containers=containers,
                pyfunctions=pyfunctions,
                invoke_shells=invoke_shells,
            )
            assert type(snakefile) is bytes
            snakefile = snakefile.decode("utf-8")
            f.writelines(snakefile)
