"""Test snakemake backend."""

from pathlib import Path

from pipecraft.backend.snakemake import SnakeMakeBackend, SnakeMakeConfig
from pipecraft.node import Container, ContainerConfig, ParContainer, UnitOfWork
from pipecraft.pipeline import Seq


def get_test_out_path() -> Path:
    return Path(__file__).parent.joinpath("out")


def test_snake_seq_node() -> None:
    pipe = Seq(
        [
            Container(
                name="Test container 1",
                input_paths={
                    "cpipe": ["s3://test_bucket/cppipe_1", "s3://test_bucket/cppipe_2"],
                    "load_data": [
                        "s3://test_bucket/load_data_1",
                        "s3://test_bucket/load_data_2",
                    ],
                },
                output_paths={
                    "images": ["s3://test_bucket/image_1", "s3://test_bucket/image_2"]
                },
                config=ContainerConfig(image="cellprofiler:5.dev", cmd=[], env={}),
            ),
        ]
    )
    out_dir = get_test_out_path().joinpath("sm_backend")
    out_dir.mkdir(exist_ok=True, parents=True)
    backend = SnakeMakeBackend(pipe, SnakeMakeConfig(), out_dir, out_dir)
    backend.compile()
    # backend.run()


def test_snake_seq_parcontainer_node() -> None:
    uow = [
        UnitOfWork(
            inputs={"cpipe": ["test_bucket/cppipe_1"]},
            outputs={"images": ["test_bucket/image_1"]},
        ),
        UnitOfWork(
            inputs={"cpipe": ["test_bucket/cppipe_2"]},
            outputs={"images": ["test_bucket/image_2"]},
        ),
    ]
    pipe = Seq(
        [
            ParContainer(
                name="echo_ubuntu",
                uow_list=uow,
                config=ContainerConfig(
                    image="ubuntu:latest", cmd=["echo", "{input.cpipe}"], env={}
                ),
            ),
        ]
    )
    out_dir = get_test_out_path().joinpath("sm_container")
    out_dir.mkdir(exist_ok=True, parents=True)
    backend = SnakeMakeBackend(
        pipe, SnakeMakeConfig(apptainer=True, print_exec=True), out_dir, out_dir
    )
    backend.compile()
    backend.run()
