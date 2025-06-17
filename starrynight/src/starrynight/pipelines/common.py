"""Common pipeline tools."""

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.schema import SpecContainer
from starrynight.schema import DataConfig


def apply_module_params(
    data: DataConfig,
    experiment: Experiment | None = None,
    updated_spec_dict: dict[str, SpecContainer] = {},
    module: StarrynightModule = None,
) -> StarrynightModule:
    """Apply modules params helper."""
    updated_spec = updated_spec_dict.get(module.module_name(), None)
    if updated_spec is not None:
        updated_spec = SpecContainer(**updated_spec)
    return module(data, experiment, updated_spec)
