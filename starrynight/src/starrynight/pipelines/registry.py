"""Starrynight pipelines registry."""

from collections.abc import Callable

from pipecraft.pipeline import Pipeline

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.schema import SpecContainer
from starrynight.pipelines.index import create_index_pipeline
from starrynight.pipelines.pcp_generic import create_pcp_generic_pipeline
from starrynight.schema import DataConfig

PIPELINE_REGISTRY: dict[
    str,
    Callable[
        [DataConfig, Experiment | None, dict[str, SpecContainer]],
        tuple[list[StarrynightModule], Pipeline],
    ],
] = {
    "Indexing": create_index_pipeline,
    "Pooled CellPainting [Generic]": create_pcp_generic_pipeline,
}
