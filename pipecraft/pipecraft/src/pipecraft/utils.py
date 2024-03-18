"""
Pipecraft utilities.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx


def save_pipeline_plot(pipeline: nx.DiGraph, file_path: Path) -> None:
    fig, axs = plt.subplots()
    nx.draw_networkx(pipeline, ax=axs, pos=nx.spring_layout(pipeline), with_labels=True)
    fig.savefig(file_path)
