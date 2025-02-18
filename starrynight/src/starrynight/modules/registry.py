"""Starrynight module registry."""

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
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.modules.sbs_illum_calc.calc_cp import SBSCalcIllumInvokeCPModule
from starrynight.modules.sbs_illum_calc.calc_cppipe import SBSCalcIllumGenCPPipeModule
from starrynight.modules.sbs_illum_calc.calc_load_data import (
    SBSCalcIllumGenLoadDataModule,
)

MODULE_REGISTRY: dict[str, StarrynightModule] = {
    GenInvModule.uid(): GenInvModule,
    GenIndexModule.uid(): GenIndexModule,
    CPCalcIllumGenLoadDataModule.uid(): CPCalcIllumGenLoadDataModule,
    CPCalcIllumGenCPPipeModule.uid(): CPCalcIllumGenCPPipeModule,
    CPCalcIllumInvokeCPModule.uid(): CPCalcIllumInvokeCPModule,
    CPApplyIllumGenLoadDataModule.uid(): CPApplyIllumGenLoadDataModule,
    CPApplyIllumGenCPPipeModule.uid(): CPApplyIllumGenCPPipeModule,
    CPApplyIllumInvokeCPModule.uid(): CPApplyIllumInvokeCPModule,
    SBSCalcIllumGenLoadDataModule.uid(): SBSCalcIllumGenLoadDataModule,
    SBSCalcIllumGenCPPipeModule.uid(): SBSCalcIllumGenCPPipeModule,
    SBSCalcIllumInvokeCPModule.uid(): SBSCalcIllumInvokeCPModule,
}
