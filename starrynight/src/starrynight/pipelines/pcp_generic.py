"""Pooled CellPainting Generic Pipeline."""

from functools import partial

from pipecraft.pipeline import Parallel, Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.illum_calc.calc_cp import CalcIllumInvokeCPModule
from starrynight.modules.illum_calc.calc_cppipe import CalcIllumGenCPPipeModule
from starrynight.modules.illum_calc.calc_load_data import CalcIllumGenLoadDataModule
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
        illum_calc_loaddata := init_module(CalcIllumGenLoadDataModule),
        illum_calc_cpipe := init_module(CalcIllumGenCPPipeModule),
        illum_calc_cp := init_module(CalcIllumInvokeCPModule),
        # sbs related modules
        sbs_illum_calc_loaddata := init_module(SBSCalcIllumGenLoadDataModule),
        sbs_illum_calc_cpipe := init_module(SBSCalcIllumGenCPPipeModule),
        sbs_illum_calc_cp := init_module(SBSCalcIllumInvokeCPModule),
    ]
    return module_list, Parallel(
        [
            Seq([illum_calc_loaddata.pipe, illum_calc_cpipe.pipe, illum_calc_cp.pipe]),
            Seq(
                [
                    sbs_illum_calc_loaddata.pipe,
                    sbs_illum_calc_cpipe.pipe,
                    sbs_illum_calc_cp.pipe,
                ]
            ),
        ]
    )
