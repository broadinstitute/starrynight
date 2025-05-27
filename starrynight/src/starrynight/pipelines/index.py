"""Indexing Pipeline."""

from functools import partial

from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.modules.schema import SpecContainer
from starrynight.pipelines.common import apply_module_params
from starrynight.schema import DataConfig


def create_index_pipeline(
    data: DataConfig,
    experiment: Experiment | None = None,
    updated_spec_dict: dict[str, SpecContainer] = {},
) -> tuple[list[StarrynightModule], Pipeline]:
    """Generate indexing pipeline."""
    init_module = partial(
        apply_module_params, data, experiment, updated_spec_dict
    )
    module_list = [
        gen_inv := init_module(GenInvModule),
        gen_index := init_module(GenIndexModule),
    ]
    return module_list, Seq([gen_inv.pipe, gen_index.pipe])
