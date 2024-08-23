"""Pipeline module.

A module that provides the base Pipeline class
and associated building blocks.
"""

from abc import ABC, abstractmethod
from collections.abc import Generator
from enum import Enum
from pathlib import Path
from uuid import uuid4

# Use a try block for backwards compatibility
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import networkx as nx
from pydantic import BaseModel


class NodeType(Enum):
    """An enumeration of node types.

    The following values are supported:

    * PyFunction: a Python function node
    * InvokeShell: an invoke shell command node
    * Container: a container node
    * Scatter: a scatter node for parallel execution
    * Gather: a gather node for parallel execution

    Examples
    --------
    >>> NodeType.PyFunction
    <NodeType.PyFunction: 'PyFunction'>

    """

    PyFunction = "PyFunction"
    InvokeShell = "InvokeShell"
    Container = "Container"
    Scatter = "Scatter"
    Gather = "Gather"


class PyFunctionConfig(BaseModel):
    """Configuration for a Python function node.

    Attributes
    ----------
    py_object : object
        The Python object associated with this configuration.
    venv : Path
        The path to the virtual environment used by this configuration.

    Examples
    --------
    >>> config = PyFunctionConfig(py_object={}, venv=Path())
    >>> config.py_object
    {}

    """

    py_object: object
    venv: Path


NodeConfigType = PyFunctionConfig | str | float


class Node(ABC):
    """An abstract base class for nodes in the pipeline.

    Attributes
    ----------
    name : str
        The unique name of this node.
    node_type : NodeType
        The type of this node.
    input_paths : list[str]
        A list of paths that are used as inputs to this node.
    output_paths : list[str]
        A list of paths that are produced by this node.
    config : object
        The configuration associated with this node.

    Examples
    --------
    >>> class CustomNode(Node):
    ...     @property
    ...     def name(self) -> str:
    ...         return "CustomNode"
    ...     # ...
    >>> node = CustomNode()
    >>> node.name
    'CustomNode'

    """

    def __init__(
        self, name: str, input_paths: list[str], output_paths: list[str], config: object
    ) -> None:
        """Abstract base class for nodes in the pipeline.

        Attributes
        ----------
        name : str
            The unique name of this node.
        node_type : NodeType
            The type of this node.
        input_paths : list[str]
            A list of paths that are used as inputs to this node.
        output_paths : list[str]
            A list of paths that are produced by this node.
        config : object
            The configuration associated with this node.

        """
        self.name = name
        self.input_paths = input_paths
        self.output_paths = output_paths
        self.config = config
        self.node_type = None


def flatten(container: list | tuple) -> Generator:
    """Flatten a list or tuple."""
    for i in container:
        if isinstance(i, list | tuple):
            yield from flatten(i)
        else:
            yield i


class Pipeline(ABC):
    """Class representing a pipeline."""

    def __init__(self, node_list: "list[Pipeline | Node]") -> None:
        """Class representing a pipeline.

        Attributes
        ----------
        pipeline : nx.DiGraph
            The directed graph representation of this pipeline.
        node_list : list[Pipeline | Node]
            The list of nodes or sub-pipelines in this pipeline.

        Examples
        --------
        >>> pipeline = Pipeline(node_list=[...])

        """
        self.pipeline = nx.DiGraph()
        self.node_list = node_list
        self.resolve()

    def resolve(self) -> None:
        """Resolve the node list into a flat list.

        This method traverses the node list and flattens any nested pipelines or nodes.

        Returns
        -------
        None

        Notes
        -----
        The resolved list is stored in the `resolved_list` attribute.

        """
        self.resolved_list = []
        for item in self.node_list:
            if isinstance(item, Node | PyFunction):
                self.resolved_list.append([item])
            else:
                self.resolved_list.append(item.resolved_list)

    @abstractmethod
    def compile(self) -> Self:
        """Compile this pipeline.

        This method must be implemented by subclasses to define the compilation process.

        Returns
        -------
        Pipeline
            The compiled pipeline.

        Raises
        ------
        NotImplementedError
            If not implemented by a subclass.

        """
        raise NotImplementedError


class Seq(Pipeline):
    """Sequential execution of nodes in the pipeline."""

    def compile(self: "Seq") -> Pipeline:
        """Compile this pipeline.

        Returns
        -------
        Pipeline
            Compiled pipeline.

        """
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
    """Parallel execution of nodes in the pipeline."""

    def __init__(self, node_list: "list[Pipeline | Node]") -> None:
        """Parallel pipeline.

        Attributes
        ----------
        pipeline : nx.DiGraph
            The directed graph representation of this pipeline.
        node_list : list[Pipeline | Node]
            The list of nodes or sub-pipelines in this pipeline.

        Examples
        --------
        >>> pipeline = Parallel([...])

        """
        super().__init__(node_list)
        self.node_list = [Scatter()] + self.node_list + [Gather()]
        self.resolve()

    def compile(self: "Parallel") -> Pipeline:
        """Compile this pipeline.

        Returns
        -------
        Pipeline
            Compiled pipeline.

        """
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


class Scatter(Node):
    """Node that represents a scatter operation for parallel execution."""

    def __init__(
        self,
        config: PyFunctionConfig | None = None,
    ) -> None:
        """Node that represents a scatter operation for parallel execution.

        Attributes
        ----------
        name : str
            The unique name of this node.
        input_paths : list[str]
            A list of paths that are used as inputs to this node.
        output_paths : list[str]
            A list of paths that are produced by this node.
        config : PyFunctionConfig | None
            The configuration associated with this node.

        Examples
        --------
        >>> node = Scatter()
        >>> node.name
        'Scatter'

        """
        self.name = f"Scatter:{uuid4()}"
        super().__init__(self.name, [], [], config)
        self.node_type = NodeType.Scatter
        self.config = PyFunctionConfig(py_object={}, venv=Path())

    def __repr__(self) -> str:
        """Node representation."""
        return "Scatter"


class Gather(Node):
    """Node that represents a gather operation for parallel execution."""

    def __init__(
        self,
        config: PyFunctionConfig | None = None,
    ) -> None:
        """Node that represents a gather operation for parallel execution.

        Attributes
        ----------
        name : str
            The unique name of this node.
        input_paths : list[str]
            A list of paths that are used as inputs to this node.
        output_paths : list[str]
            A list of paths that are produced by this node.
        config : PyFunctionConfig | None
            The configuration associated with this node.

        Examples
        --------
        >>> node = Gather()
        >>> node.name
        'Gather'

        """
        self.name = f"Gather:{uuid4()}"
        super().__init__(self.name, [], [], config)
        if config is None:
            self.config = PyFunctionConfig(py_object={}, venv=Path())

    def __repr__(self) -> str:
        """Node representation."""
        return "Gather"


class PyFunction(Node):
    """Node that represents a Python function."""

    def __init__(
        self,
        name: str,
        input_paths: list[str],
        output_paths: list[str],
        config: PyFunctionConfig | None = None,
    ) -> None:
        """Node that represents a Python function.

        Attributes
        ----------
        name : str
            The unique name of this node.
        input_paths : list[str]
            A list of paths that are used as inputs to this node.
        output_paths : list[str]
            A list of paths that are produced by this node.
        config : PyFunctionConfig | None
            The configuration associated with this node.

        Examples
        --------
        >>> node = PyFunction(name="my_node", input_paths=[], output_paths=[])
        >>> node.name
        'my_node'

        """
        super().__init__(name, input_paths, output_paths, config)
        self.node_type = NodeType.PyFunction
        if config is None:
            self.config = PyFunctionConfig(py_object={}, venv=Path())

    def __repr__(self) -> str:
        """Node representation."""
        return f"{self.name}(PF)"


class InvokeShell(Node):
    """Node that represents an invoke shell command."""

    @property
    def node_type(self) -> NodeType:
        """Node type."""
        return NodeType.InvokeShell


class Container(Node):
    """Node that represents a container."""

    @property
    def node_type(self) -> NodeType:
        """Node type."""
        return NodeType.Container
