"""Pooled CellPainting Generic Pipeline."""

from functools import partial

from pipecraft.pipeline import Parallel, Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.cp_illum_apply.apply_cp import CPApplyIllumInvokeCPModule
from starrynight.modules.cp_illum_apply.apply_cppipe import CPApplyIllumGenCPPipeModule
from starrynight.modules.cp_illum_apply.apply_load_data import (
    CPApplyIllumGenLoadDataModule,
)
from starrynight.modules.cp_illum_calc.calc_cp import CPCalcIllumInvokeCPModule
from starrynight.modules.cp_illum_calc.calc_cppipe import CPCalcIllumGenCPPipeModule
from starrynight.modules.cp_illum_calc.calc_load_data import (
    CPCalcIllumGenLoadDataModule,
)
from starrynight.modules.sbs_illum_calc.calc_cp import SBSCalcIllumInvokeCPModule
from starrynight.modules.sbs_illum_calc.calc_cppipe import SBSCalcIllumGenCPPipeModule
from starrynight.modules.sbs_illum_calc.calc_load_data import (
    SBSCalcIllumGenLoadDataModule,
)
from starrynight.modules.schema import Container
from starrynight.pipelines.common import apply_module_params
from starrynight.schema import DataConfig


def create_pcp_generic_pipeline(
    data: DataConfig,
    experiment: Experiment | None = None,
    updated_spec_dict: dict[str, Container] = {},
) -> tuple[list[StarrynightModule], Pipeline]:
    init_module = partial(apply_module_params, data, experiment, updated_spec_dict)
    module_list = [
        # cp modules
        cp_illum_calc_loaddata := init_module(CPCalcIllumGenLoadDataModule),
        cp_illum_calc_cpipe := init_module(CPCalcIllumGenCPPipeModule),
        cp_illum_calc_cp := init_module(CPCalcIllumInvokeCPModule),
        cp_apply_calc_loaddata := init_module(CPApplyIllumGenLoadDataModule),
        cp_apply_calc_cpipe := init_module(CPApplyIllumGenCPPipeModule),
        cp_apply_calc_cp := init_module(CPApplyIllumInvokeCPModule),
        # sbs related modules
        sbs_illum_calc_loaddata := init_module(SBSCalcIllumGenLoadDataModule),
        sbs_illum_calc_cpipe := init_module(SBSCalcIllumGenCPPipeModule),
        sbs_illum_calc_cp := init_module(SBSCalcIllumInvokeCPModule),
    ]
    return module_list, Parallel(
        [
            Seq(
                [
                    cp_illum_calc_loaddata.pipe,
                    cp_illum_calc_cpipe.pipe,
                    cp_illum_calc_cp.pipe,
                    cp_apply_calc_loaddata.pipe,
                    cp_apply_calc_cpipe.pipe,
                    cp_apply_calc_cp.pipe,
                ]
            ),
            Seq(
                [
                    sbs_illum_calc_loaddata.pipe,
                    sbs_illum_calc_cpipe.pipe,
                    sbs_illum_calc_cp.pipe,
                ]
            ),
        ]
    )
