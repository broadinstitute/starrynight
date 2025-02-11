"""Starrynight module registry."""

from starrynight.modules.common import StarrynightModule
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.modules.illum_calc.calc_cp import CalcIllumInvokeCPModule
from starrynight.modules.illum_calc.calc_cppipe import CalcIllumGenCPPipeModule
from starrynight.modules.illum_calc.calc_load_data import CalcIllumGenLoadDataModule

MODULE_REGISTRY: dict[str, StarrynightModule] = {
    GenInvModule.uid(): GenInvModule,
    GenIndexModule.uid(): GenIndexModule,
    CalcIllumGenLoadDataModule.uid(): CalcIllumGenLoadDataModule,
    CalcIllumGenCPPipeModule.uid(): CalcIllumGenCPPipeModule,
    CalcIllumInvokeCPModule.uid(): CalcIllumInvokeCPModule,
}
