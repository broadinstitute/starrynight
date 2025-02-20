"""Calculate illumination correction calculate invoke cellprofiler module."""

from pathlib import Path
from typing import Self

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig, UnitOfWork
from pipecraft.pipeline import Pipeline, Seq

from starrynight.experiments.common import Experiment
from starrynight.modules.common import StarrynightModule
from starrynight.modules.sbs_illum_calc.constants import (
    SBS_ILLUM_CALC_CP_CPPIPE_OUT_PATH_SUFFIX,
    SBS_ILLUM_CALC_CP_LOADDATA_OUT_PATH_SUFFIX,
    SBS_ILLUM_CALC_OUT_PATH_SUFFIX,
)
from starrynight.modules.schema import (
    Container as SpecContainer,
)
from starrynight.modules.schema import (
    ExecFunction,
    TypeAlgorithmFromCitation,
    TypeCitations,
    TypeEnum,
    TypeInput,
    TypeOutput,
)
from starrynight.schema import DataConfig


def create_work_unit_gen_index(out_dir: Path | CloudPath) -> list[UnitOfWork]:
    """Create units of work for Generate Index step.

    Parameters
    ----------
    out_dir : Path | CloudPath
        Path to load data csv. Can be local or cloud.

    Returns
    -------
    list[UnitOfWork]
        List of unit of work.

    """
    uow_list = [
        UnitOfWork(
            inputs={
                "inventory": [out_dir.joinpath("inventory.parquet").resolve().__str__()]
            },
            outputs={"index": [out_dir.joinpath("index.parquet").resolve().__str__()]},
        )
    ]

    return uow_list


def create_pipe_gen_cpinvoke(uid: str, spec: SpecContainer) -> Pipeline:
    """Create pipeline for invoking cellprofiler.

    Parameters
    ----------
    uid: str
        Module unique id.
    spec: SpecContainer
        CalcIllumInvokeCPModule specification.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    cmd = [
        "starrynight",
        "cp",
        "-p",
        spec.inputs[0].path,
        "-l",
        spec.inputs[1].path,
        "-o",
        spec.outputs[0].path,
        "--sbs",
    ]

    gen_load_data_pipe = Seq(
        [
            Container(
                name=uid,
                input_paths={
                    "cppipe_path": [spec.inputs[0].path],
                    "load_data_path": [spec.inputs[1].path],
                },
                output_paths={"illum_dir": [spec.outputs[0].path]},
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=cmd,
                    env={},
                ),
            ),
        ]
    )
    return gen_load_data_pipe


class SBSCalcIllumInvokeCPModule(StarrynightModule):
    """SBSCalculate illumination invoke cellprofiler module."""

    @staticmethod
    def uid() -> str:
        """Return module unique id."""
        return "sbs_calc_illum_invoke_cp"

    @staticmethod
    def _spec() -> str:
        """Return module default spec."""
        return SpecContainer(
            inputs=[
                TypeInput(
                    name="cppipe_path",
                    type=TypeEnum.files,
                    description="Path to the cppipe file.",
                    optional=False,
                    path="path/to/the/cppipe",
                ),
                TypeInput(
                    name="load_data_path",
                    type=TypeEnum.files,
                    description="Path to the LoadData csv.",
                    optional=False,
                    path="path/to/the/loaddata",
                ),
            ],
            outputs=[
                TypeOutput(
                    name="plate_illum",
                    type=TypeEnum.files,
                    description="Generated Illum correction files for the plate",
                    optional=False,
                    path="random/path/to/illum plate dir",
                ),
                TypeOutput(
                    name="cppipe_notebook",
                    type=TypeEnum.notebook,
                    description="Notebook for inspecting generated illum corrections",
                    optional=False,
                    path="http://karkinos:2720/?file=.%2FillumCalcOutput.py",
                ),
            ],
            parameters=[],
            display_only=[],
            results=[],
            exec_function=ExecFunction(
                name="",
                script="",
                module="",
                cli_command="",
            ),
            docker_image=None,
            algorithm_folder_name=None,
            citations=TypeCitations(
                algorithm=[
                    TypeAlgorithmFromCitation(
                        name="Starrynight SBS illum calculation invoke cellprofiler module",
                        description="This module invoke cellprofiler for generating sbs illumination corrections.",
                    )
                ]
            ),
        )

    @staticmethod
    def from_config(
        data: DataConfig,
        experiment: Experiment | None = None,
        spec: SpecContainer | None = None,
    ) -> Self:
        """Create module from experiment and data config."""
        if spec is None:
            spec = SBSCalcIllumInvokeCPModule._spec()
            spec.inputs[0].path = (
                data.workspace_path.joinpath(SBS_ILLUM_CALC_CP_CPPIPE_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )

            spec.inputs[1].path = (
                data.workspace_path.joinpath(SBS_ILLUM_CALC_CP_LOADDATA_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )

            spec.outputs[0].path = (
                data.workspace_path.joinpath(SBS_ILLUM_CALC_OUT_PATH_SUFFIX)
                .resolve()
                .__str__()
            )
        pipe = create_pipe_gen_cpinvoke(
            uid=SBSCalcIllumInvokeCPModule.uid(),
            spec=spec,
        )
        uow = create_work_unit_gen_index(out_dir=data.storage_path.joinpath("index"))

        return SBSCalcIllumInvokeCPModule(spec=spec, pipe=pipe, uow=uow)
