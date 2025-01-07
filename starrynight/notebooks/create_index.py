"""Create index for a project."""

from pathlib import Path

from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig

from starrynight.experiments.common import DummyExperiment
from starrynight.modules.gen_inv import GenInvModule
from starrynight.pipelines.index import create_index_pipeline
from starrynight.schema import DataConfig

# Setup experiment
data = DataConfig(
    dataset_path=Path("/datastore/cpg0999-merck-asma"),
    storage_path=Path("./run001/workspace"),
    workspace_path=Path("./run001/workspace"),
)
experiment = DummyExperiment(dataset_id="cpg0999-merck-asma")

# Create the pipeline
pipeline = create_index_pipeline(experiment, data)


# Configure execution backend
config = SnakeMakeConfig()
exec_backend = SnakeMakeBackend(
    pipeline, config, data.storage_path, data.workspace_path
)

# Compile to get the generated snakemake file if
# manual execution or inspection is required.
# exec_backend.compile()

# or execute directly
# exec_backend.run()

# -------------------------------------------------------------------
# Changing default module specs
# -------------------------------------------------------------------

# Iniialize module with experiment and data
gen_inv_module = GenInvModule.from_config(experiment, data)

# Inspect current specification and make changes
print(gen_inv_module.spec)
gen_inv_module.spec.inputs[0].path = Path("path/to/my/parser.lark").resolve().__str__()

# Add the configured module back to pipeline
pipeline = create_index_pipeline(
    experiment, data, {GenInvModule.uid(): gen_inv_module.spec}
)
