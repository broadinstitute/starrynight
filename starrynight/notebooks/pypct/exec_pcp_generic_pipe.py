# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Execute PCP generic pipeline step by step

# %% [markdown]
# ## Imports

# %%
from pathlib import Path

from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig

from starrynight.experiments.common import AcquisitionOrderType, ImageFrameType
from starrynight.experiments.pcp_generic import PCPGeneric, PCPGenericInitConfig
from starrynight.modules.analysis.analysis_cp import AnalysisInvokeCPModule
from starrynight.modules.analysis.analysis_cppipe import AnalysisGenCPPipeModule
from starrynight.modules.analysis.analysis_load_data import (
    AnalysisGenLoadDataModule,
)
from starrynight.modules.cp_illum_apply.apply_cp import (
    CPApplyIllumInvokeCPModule,
)
from starrynight.modules.cp_illum_apply.apply_cppipe import (
    CPApplyIllumGenCPPipeModule,
)
from starrynight.modules.cp_illum_apply.apply_load_data import (
    CPApplyIllumGenLoadDataModule,
)

# cp_illum_calc
from starrynight.modules.cp_illum_calc.calc_cp import CPCalcIllumInvokeCPModule
from starrynight.modules.cp_illum_calc.calc_cppipe import (
    CPCalcIllumGenCPPipeModule,
)
from starrynight.modules.cp_illum_calc.calc_load_data import (
    CPCalcIllumGenLoadDataModule,
)

# cp_segcheck
from starrynight.modules.cp_segcheck.segcheck_cp import CPSegcheckInvokeCPModule
from starrynight.modules.cp_segcheck.segcheck_cppipe import (
    CPSegcheckGenCPPipeModule,
)
from starrynight.modules.cp_segcheck.segcheck_load_data import (
    CPSegcheckGenLoadDataModule,
)

# inventory and index
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.modules.sbs_illum_apply.apply_cp import (
    SBSApplyIllumInvokeCPModule,
)
from starrynight.modules.sbs_illum_apply.apply_cppipe import (
    SBSApplyIllumGenCPPipeModule,
)
from starrynight.modules.sbs_illum_apply.apply_load_data import (
    SBSApplyIllumGenLoadDataModule,
)
from starrynight.modules.sbs_illum_calc.calc_cp import (
    SBSCalcIllumInvokeCPModule,
)
from starrynight.modules.sbs_illum_calc.calc_cppipe import (
    SBSCalcIllumGenCPPipeModule,
)
from starrynight.modules.sbs_illum_calc.calc_load_data import (
    SBSCalcIllumGenLoadDataModule,
)
from starrynight.modules.sbs_preprocess.preprocess_cp import (
    SBSPreprocessInvokeCPModule,
)  # noqa: E501
from starrynight.modules.sbs_preprocess.preprocess_cppipe import (
    SBSPreprocessGenCPPipeModule,
)
from starrynight.modules.sbs_preprocess.preprocess_load_data import (
    SBSPreprocessGenLoadDataModule,
)
from starrynight.schema import DataConfig

# %% [markdown]
# ## Setup dataset paths
# These paths are required for creating the `DataConfig` object and configure the execution backend.

# %%
dataset_path = Path("../../../scratch/starrynight_example_input")
barcode_csv_path = dataset_path.joinpath("workspace/metadata/barcode.csv")
workspace_path = Path("../../../scratch/new_starrynight_example_output")
exec_runs = Path("../../../scratch/new_starrynight_runs")
exec_mounts = Path("../../../scratch/new_starrynight_mounts")


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
# Here we are creating a `SnakeMakeBackend` config.
# We can also use other backends like `NextflowBackend` and `AWSBatchBackend`

# %%
backend_config = SnakeMakeConfig(
    use_fluent_bit=False, print_exec=True, background=False
)


# %% [markdown]
# ## Configure the generate inventory module
# This module is special and doesn't require an experiment for configuration

# %%
gen_inv_mod = GenInvModule(data_config)
exec_backend = SnakeMakeBackend(
    gen_inv_mod.pipe, backend_config, exec_runs / "run001", exec_mounts
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ## Configure the generate index module
# This module is special and doesn't require an experiment for configuration

# %%
gen_ind_mod = GenIndexModule(data_config)
exec_backend = SnakeMakeBackend(
    gen_ind_mod.pipe, backend_config, exec_runs / "run002", exec_mounts
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ## Configure the experiment with the generated index

# %%
index_path = workspace_path / "index/index.parquet"
pcp_exp_init = PCPGenericInitConfig(
    barcode_csv_path=barcode_csv_path.resolve(),
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


# %%
# Write out the experiment as a json file
experiment_dir = data_config.workspace_path.joinpath("experiment")
experiment_dir.mkdir(parents=True, exist_ok=True)
experiment_dir.joinpath("experiment.json").write_text(
    pcp_experiment.model_dump_json()
)

# %% [markdown]
# ## Configure the following modules with the experiment
#
# ------------------------------------------------------------------

# %% [markdown]
# ## Step 1: CP calculate illum correction

# %% [markdown]
# ### Gen load data

# %%
cp_calc_illum_load_data_mod = CPCalcIllumGenLoadDataModule(
    data_config, pcp_experiment
)
# Change default value to use legacy pipeline compatible load data
cp_calc_illum_load_data_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    cp_calc_illum_load_data_mod.pipe,
    backend_config,
    exec_runs / "run003",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Gen cppipe file

# %%
cp_calc_illum_cppipe_mod = CPCalcIllumGenCPPipeModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
cp_calc_illum_cppipe_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    cp_calc_illum_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run004",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Invoke cppipe file

# %%
cp_calc_illum_invoke_mod = CPCalcIllumInvokeCPModule(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_calc_illum_invoke_mod.pipe,
    backend_config,
    exec_runs / "run005",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# ------------------------------------------------------------------

# %% [markdown]
# ## Step 2: CP apply illum correction

# %% [markdown]
# ### Gen load data

# %%
cp_apply_illum_load_data_mod = CPApplyIllumGenLoadDataModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
cp_apply_illum_load_data_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    cp_apply_illum_load_data_mod.pipe,
    backend_config,
    exec_runs / "run006",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Gen cppipe file

# %%
cp_apply_illum_cppipe_mod = CPApplyIllumGenCPPipeModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
cp_apply_illum_cppipe_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    cp_apply_illum_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run007",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Invoke cppipe file

# %%
cp_apply_illum_invoke_mod = CPApplyIllumInvokeCPModule(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_apply_illum_invoke_mod.pipe,
    backend_config,
    exec_runs / "run008",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# ------------------------------------------------------------------

# %% [markdown]
# ## Step 3: CP segcheck

# %% [markdown]
# ### Gen load data

# %%
cp_segcheck_load_data_mod = CPSegcheckGenLoadDataModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
cp_segcheck_load_data_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    cp_segcheck_load_data_mod.pipe,
    backend_config,
    exec_runs / "run009",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Gen cppipe file

# %%
cp_segcheck_cppipe_mod = CPSegcheckGenCPPipeModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
cp_segcheck_cppipe_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    cp_segcheck_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run010",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Invoke cppipe file

# %%
cp_segcheck_invoke_mod = CPSegcheckInvokeCPModule(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_segcheck_invoke_mod.pipe,
    backend_config,
    exec_runs / "run011",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# ------------------------------------------------------------------

# %% [markdown]
# ## Step 5: SBS calculate illum correction

# %% [markdown]
# ### Gen load data

# %%
sbs_calc_illum_load_data_mod = SBSCalcIllumGenLoadDataModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
sbs_calc_illum_load_data_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    sbs_calc_illum_load_data_mod.pipe,
    backend_config,
    exec_runs / "run012",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Gen cppipe file

# %%
sbs_calc_illum_cppipe_mod = SBSCalcIllumGenCPPipeModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
sbs_calc_illum_cppipe_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    sbs_calc_illum_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run013",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Invoke cppipe file

# %%
sbs_calc_illum_invoke_mod = SBSCalcIllumInvokeCPModule(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    sbs_calc_illum_invoke_mod.pipe,
    backend_config,
    exec_runs / "run014",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# ------------------------------------------------------------------

# %% [markdown]
# ## Step 6: SBS apply illum correction

# %% [markdown]
# ### Gen load data

# %%
sbs_apply_illum_load_data_mod = SBSApplyIllumGenLoadDataModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
sbs_apply_illum_load_data_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    sbs_apply_illum_load_data_mod.pipe,
    backend_config,
    exec_runs / "run015",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown] jp-MarkdownHeadingCollapsed=true
# ### Gen cppipe file

# %%
sbs_apply_illum_cppipe_mod = SBSApplyIllumGenCPPipeModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
sbs_apply_illum_cppipe_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    sbs_apply_illum_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run016",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Invoke cppipe file

# %%
sbs_apply_illum_invoke_mod = SBSApplyIllumInvokeCPModule(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    sbs_apply_illum_invoke_mod.pipe,
    backend_config,
    exec_runs / "run017",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# ------------------------------------------------------------------

# %% [markdown]
# ## Step 7: SBS preprocess

# %% [markdown]
# ### Gen load data

# %%
sbs_preprocess_load_data_mod = SBSPreprocessGenLoadDataModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
sbs_preprocess_load_data_mod.spec.inputs["use_legacy"].value = True
#Fix align path for legacy module
sbs_preprocess_load_data_mod.spec.inputs["aligned_images_path"].value = sbs_preprocess_load_data_mod.spec.inputs["corrected_images_path"].value
exec_backend = SnakeMakeBackend(
    sbs_preprocess_load_data_mod.pipe,
    backend_config,
    exec_runs / "run018",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Gen cppipe file

# %%
sbs_preprocess_cppipe_mod = SBSPreprocessGenCPPipeModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
sbs_preprocess_cppipe_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    sbs_preprocess_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run019",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Invoke cppipe file

# %%
sbs_preprocess_invoke_mod = SBSPreprocessInvokeCPModule(
    data_config, pcp_experiment
)
# Add the CP plugin directory
sbs_preprocess_invoke_mod.spec.inputs["plugin_path"] = "/home/ank/workspace/hub/broad/starrynight/scratch/CellProfiler-plugins/active_plugins/"

exec_backend = SnakeMakeBackend(
    sbs_preprocess_invoke_mod.pipe,
    backend_config,
    exec_runs / "run020",
    exec_mounts,
)
run = exec_backend.run()
run.wait()
# ------------------------------------------------------------------

# %% [markdown]
# ## Step 9: Analysis

# %% [markdown]
# ### Gen load data

# %%
analysis_load_data_mod = AnalysisGenLoadDataModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
analysis_load_data_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    analysis_load_data_mod.pipe,
    backend_config,
    exec_runs / "run021",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Gen cppipe file

# %%
analysis_cppipe_mod = AnalysisGenCPPipeModule(
    data_config, pcp_experiment
)

# Change default value to use legacy pipeline compatible load data
analysis_cppipe_mod.spec.inputs["use_legacy"].value = True

exec_backend = SnakeMakeBackend(
    analysis_cppipe_mod.pipe,
    backend_config,
    exec_runs / "run022",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %% [markdown]
# ### Invoke cppipe file

# %%
analysis_invoke_mod = AnalysisInvokeCPModule(
    data_config, pcp_experiment
)

# Add the CP plugin directory
analysis_invoke_mod.spec.inputs["plugin_path"] = "/home/ank/workspace/hub/broad/starrynight/scratch/CellProfiler-plugins/active_plugins/"

exec_backend = SnakeMakeBackend(
    analysis_invoke_mod.pipe,
    backend_config,
    exec_runs / "run023",
    exec_mounts,
)
run = exec_backend.run()
run.wait()

# %%
