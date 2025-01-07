"""Pipeline module.

A module that provides the base Pipeline class
and associated building blocks.
"""

from abc import ABC, abstractmethod
from collections.abc import Generator

# Use a try block for backwards compatibility
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import networkx as nx

from pipecraft.node import Gather, Node, PyFunction, Scatter


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
        self.is_compiled = False
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
        if self.is_compiled:
            return self
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
        self.is_compiled = True
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
        if self.is_compiled:
            return self
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
        self.is_compiled = True
        return self
