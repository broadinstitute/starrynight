"""
Pipecraft utilities.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx


def save_pipeline_plot(pipeline: nx.DiGraph, file_path: Path) -> None:
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
    fig.savefig(file_path)
