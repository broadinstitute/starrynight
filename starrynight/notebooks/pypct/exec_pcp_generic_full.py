# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Execute PCP generic pipeline

# %%
from pathlib import Path

from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig

from starrynight.experiments.common import AcquisitionOrderType, ImageFrameType
from starrynight.experiments.pcp_generic import PCPGeneric, PCPGenericInitConfig
from starrynight.modules.analysis.analysis_cp import AnalysisInvokeCPModule
from starrynight.modules.analysis.analysis_cppipe import AnalysisGenCPPipeModule

# inventory and index
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.pipelines.index import create_index_pipeline
from starrynight.pipelines.pcp_generic import create_pcp_generic_pipeline
from starrynight.schema import DataConfig

# %% [markdown]
# ## Setup dataset paths

# %%
dataset_path = Path("../../../scratch/starrynight_example_input")
workspace_path = Path("../../../scratch/starrynight_example_output")
exec_runs = Path("../../../scratch/starrynight_runs_full")
exec_mounts = Path("../../../scratch/starrynight_mounts")


# %% [markdown]
# ## Create data config

# %%
data_config = DataConfig(
    dataset_path=dataset_path,
    storage_path=dataset_path,
    workspace_path=workspace_path,
)

# %% [markdown]
# ## Create execution engine config config

# %%
backend_config = SnakeMakeConfig(
    use_fluent_bit=False, print_exec=True, background=False
)


# %% [markdown]
# ## Configure and execute the indexing pipeline

# %%
# Create index pipeline
index_modules, index_pipeline = create_index_pipeline(data_config)

# %%
exec_backend = SnakeMakeBackend(
    index_pipeline, backend_config, exec_runs / "run001", exec_mounts
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ## Configure the experiment with the generated index

# %%
index_path = workspace_path / "index/index.parquet"
pcp_exp_init = PCPGenericInitConfig(
    barcode_csv_path=dataset_path / "workspace/metadata/barcode.csv",
    cp_acquisition_order=AcquisitionOrderType.SNAKE,
    cp_img_frame_type=ImageFrameType.ROUND,
    cp_img_overlap_pct=10,
    sbs_acquisition_order=AcquisitionOrderType.SNAKE,
    sbs_img_frame_type=ImageFrameType.ROUND,
    sbs_img_overlap_pct=10,
    cp_nuclei_channel="DAPI",
    cp_cell_channel="PhalloAF750",
    cp_mito_channel="ZO1AF488",
    sbs_nuclei_channel="DAPI",
    sbs_cell_channel="PhalloAF750",
    sbs_mito_channel="ZO1AF488",
)
pcp_experiment = PCPGeneric.from_index(index_path, pcp_exp_init.model_dump())


# %% [markdown]
# ## Configure the following modules with the experiment
#
# ------------------------------------------------------------------

# %% [markdown]
# ## Create and exec pipeline

# %%
# Create pipeline
modules, pcp_generic_pipeline = create_pcp_generic_pipeline(
    data_config, pcp_experiment
)


# %%
modules

# %%
pcp_generic_pipeline.compile()
pcp_generic_pipeline.pipeline.nodes

# %%
# Exec pipeline
exec_backend = SnakeMakeBackend(
    pcp_generic_pipeline,
    backend_config,
    exec_runs / "run003",
    exec_mounts,
)
exec_backend.compile()

# %%
run = exec_backend.run()

# %%
