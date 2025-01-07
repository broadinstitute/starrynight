"""Pooled CellPainting Generic Pipeline."""

from pipecraft.pipeline import Parallel, Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.schema import Container
from starrynight.schema import DataConfig


def create_pcp_generic_pipeline(
    experiment: Experiment,
    data: DataConfig,
    updated_spec_dict: dict[str, Container] = {},
) -> Pipeline:
    return Parallel([Seq([]), Seq([])])
