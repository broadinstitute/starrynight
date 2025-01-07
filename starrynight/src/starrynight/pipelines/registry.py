"""Starrynight pipelines registry."""

from collections.abc import Callable

from starrynight.experiments.common import Experiment
from starrynight.modules.schema import Container
from starrynight.pipelines.index import create_index_pipeline
from starrynight.pipelines.pcp_generic import create_pcp_generic_pipeline
from starrynight.schema import DataConfig

PIPELINE_REGISTRY: dict[
    str, Callable[[Experiment, DataConfig, dict[str, Container] | None]]
] = {
    "Indexing": create_index_pipeline,
    "Pooled CellPainting [Generic]": create_pcp_generic_pipeline,
}
