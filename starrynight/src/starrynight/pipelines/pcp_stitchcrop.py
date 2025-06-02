"""Pooled CellPainting Generic Pipeline."""
# pyright: reportArgumentType=false

from functools import partial

from pipecraft.pipeline import Parallel, Pipeline, Seq

from starrynight.experiments.common import Experiment
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
from starrynight.modules.cp_segcheck.segcheck_cp import (
    CPSegcheckInvokeCPModule,
)
from starrynight.modules.cp_segcheck.segcheck_cppipe import (
    CPSegcheckGenCPPipeModule,
)
from starrynight.modules.cp_segcheck.segcheck_load_data import (
    CPSegcheckGenLoadDataModule,
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
from starrynight.modules.sbs_preprocess.preprocess_cp import (
    SBSPreprocessInvokeCPModule,
)
from starrynight.modules.sbs_preprocess.preprocess_cppipe import (
    SBSPreprocessGenCPPipeModule,
)
from starrynight.modules.sbs_preprocess.preprocess_load_data import (
    SBSPreprocessGenLoadDataModule,
)
from starrynight.modules.schema import SpecContainer
from starrynight.modules.stitchcrop.stitchcrop_fiji import (
    StitchcropInvokeFijiModule,
)
from starrynight.modules.stitchcrop.stitchcrop_pipeline import (
    StitchcropGenPipelineModule,
)
from starrynight.pipelines.common import apply_module_params
from starrynight.schema import DataConfig


def create_pcp_stitchcrop_pipeline(
    data: DataConfig,
    experiment: Experiment | None = None,
    updated_spec_dict: dict[str, SpecContainer] = {},
) -> tuple[list[StarrynightModule], Pipeline]:
    # Write out the experiment config as a json file
    experiment_dir = data.workspace_path.joinpath("experiment")
    experiment_dir.mkdir(parents=True, exist_ok=True)
    experiment_dir.joinpath("experiment.json").write_text(
        experiment.model_dump_json()
    )

    # Initialize modules
    init_module = partial(
        apply_module_params, data, experiment, updated_spec_dict
    )
    module_list = [
        # cp modules
        cp_illum_calc_loaddata := init_module(CPCalcIllumGenLoadDataModule),
        cp_illum_calc_cpipe := init_module(CPCalcIllumGenCPPipeModule),
        cp_illum_calc_cp := init_module(CPCalcIllumInvokeCPModule),
        cp_apply_calc_loaddata := init_module(CPApplyIllumGenLoadDataModule),
        cp_apply_calc_cpipe := init_module(CPApplyIllumGenCPPipeModule),
        cp_apply_calc_cp := init_module(CPApplyIllumInvokeCPModule),
        cp_segcheck_loaddata := init_module(CPSegcheckGenLoadDataModule),
        cp_segcheck_cpipe := init_module(CPSegcheckGenCPPipeModule),
        cp_segcheck_cp := init_module(CPSegcheckInvokeCPModule),
        # sbs related modules
        sbs_illum_calc_loaddata := init_module(SBSCalcIllumGenLoadDataModule),
        sbs_illum_calc_cpipe := init_module(SBSCalcIllumGenCPPipeModule),
        sbs_illum_calc_cp := init_module(SBSCalcIllumInvokeCPModule),
        sbs_illum_apply_loaddata := init_module(SBSApplyIllumGenLoadDataModule),
        sbs_illum_apply_cpipe := init_module(SBSApplyIllumGenCPPipeModule),
        sbs_illum_apply_cp := init_module(SBSApplyIllumInvokeCPModule),
        sbs_preprocess_loaddata := init_module(SBSPreprocessGenLoadDataModule),
        sbs_preprocess_cpipe := init_module(SBSPreprocessGenCPPipeModule),
        sbs_preprocess_cp := init_module(SBSPreprocessInvokeCPModule),
        # stitch and crop
        stitchcrop_pipeline := init_module(StitchcropGenPipelineModule),
        stitchcrop_fiji := init_module(StitchcropInvokeFijiModule),
        # analysis
        analysis_loaddata := init_module(AnalysisGenLoadDataModule),
        analysis_cpipe := init_module(AnalysisGenCPPipeModule),
        analysis_cp := init_module(AnalysisInvokeCPModule),
    ]

    # Set use legacy flag if required
    if experiment.use_legacy:
        for module in module_list:
            if "use_legacy" in module.spec.inputs.keys():
                module.spec.inputs["use_legacy"].value = True

    return module_list, Seq(
        [
            Parallel(
                [
                    Seq(
                        [
                            cp_illum_calc_loaddata.pipe,
                            cp_illum_calc_cpipe.pipe,
                            cp_illum_calc_cp.pipe,
                            cp_apply_calc_loaddata.pipe,
                            cp_apply_calc_cpipe.pipe,
                            cp_apply_calc_cp.pipe,
                            cp_segcheck_loaddata.pipe,
                            cp_segcheck_cpipe.pipe,
                            cp_segcheck_cp.pipe,
                        ]
                    ),
                    Seq(
                        [
                            sbs_illum_calc_loaddata.pipe,
                            sbs_illum_calc_cpipe.pipe,
                            sbs_illum_calc_cp.pipe,
                            sbs_illum_apply_loaddata.pipe,
                            sbs_illum_apply_cpipe.pipe,
                            sbs_illum_apply_cp.pipe,
                            sbs_preprocess_loaddata.pipe,
                            sbs_preprocess_cpipe.pipe,
                            sbs_preprocess_cp.pipe,
                        ]
                    ),
                ]
            ),
            stitchcrop_pipeline.pipe,
            stitchcrop_fiji.pipe,
            analysis_loaddata.pipe,
            analysis_cpipe.pipe,
            analysis_cp.pipe,
        ]
    )
