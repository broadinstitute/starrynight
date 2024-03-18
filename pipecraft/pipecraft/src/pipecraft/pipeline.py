"""Pipeline module

A module that provides the base Pipeline class
and associated building blocks.
"""

from abc import ABC, abstractmethod, abstractproperty
from uuid import uuid4
from typing import Union, Generic, TypeVar
from enum import Enum
from pathlib import Path

from pydantic import BaseModel
import networkx as nx


def flatten(container):
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i


class NodeType(Enum):
    PyFunction = "PyFunction"
    InvokeShell = "InvokeShell"
    Container = "Container"
    Scatter = "Scatter"
    Gather = "Gather"


class PyFunctionConfig(BaseModel):
    py_object: object
    venv: Path


NodeConfigType = Union[PyFunctionConfig, str, float]
N = TypeVar("N")
NConfig = TypeVar("NConfig")


class Node(Generic[N, NConfig], ABC):
    @abstractproperty
    def name(self: N) -> str:
        raise NotImplementedError

    @abstractproperty
    def node_type(self: N) -> NodeType:
        raise NotImplementedError

    @abstractproperty
    def input_paths(self: N) -> list[str]:
        raise NotImplementedError

    @abstractproperty
    def output_paths(self: N) -> list[str]:
        raise NotImplementedError

    @abstractproperty
    def config(self) -> NConfig:
        raise NotImplementedError


class Pipeline:
    def __init__(self, node_list: "list[Pipeline | Node]") -> None:
        self.pipeline = nx.DiGraph()
        self.node_list = node_list
        self.resolve()

    def resolve(self: "Pipeline") -> None:
        self.resolved_list = []
        for item in self.node_list:
            if isinstance(item, Node | PyFunction):
                self.resolved_list.append([item])
            else:
                self.resolved_list.append(item.resolved_list)

    @abstractmethod
    def compile(self: "Pipeline") -> "Pipeline":
        raise NotImplementedError


class Seq(Pipeline):
    def compile(self: "Seq") -> Pipeline:
        # for i in range(max(0, len(self.node_list) - 1)):
        prev_root = None
        for i, item in enumerate(self.node_list):
            current_root: list[Node] = list(flatten([self.resolved_list[i]]))
            if isinstance(item, Node):
                if isinstance(prev_root, Node):
                    self.pipeline.add_edge(prev_root, item)
                elif isinstance(prev_root, list):
                    self.pipeline.add_edge(prev_root[-1], item)
                elif prev_root is None:
                    self.pipeline.add_node(item)
                prev_root = current_root
            else:
                subgraph = item.compile().pipeline
                self.pipeline = nx.union(self.pipeline, subgraph)
                subgraph_flattened = list(flatten([self.resolved_list[i]]))
                if isinstance(prev_root, Node):
                    self.pipeline.add_edge(prev_root, subgraph_flattened[0])
                elif isinstance(prev_root, list):
                    self.pipeline.add_edge(prev_root[-1], subgraph_flattened[0])
                prev_root = subgraph_flattened[-1]
        return self


class Parallel(Pipeline):
    def __init__(self, node_list: "list[Pipeline | Node]") -> None:
        super().__init__(node_list)
        self.node_list = [Scatter()] + self.node_list + [Gather()]
        self.resolve()

    def compile(self: "Parallel") -> Pipeline:
        flattened_list: list[Node] = list(flatten([self.resolved_list]))
        scatter_node = flattened_list[0]
        gather_node = flattened_list[-1]
        for i, item in enumerate(self.node_list):
            if isinstance(item, Node):
                if scatter_node != item and gather_node != item:
                    self.pipeline.add_edge(scatter_node, item)
                    self.pipeline.add_edge(item, gather_node)
            else:
                subgraph = item.compile().pipeline
                self.pipeline = nx.union(self.pipeline, subgraph)
                subgraph_flattened = list(flatten([self.resolved_list[i]]))
                self.pipeline.add_edge(scatter_node, subgraph_flattened[0])
                self.pipeline.add_edge(subgraph_flattened[-1], gather_node)
        return self


class Scatter(Node["Scatter", PyFunctionConfig]):
    def __init__(self) -> None:
        self._name = f"Scatter:{uuid4()}"

    @property
    def name(self: "Scatter") -> str:
        return self._name

    @property
    def node_type(self: "Scatter") -> NodeType:
        return NodeType.Scatter

    @property
    def input_paths(self: "Scatter") -> list[str]:
        return []

    @property
    def output_paths(self: "Scatter") -> list[str]:
        return []

    @property
    def config(self: "Scatter") -> PyFunctionConfig:
        return PyFunctionConfig(py_object={}, venv=Path())

    def __repr__(self: "Scatter") -> str:
        return "Scatter"


class Gather(Node["Gather", PyFunctionConfig]):
    def __init__(self) -> None:
        self._name = f"Gather:{uuid4()}"

    @property
    def name(self: "Gather") -> str:
        return self._name

    @property
    def node_type(self: "Gather") -> NodeType:
        return NodeType.Gather

    @property
    def input_paths(self: "Gather") -> list[str]:
        return []

    @property
    def output_paths(self: "Gather") -> list[str]:
        return []

    @property
    def config(self: "Gather") -> PyFunctionConfig:
        return PyFunctionConfig(py_object={}, venv=Path())

    def __repr__(self: "Gather") -> str:
        return "Gather"


class PyFunction(Node["PyFunction", PyFunctionConfig]):
    def __init__(
        self, name: str, input_paths: list[str], output_paths: list[str]
    ) -> None:
        self._name = name
        self._input_paths = input_paths
        self._output_paths = output_paths

    @property
    def name(self) -> str:
        return self._name

    @property
    def input_paths(self) -> list[str]:
        return self._input_paths

    @property
    def output_paths(self) -> list[str]:
        return self._output_paths

    @property
    def node_type(self: "PyFunction") -> NodeType:
        return NodeType.PyFunction

    @property
    def config(self) -> PyFunctionConfig:
        return PyFunctionConfig(py_object={}, venv=Path())

    def __repr__(self) -> str:
        return f"{self.name}(PF)"


class InvokeShell(Node):
    @property
    def node_type(self: "InvokeShell") -> NodeType:
        return NodeType.InvokeShell


class Container(Node):
    @property
    def node_type(self: "Container") -> NodeType:
        return NodeType.Container
