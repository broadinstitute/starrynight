"""Backends for Pipeline execution."""

from abc import ABC
from pathlib import Path
from types import NotImplementedType

from pipecraft.pipeline import (
    Container,
    Gather,
    InvokeShell,
    Pipeline,
    PyFunction,
    Scatter,
)


class Backend(ABC):
    """Abstract class for backends."""

    pass


class SnakeMakeConfig:
    """SnakeMake backend config."""

    pass


class SnakeMakeBackend(Backend):
    """SnakeMake backend.

    Attributes
    ----------
    pipeline : Pipeline
    config : SnakeMakeConfig
    sm_file_blocks : List[str]

    """

    def __init__(self, pipeline: Pipeline, config: SnakeMakeConfig) -> None:
        """SbnakeMakeBackend.

        Parameters
        ----------
        pipeline : Pipeline
            Pipeline to compile.
        config : SnakeMakeConfig
            SnakeMake backend config.

        """
        self.pipeline = pipeline
        self.pipeline.compile()
        self.config = config

    def add_all_rule_block(self: "SnakeMakeBackend") -> None:
        """Create rule block for all nodes."""
        outputs = []
        sep = ",\n        "
        for node in self.pipeline.pipeline.nodes:
            if len(node.output_paths) != 0:
                outputs.extend(node.output_paths)
        outputs = [f'"{out}"' for out in outputs]
        self.sm_file_blocks.append(
            f"""
rule all:
    input:
        {sep.join(outputs)}
"""
        )

    def add_pyfunc_block(self: "SnakeMakeBackend", node: PyFunction) -> None:
        """Add rule block for PyFunction node.

        Parameters
        ----------
        node : PyFunction
            PyFunction node.

        """
        sep = ",\n"
        self.sm_file_blocks.append(
            f"""
rule {node.name}:
    input:
        "{sep.join(node.input_paths)}"
    output:
        "{sep.join(node.output_paths)}",
    shell:
        "echo hello"
"""
        )

    def compile(self, output_dir: Path) -> None:
        """Compile SnakeMake pipeline.

        Parameters
        ----------
        output_dir : Path
            Path to save output files.

        """
        self.sm_file_blocks = []
        self.add_all_rule_block()
        for node in self.pipeline.pipeline.nodes:
            if isinstance(node, PyFunction):
                print(node)
                self.add_pyfunc_block(node)
            elif isinstance(node, InvokeShell):
                print(node)
            elif isinstance(node, Container):
                print(node)
            elif isinstance(node, Scatter):
                print(node)
            elif isinstance(node, Gather):
                print(node)
            else:
                raise NotImplementedType
        with output_dir.joinpath("Snakefile").open("w") as f:
            f.writelines(self.sm_file_blocks)
