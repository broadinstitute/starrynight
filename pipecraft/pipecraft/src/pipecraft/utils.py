"""Pipecraft utilities."""

from pathlib import Path

from cloudpathlib import CloudPath
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.figure import Figure


def save_pipeline_plot(
    pipeline: nx.DiGraph, file_path: Path | CloudPath | None
) -> Figure:
    """Create a plot of the pipeline."""
    plt.style.use("dark_background")
    fig, axs = plt.subplots()
    nx.draw_networkx(
        pipeline,
        ax=axs,
        pos=nx.spring_layout(pipeline),
        with_labels=False,
        node_color="#49a078",
        edge_color="#ffffff",
    )
    axs.axis("off")
    if file_path:
        fig.savefig(file_path)
    return fig
