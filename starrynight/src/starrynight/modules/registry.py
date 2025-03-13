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
from starrynight.modules.sbs_pre_segcheck.pre_segcheck_cp import (
    SBSPreSegcheckInvokeCPModule,
)
from starrynight.modules.sbs_pre_segcheck.pre_segcheck_cppipe import (
    SBSPreSegcheckGenCPPipeModule,
)
from starrynight.modules.sbs_pre_segcheck.pre_segcheck_load_data import (
    SBSPreSegcheckGenLoadDataModule,
)
from starrynight.modules.sbs_preprocess.preprocess_cp import SBSPreprocessInvokeCPModule
from starrynight.modules.sbs_preprocess.preprocess_cppipe import (
    SBSPreprocessGenCPPipeModule,
)
from starrynight.modules.sbs_preprocess.preprocess_load_data import (
    SBSPreprocessGenLoadDataModule,
)

MODULE_REGISTRY: dict[str, StarrynightModule] = {
    # Generate inventory and index for the project
    GenInvModule.uid(): GenInvModule,
    GenIndexModule.uid(): GenIndexModule,
    # CP illum calc
    CPCalcIllumGenLoadDataModule.uid(): CPCalcIllumGenLoadDataModule,
    CPCalcIllumGenCPPipeModule.uid(): CPCalcIllumGenCPPipeModule,
    CPCalcIllumInvokeCPModule.uid(): CPCalcIllumInvokeCPModule,
    # CP illum apply
    CPApplyIllumGenLoadDataModule.uid(): CPApplyIllumGenLoadDataModule,
    CPApplyIllumGenCPPipeModule.uid(): CPApplyIllumGenCPPipeModule,
    CPApplyIllumInvokeCPModule.uid(): CPApplyIllumInvokeCPModule,
    # CP pre segcheck
    CPPreSegcheckGenLoadDataModule.uid(): CPPreSegcheckGenLoadDataModule,
    CPPreSegcheckGenCPPipeModule.uid(): CPPreSegcheckGenCPPipeModule,
    CPPreSegcheckInvokeCPModule.uid(): CPPreSegcheckInvokeCPModule,
    # CP segcheck
    CPSegcheckGenLoadDataModule.uid(): CPSegcheckGenLoadDataModule,
    CPSegcheckGenCPPipeModule.uid(): CPSegcheckGenCPPipeModule,
    CPSegcheckInvokeCPModule.uid(): CPSegcheckInvokeCPModule,
    # SBS illum calc
    SBSCalcIllumGenLoadDataModule.uid(): SBSCalcIllumGenLoadDataModule,
    SBSCalcIllumGenCPPipeModule.uid(): SBSCalcIllumGenCPPipeModule,
    SBSCalcIllumInvokeCPModule.uid(): SBSCalcIllumInvokeCPModule,
    # SBS illum apply
    SBSApplyIllumGenLoadDataModule.uid(): SBSApplyIllumGenLoadDataModule,
    SBSApplyIllumGenCPPipeModule.uid(): SBSApplyIllumGenCPPipeModule,
    SBSApplyIllumInvokeCPModule.uid(): SBSApplyIllumInvokeCPModule,
    # SBS pre segcheck
    SBSPreSegcheckGenLoadDataModule.uid(): SBSPreSegcheckGenLoadDataModule,
    SBSPreSegcheckGenCPPipeModule.uid(): SBSPreSegcheckGenLoadDataModule,
    SBSPreSegcheckInvokeCPModule.uid(): SBSPreSegcheckInvokeCPModule,
    # SBS align
    SBSAlignGenLoadDataModule.uid(): SBSAlignGenLoadDataModule,
    SBSAlignGenCPPipeModule.uid(): SBSAlignGenCPPipeModule,
    SBSAlignInvokeCPModule.uid(): SBSAlignInvokeCPModule,
    # SBS preprocess
    SBSPreprocessGenLoadDataModule.uid(): SBSPreprocessGenLoadDataModule,
    SBSPreprocessGenCPPipeModule.uid(): SBSPreprocessGenCPPipeModule,
    SBSPreprocessInvokeCPModule.uid(): SBSPreprocessInvokeCPModule,
}
