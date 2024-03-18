"""
Backends for Pipeline execution.
"""

from abc import ABC
from pathlib import Path
from types import NotImplementedType
from typing import Generic, TypeVar

from pipecraft.pipeline import (
    Container,
    Gather,
    InvokeShell,
    Pipeline,
    PyFunction,
    Scatter,
)

B = TypeVar("B")
BConfig = TypeVar("BConfig")


class Backend(Generic[B, BConfig], ABC):
    pass


class SnakeMakeConfig:
    pass


class SnakeMakeBackend(Backend["SnakeMakeBackend", SnakeMakeConfig]):
    def __init__(
        self: "SnakeMakeBackend", pipeline: Pipeline, config: SnakeMakeConfig
    ) -> None:
        self.pipeline = pipeline
        self.pipeline.compile()
        self.config = config

    def add_all_rule_block(self: "SnakeMakeBackend") -> None:
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

    def compile(self: "SnakeMakeBackend", output_dir: Path):
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
