"""SankeMake Backend for Pipeline execution."""

import os
import signal
from pathlib import Path
from subprocess import Popen, run
from types import NotImplementedType

from cloudpathlib import CloudPath
from mako.template import Template

from pipecraft.backend.base import Backend, BackendConfig, BaseBackendRun
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
    use_fluent_bit: bool = True
    force_execution: bool = True


class SnakeMakeBackendRun(BaseBackendRun):
    """Snakemake run object."""

    def terminate(self) -> None:
        """Terminate snakemake run."""
        os.kill(self.pid, signal.SIGTERM)

    def kill(self) -> None:
        """Kill snakemake run."""
        print(f"sending kill signal to PID: {self.pid}")
        os.kill(self.pid, signal.SIGKILL)
        os.kill(self.pid, signal.SIGKILL)


class SnakeMakeBackend(Backend):
    """SnakeMake backend.

    Attributes
    ----------
    pipeline : Pipeline
    config : SnakeMakeConfig
    output_dir : Path

    """

    def __init__(
        self,
        pipeline: Pipeline,
        config: SnakeMakeConfig,
        output_dir: Path | CloudPath,
        scratch_path: Path,
    ) -> None:
        """SnakeMakeBackend.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline to compile.
        config : SnakeMakeConfig
            SnakeMake backend config.
        output_dir : Path | CloudPath
            SnakeMake output dir.
        scratch_path : Path
            Scratch path.

        """
        self.pipeline = pipeline
        self.pipeline.compile()
        self.config = config
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.scratch_path = scratch_path
        self.template = Template(
            text=Path(__file__).parent.joinpath("templates/snakemake.mako").read_text(),
            output_encoding="utf-8",
        )
        self.fluent_bit_template = Template(
            text=Path(__file__)
            .parent.joinpath("templates/fluent.yaml.mako")
            .read_text(),
            output_encoding="utf-8",
        )
        self.snakefile = None

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
            self.snakefile = snakefile.decode("utf-8")
            f.writelines(self.snakefile)
        if self.config.use_fluent_bit:
            with self.output_dir.joinpath("fluent.yaml").open("w") as f:
                fluent_bit = self.fluent_bit_template.render()
                assert type(fluent_bit) is bytes
                self.fluent_bit = fluent_bit.decode("utf-8")
                f.writelines(self.fluent_bit)

    def run(self) -> SnakeMakeBackendRun:
        """Run SankeMake.

        Returns
        -------
        Path | CloudPath:
            Path to run log file.

        """
        self.compile()
        cwd = self.output_dir
        if isinstance(self.output_dir, CloudPath):
            bucket = self.output_dir.drive
            prefix = "/".join(self.output_dir.parts[2:])
            self.scratch_path.mkdir(exist_ok=True, parents=True)
            cwd = self.scratch_path
            # mount run dir
            run(["goofys", f"{bucket}:{prefix}", str(cwd.resolve())])
        cmd = []
        if self.config.background:
            cmd += ["nohup"]
        cmd += ["snakemake", "-c", str(self.config.cores)]
        if self.config.force_execution:
            cmd += ["-F"]
        if self.config.apptainer:
            cmd += ["--use-apptainer"]
        if self.config.print_exec:
            cmd += ["-p"]
        if self.config.use_fluent_bit:
            cmd += [" 2>&1 | fluent-bit -c fluent.yaml"]
        # keep this at the end
        if self.config.background:
            cmd += ["&"]
        cmd = " ".join(cmd)
        process = Popen(cmd, cwd=cwd, shell=True)
        run_obj = SnakeMakeBackendRun(
            pid=process.pid,
            log_path=self.output_dir.joinpath("nohup.out"),
            process=process,
        )
        return run_obj
