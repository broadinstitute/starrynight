"""Pipecraft pipeline."""

from pathlib import Path

from pipecraft.node import ContainerConfig, ParContainer
from pipecraft.pipeline import Pipeline, Seq

from starrynight.modules.illum_calc.work_unit import create_work_unit_illum_calc


def create_pipe_illum_calc(load_data_path: Path, illum_cpipe_path: Path) -> Pipeline:
    uow_list = create_work_unit_illum_calc(load_data_path, illum_cpipe_path)
    illum_calc_pipe = Seq(
        [
            ParContainer(
                "Illumination Calculation",
                uow_list=uow_list,
                config=ContainerConfig(
                    image="",
                    cmd=[],
                    env={},
                ),
            ),
        ]
    )
    return illum_calc_pipe
