"""Pipecraft pipeline."""

from pathlib import Path

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig
from pipecraft.pipeline import Pipeline, Seq


def create_pipe_illum_loaddata(
    index_path: CloudPath | Path, out_path: CloudPath | Path, prefix: str | None
) -> Pipeline:
    """Create pipeline for load data generation.

    Parameters
    ----------
    index_path: CloudPath |Path
            Path to the index file.
    out_path: CloudPath |Path
            Path to the output directory.
    prefix: Path
        Pass

    Returns
    -------
        Pipeline: A pipecraft Pipeline object configured for load data generation.

    """
    loaddata_pipe = Seq(
        [
            Container(
                "Illumination Calculation Generate Loaddata",
                input_paths={"index": [index_path.resolve().__str__()]},
                output_paths={
                    "loaddata": [out_path.joinpath("loaddata.csv").resolve().__str__()]
                },
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=[
                        "starrynight",
                        "illum",
                        "loaddata",
                        "-i",
                        index_path.resolve().__str__(),
                        "-o",
                        out_path.resolve().__str__(),
                    ],
                    env={},
                ),
            ),
        ]
    )
    return loaddata_pipe


def create_pipe_illum_cppipe(
    load_data_path: CloudPath | Path, illum_cpipe_path: CloudPath | Path
) -> Pipeline:
    """Create a pipeline for illumination calculation.

    This function sets up and returns a pipeline that performs an illumination
    calculation using the specified parameters and configurations.

    Parameters
    ----------
    load_data_path: CloudPath |Path
            Path to the data file or directory needed for the illumination calculation.
    illum_cpipe_path : CloudPath |Path
            The path to the configuration file specific to the illumination pipeline.

    Returns
    -------
        Pipeline: A pipecraft Pipeline object configured for illumination calculations.

    """
    illum_calc_pipe = Seq(
        [
            Container(
                "Illumination Calculation Generate Cppipe",
                input_paths={
                    "loaddata": [load_data_path.resolve().__str__()],
                },
                output_paths={
                    "cppipe": [
                        illum_cpipe_path.joinpath("illum_calc.cppipe")
                        .resolve()
                        .__str__()
                    ]
                },
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=[
                        "starrynight",
                        "illum",
                        "cppipe",
                        "-l",
                        load_data_path.resolve().__str__(),
                        "-o",
                        illum_cpipe_path.resolve().__str__(),
                        "-r",
                        illum_cpipe_path.resolve().__str__(),
                    ],
                    env={},
                ),
            ),
        ]
    )
    return illum_calc_pipe


def create_pipe_illum_run_cp(
    load_data_path: CloudPath | Path, illum_cpipe_path: CloudPath | Path
) -> Pipeline:
    """Create a pipeline for illumination calculation.

    This function sets up and returns a pipeline that performs an illumination
    calculation using the specified parameters and configurations.

    Parameters
    ----------
    load_data_path: CloudPath |Path
            Path to the data file or directory needed for the illumination calculation.
    illum_cpipe_path : CloudPath |Path
            The path to the configuration file specific to the illumination pipeline.

    Returns
    -------
        Pipeline: A pipecraft Pipeline object configured for illumination calculations.

    """
    illum_calc_pipe = Seq(
        [
            Container(
                "Illumination Calculation Generate Cppipe",
                input_paths={
                    "loaddata": [load_data_path.resolve().__str__()],
                },
                output_paths={"cppipe": [illum_cpipe_path.resolve().__str__()]},
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=[
                        "starrynight",
                        "illum",
                        "cppipe",
                        "-l",
                        load_data_path.resolve().__str__(),
                        "-o",
                        illum_cpipe_path.resolve().__str__(),
                        "-r",
                        illum_cpipe_path.resolve().__str__(),
                    ],
                    env={},
                ),
            ),
        ]
    )
    return illum_calc_pipe
