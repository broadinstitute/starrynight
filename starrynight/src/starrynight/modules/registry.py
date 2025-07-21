"""Starrynight module registry."""
# pyright: reportAssignmentType=false

from starrynight.modules.analysis.analysis_cp import AnalysisInvokeCPModule
from starrynight.modules.analysis.analysis_cppipe import AnalysisGenCPPipeModule
from starrynight.modules.analysis.analysis_load_data import (
    AnalysisGenLoadDataModule,
)
from starrynight.modules.common import StarrynightModule
from starrynight.modules.cp_illum_apply.apply_cp import (
    CPApplyIllumInvokeCPModule,
)
from starrynight.modules.cp_illum_apply.apply_cppipe import (
    CPApplyIllumGenCPPipeModule,
)
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
from starrynight.modules.cp_stitchcrop.stitchcrop_fiji import (
    StitchcropInvokeFijiModule,
)
from starrynight.modules.cp_stitchcrop.stitchcrop_pipeline import (
    StitchcropGenPipelineModule,
)
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule
from starrynight.modules.sbs_align.algin_cp import SBSAlignInvokeCPModule
from starrynight.modules.sbs_align.algin_cppipe import SBSAlignGenCPPipeModule
from starrynight.modules.sbs_align.algin_load_data import (
    SBSAlignGenLoadDataModule,
)
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
from starrynight.modules.sbs_pre_segcheck.pre_segcheck_cp import (
    SBSPreSegcheckInvokeCPModule,
)
from starrynight.modules.sbs_pre_segcheck.pre_segcheck_cppipe import (
    SBSPreSegcheckGenCPPipeModule,
)
from starrynight.modules.sbs_pre_segcheck.pre_segcheck_load_data import (
    SBSPreSegcheckGenLoadDataModule,
)
from starrynight.modules.sbs_preprocess.preprocess_cp import (
    SBSPreprocessInvokeCPModule,
)
from starrynight.modules.sbs_preprocess.preprocess_cppipe import (
    SBSPreprocessGenCPPipeModule,
)
from starrynight.modules.sbs_preprocess.preprocess_load_data import (
    SBSPreprocessGenLoadDataModule,
)

MODULE_REGISTRY: dict[str, StarrynightModule] = {
    # Generate inventory and index for the project
    GenInvModule.module_name(): GenInvModule,
    GenIndexModule.module_name(): GenIndexModule,
    # CP illum calc
    CPCalcIllumGenLoadDataModule.module_name(): CPCalcIllumGenLoadDataModule,
    CPCalcIllumGenCPPipeModule.module_name(): CPCalcIllumGenCPPipeModule,
    CPCalcIllumInvokeCPModule.module_name(): CPCalcIllumInvokeCPModule,
    # CP illum apply
    CPApplyIllumGenLoadDataModule.module_name(): CPApplyIllumGenLoadDataModule,
    CPApplyIllumGenCPPipeModule.module_name(): CPApplyIllumGenCPPipeModule,
    CPApplyIllumInvokeCPModule.module_name(): CPApplyIllumInvokeCPModule,
    # CP pre segcheck
    CPPreSegcheckGenLoadDataModule.module_name(): CPPreSegcheckGenLoadDataModule,
    CPPreSegcheckGenCPPipeModule.module_name(): CPPreSegcheckGenCPPipeModule,
    CPPreSegcheckInvokeCPModule.module_name(): CPPreSegcheckInvokeCPModule,
    # CP segcheck
    CPSegcheckGenLoadDataModule.module_name(): CPSegcheckGenLoadDataModule,
    CPSegcheckGenCPPipeModule.module_name(): CPSegcheckGenCPPipeModule,
    CPSegcheckInvokeCPModule.module_name(): CPSegcheckInvokeCPModule,
    # SBS illum calc
    SBSCalcIllumGenLoadDataModule.module_name(): SBSCalcIllumGenLoadDataModule,
    SBSCalcIllumGenCPPipeModule.module_name(): SBSCalcIllumGenCPPipeModule,
    SBSCalcIllumInvokeCPModule.module_name(): SBSCalcIllumInvokeCPModule,
    # SBS illum apply
    SBSApplyIllumGenLoadDataModule.module_name(): SBSApplyIllumGenLoadDataModule,
    SBSApplyIllumGenCPPipeModule.module_name(): SBSApplyIllumGenCPPipeModule,
    SBSApplyIllumInvokeCPModule.module_name(): SBSApplyIllumInvokeCPModule,
    # SBS pre segcheck
    SBSPreSegcheckGenLoadDataModule.module_name(): SBSPreSegcheckGenLoadDataModule,
    SBSPreSegcheckGenCPPipeModule.module_name(): SBSPreSegcheckGenLoadDataModule,
    SBSPreSegcheckInvokeCPModule.module_name(): SBSPreSegcheckInvokeCPModule,
    # SBS align
    SBSAlignGenLoadDataModule.module_name(): SBSAlignGenLoadDataModule,
    SBSAlignGenCPPipeModule.module_name(): SBSAlignGenCPPipeModule,
    SBSAlignInvokeCPModule.module_name(): SBSAlignInvokeCPModule,
    # SBS preprocess
    SBSPreprocessGenLoadDataModule.module_name(): SBSPreprocessGenLoadDataModule,
    SBSPreprocessGenCPPipeModule.module_name(): SBSPreprocessGenCPPipeModule,
    SBSPreprocessInvokeCPModule.module_name(): SBSPreprocessInvokeCPModule,
    # CP Stitchcrop
    StitchcropInvokeFijiModule.module_name(): StitchcropInvokeFijiModule,
    StitchcropGenPipelineModule.module_name(): StitchcropGenPipelineModule,
    # Analysis
    AnalysisGenLoadDataModule.module_name(): AnalysisGenLoadDataModule,
    AnalysisGenCPPipeModule.module_name(): AnalysisGenCPPipeModule,
    AnalysisInvokeCPModule.module_name(): AnalysisInvokeCPModule,
}
