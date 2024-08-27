"""Pipecraft pipeline."""

from pathlib import Path

from cloudpathlib import CloudPath
from pipecraft.node import Container, ContainerConfig
from pipecraft.pipeline import Pipeline, Seq


def create_pipe_gen_inv(
    dataset_path: Path | CloudPath, out_dir: Path | CloudPath
) -> Pipeline:
    """Create pipeline for gen inv.

    Parameters
    ----------
    dataset_path : Path | CloudPath
        Dataset path. Can be local or cloud.
    out_dir : Path | CloudPath
        Path to save outpus. Can be local or cloud.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    gen_index_pipe = Seq(
        [
            Container(
                "Generate Inventory",
                input_paths={},
                output_paths={
                    "inventory": [
                        out_dir.joinpath("inventory.parquet").resolve().__str__()
                    ]
                },
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=[
                        "starrynight",
                        "inventory",
                        "gen",
                        "-d",
                        dataset_path.resolve().__str__(),
                        "-o",
                        out_dir.resolve().__str__(),
                    ],
                    env={},
                ),
            ),
        ]
    )
    return gen_index_pipe


def create_pipe_gen_index(
    inventory_path: Path | CloudPath, out_dir: Path | CloudPath
) -> Pipeline:
    """Create pipeline for gen index.

    Parameters
    ----------
    inventory_path : Path | CloudPath
        Inventory path. Can be local or cloud.
    out_dir : Path | CloudPath
        Path to save outpus. Can be local or cloud.

    Returns
    -------
    Pipeline
        Pipeline instance.

    """
    gen_index_pipe = Seq(
        [
            Container(
                "Generate Index",
                input_paths={"inventory": [inventory_path.resolve().__str__()]},
                output_paths={
                    "index": [out_dir.joinpath("index.parquet").resolve().__str__()]
                },
                config=ContainerConfig(
                    image="ghrc.io/leoank/starrynight:dev",
                    cmd=[
                        "starrynight",
                        "index",
                        "gen",
                        "-i",
                        inventory_path.resolve().__str__(),
                        "-o",
                        out_dir.resolve().__str__(),
                    ],
                    env={},
                ),
            ),
        ]
    )
    return gen_index_pipe
