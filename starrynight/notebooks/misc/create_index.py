"""Create index for a project."""

from pathlib import Path

from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig

from starrynight.experiments.pcp_generic import PCPGeneric, PCPGenericInitConfig
from starrynight.modules.gen_inv import GenInvModule
from starrynight.pipelines.index import create_index_pipeline
from starrynight.pipelines.pcp_generic import create_pcp_generic_pipeline
from starrynight.schema import DataConfig

# Setup experiment
data = DataConfig(
    dataset_path=Path("/datastore/cpg0999-merck-asma"),
    storage_path=Path("/datastore/cpg0999-merck-asma"),
    workspace_path=Path("./run001/workspace"),
)

pcp_exp = PCPGeneric.from_index(
    data.storage_path.joinpath("index/index.parquet"),
    PCPGenericInitConfig(
        barcode_csv_path=data.storage_path.joinpath("barcode.csv")
    ).model_dump(),
)

# Create the pipeline
# modules, simple_pipeline = create_index_pipeline(data)
modules, simple_pipeline = create_pcp_generic_pipeline(data, experiment=pcp_exp)


# Configure execution backend
config = SnakeMakeConfig()
exec_backend01 = SnakeMakeBackend(
    simple_pipeline, config, data.storage_path, data.workspace_path
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
gen_inv_module = GenInvModule.from_config(data)

# Inspect current specification and make changes
print(gen_inv_module.spec)
gen_inv_module.spec.inputs[0].path = Path("path/to/my/parser.lark").resolve().__str__()

# Add the configured module back to pipeline
configured_modules, configure_pipeline = create_index_pipeline(
    data, updated_spec_dict={GenInvModule.uid(): gen_inv_module.spec}
)

# --------------------------------------------------------------------
# Experiment configuration.
# --------------------------------------------------------------------
