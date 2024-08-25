"""SankeMake Backend for Pipeline execution."""

from pathlib import Path
from subprocess import Popen
from types import NotImplementedType

from mako.template import Template

from pipecraft.backend.base import Backend, BackendConfig
from pipecraft.node import (
    Container,
    Gather,
    InvokeShell,
    ParContainer,
    PyFunction,
    Scatter,
)
from pipecraft.pipeline import Pipeline


class SnakeMakeConfig(BackendConfig):
    """SnakeMake backend config."""

    cores: int = 10
    docker: bool = False
    singularity: bool = False
    apptainer: bool = False
    print_exec: bool = False


class SnakeMakeBackend(Backend):
    """SnakeMake backend.

    Attributes
    ----------
    pipeline : Pipeline
    config : SnakeMakeConfig
    output_dir : Path

    """

    def __init__(
        self, pipeline: Pipeline, config: SnakeMakeConfig, output_dir: Path
    ) -> None:
        """SnakeMakeBackend.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline to compile.
        config : SnakeMakeConfig
            SnakeMake backend config.
        output_dir : Path
            SnakeMake output dir.

        """
        self.pipeline = pipeline
        self.pipeline.compile()
        self.config = config
        self.output_dir = output_dir
        self.template = Template(
            text=Path(__file__).parent.joinpath("templates/snakemake.mako").read_text(),
            output_encoding="utf-8",
        )

    def compile(self) -> None:
        """Compile SnakeMake pipeline.

        Parameters
        ----------
        output_dir : Path
            Path to save output files.

        """
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
        with self.output_dir.joinpath("Snakefile").open("w") as f:
            snakefile = self.template.render(
                containers=containers,
                pyfunctions=pyfunctions,
                invoke_shells=invoke_shells,
            )
            assert type(snakefile) is bytes
            snakefile = snakefile.decode("utf-8")
            f.writelines(snakefile)

    def run(self) -> Path:
        """Run SankeMake.

        Returns
        -------
        Path:
            Path to run log file.

        """
        cmd = []
        if self.config.background:
            cmd += ["nohup"]
        cmd += ["snakemake", "-c", str(self.config.cores)]
        if self.config.apptainer:
            cmd += ["--use-apptainer"]
        if self.config.print_exec:
            cmd += ["-p"]
        # keep this at the end
        if self.config.background:
            cmd += ["&"]
        cmd = " ".join(cmd)
        Popen(cmd, cwd=self.output_dir, shell=True)
        return self.output_dir.joinpath("nohup.log")
