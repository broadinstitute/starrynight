"""Execute PCP generic pipeline"""

# %%
from pathlib import Path

from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig

from starrynight.experiments.pcp_generic import PCPGeneric, PCPGenericInitConfig
from starrynight.modules import cp_pre_segcheck
from starrynight.modules.analysis.analysis_cp import AnalysisInvokeCPModule
from starrynight.modules.analysis.analysis_cppipe import AnalysisGenCPPipeModule
from starrynight.modules.analysis.analysis_load_data import AnalysisGenLoadDataModule
from starrynight.modules.cp_illum_apply.apply_cp import CPApplyIllumInvokeCPModule
from starrynight.modules.cp_illum_apply.apply_cppipe import CPApplyIllumGenCPPipeModule
from starrynight.modules.cp_illum_apply.apply_load_data import (
    CPApplyIllumGenLoadDataModule,
)
from starrynight.modules.cp_illum_calc.calc_cp import CPCalcIllumInvokeCPModule
from starrynight.modules.cp_illum_calc.calc_cppipe import (
    CPCalcIllumGenCPPipeModule,
)
from starrynight.modules.cp_illum_calc.calc_load_data import (
    CPCalcIllumGenLoadDataModule,
)
from starrynight.modules.cp_pre_segcheck.pre_segcheck_cp import (
    CPPreSegcheckInvokeCPModule,
)
from starrynight.modules.cp_pre_segcheck.pre_segcheck_cppipe import (
    CPPreSegcheckGenCPPipeModule,
)
from starrynight.modules.cp_pre_segcheck.pre_segcheck_load_data import (
    CPPreSegcheckGenLoadDataModule,
)
from starrynight.modules.cp_segcheck.segcheck_cp import (
    CPSegcheckInvokeCPModule,
)
from starrynight.modules.cp_segcheck.segcheck_cppipe import (
    CPSegcheckGenCPPipeModule,
)
from starrynight.modules.cp_segcheck.segcheck_load_data import (
    CPSegcheckGenLoadDataModule,
)
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.modules.sbs_align.algin_cp import SBSAlignInvokeCPModule
from starrynight.modules.sbs_align.algin_cppipe import SBSAlignGenCPPipeModule
from starrynight.modules.sbs_align.algin_load_data import SBSAlignGenLoadDataModule
from starrynight.modules.sbs_illum_apply.apply_cp import SBSApplyIllumInvokeCPModule
from starrynight.modules.sbs_illum_apply.apply_cppipe import (
    SBSApplyIllumGenCPPipeModule,
)
from starrynight.modules.sbs_illum_apply.apply_load_data import (
    SBSApplyIllumGenLoadDataModule,
)
from starrynight.modules.sbs_illum_calc.calc_cp import SBSCalcIllumInvokeCPModule
from starrynight.modules.sbs_illum_calc.calc_cppipe import SBSCalcIllumGenCPPipeModule
from starrynight.modules.sbs_illum_calc.calc_load_data import (
    SBSCalcIllumGenLoadDataModule,
)
from starrynight.modules.sbs_preprocess.preprocess_cp import SBSPreprocessInvokeCPModule
from starrynight.modules.sbs_preprocess.preprocess_cppipe import (
    SBSPreprocessGenCPPipeModule,
)
from starrynight.modules.sbs_preprocess.preprocess_load_data import (
    SBSPreprocessGenLoadDataModule,
)
from starrynight.schema import DataConfig

# %% [markdown]
# Setup dataset paths

# %%
dataset_path = Path("../../scratch/starrynight_example_input")
workspace_path = Path("../../scratch/starrynight_example_output")
exec_runs = Path("../../scratch/starrynight_runs")
exec_mounts = Path("../../scratch/starrynight_mounts")


# %% [markdown]
# Create data config

# %%
data_config = DataConfig(
    dataset_path=dataset_path,
    storage_path=dataset_path,
    workspace_path=workspace_path,
)

# %% [markdown]
# Create execution engine config config

# %%
backend_config = SnakeMakeConfig(use_fluent_bit=False, print_exec=True)


# %% [markdown]
# Configure the generate inventory module
# This module is special and doesn't require an experiment for configuration

# %%
gen_inv_mod = GenInvModule.from_config(data_config)
exec_backend = SnakeMakeBackend(
    gen_inv_mod.pipe, backend_config, exec_runs / "run001", exec_mounts
)
run = exec_backend.run()

# %% [markdown]
# Configure the generate index module
# This module is special and doesn't require an experiment for configuration

# %%
gen_ind_mod = GenIndexModule.from_config(data_config)
exec_backend = SnakeMakeBackend(
    gen_ind_mod.pipe, backend_config, exec_runs / "run002", exec_mounts
)
run = exec_backend.run()

# %% [markdown]
# Configure the experiment with the generated index

# %%
index_path = workspace_path / "index/index.parquet"
pcp_exp_init = PCPGenericInitConfig(
    barcode_csv_path="",
    cp_acquisition_order="snake",
    cp_img_frame_type="round",
    cp_img_overlap_pct="10",
    sbs_acquisition_order="snake",
    sbs_img_frame_type="round",
    sbs_img_overlap_pct="10",
    cp_nuclei_channel="DAPI",
    cp_cell_channel="PhalloAF750",
    cp_mito_channel="ZO1AF488",
    sbs_nuclei_channel="DAPI",
    sbs_cell_channel="PhalloAF750",
    sbs_mito_channel="ZO1AF488",
)
pcp_experiment = PCPGeneric.from_index(index_path, pcp_exp_init)


# %% [markdown]
# Configure the following modules with the experiment

# ------------------------------------------------------------------

# %% [markdown]
# Step 1: CP calculate illum correction

# %%
# Gen load data
cp_calc_illum_load_data_mod = CPCalcIllumGenLoadDataModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_calc_illum_load_data_mod.pipe, backend_config, exec_runs / "run003", exec_mounts
)
run = exec_backend.run()

# Gen cppipe file
cp_calc_illum_cppipe_mod = CPCalcIllumGenCPPipeModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_calc_illum_cppipe_mod.pipe, backend_config, exec_runs / "run004", exec_mounts
)
run = exec_backend.run()

# Invoke cppipe file
cp_calc_illum_invoke_mod = CPCalcIllumInvokeCPModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_calc_illum_invoke_mod.pipe, backend_config, exec_runs / "run005", exec_mounts
)
run = exec_backend.run()

# ------------------------------------------------------------------

# %% [markdown]
# Step 2: CP apply illum correction

# %%
# Gen load data
cp_apply_illum_load_data_mod = CPApplyIllumGenLoadDataModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_apply_illum_load_data_mod.pipe, backend_config, exec_runs / "run006", exec_mounts
)
run = exec_backend.run()

# Gen cppipe file
cp_apply_illum_cppipe_mod = CPApplyIllumGenCPPipeModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_apply_illum_cppipe_mod.pipe, backend_config, exec_runs / "run007", exec_mounts
)
run = exec_backend.run()

# Invoke cppipe file
cp_apply_illum_invoke_mod = CPApplyIllumInvokeCPModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_apply_illum_invoke_mod.pipe, backend_config, exec_runs / "run008", exec_mounts
)
run = exec_backend.run()

# ------------------------------------------------------------------

# %% [markdown]
# Step 3: CP segcheck

# %%
# Gen load data
cp_segcheck_load_data_mod = CPSegcheckGenLoadDataModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_segcheck_load_data_mod.pipe, backend_config, exec_runs / "run009", exec_mounts
)
run = exec_backend.run()

# Gen cppipe file
cp_segcheck_cppipe_mod = CPSegcheckGenCPPipeModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_segcheck_cppipe_mod.pipe, backend_config, exec_runs / "run010", exec_mounts
)
run = exec_backend.run()

# Invoke cppipe file
cp_segcheck_invoke_mod = CPSegcheckInvokeCPModule.from_config(
    data_config, pcp_experiment
)

exec_backend = SnakeMakeBackend(
    cp_segcheck_invoke_mod.pipe, backend_config, exec_runs / "run011", exec_mounts
)
run = exec_backend.run()
