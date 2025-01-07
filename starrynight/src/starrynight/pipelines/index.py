"""Indexing Pipeline."""

from functools import partial

from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.modules.schema import Container as SpecContainer
from starrynight.pipelines.common import apply_module_params
from starrynight.schema import DataConfig


def create_index_pipeline(
    experiment: Experiment,
    data: DataConfig,
    updated_spec_dict: dict[str, SpecContainer] = {},
) -> Pipeline:
    """Generate indexing pipeline."""
    init_module = partial(apply_module_params, experiment, data, updated_spec_dict)
    return Seq([init_module(GenInvModule).pipe, init_module(GenIndexModule).pipe])
