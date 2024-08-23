"""Test snakemake backend."""

from pathlib import Path

from pipecraft.backend import SnakeMakeBackend, SnakeMakeConfig
from pipecraft.pipeline import PyFunction, Seq


def get_test_out_path() -> Path:
    return Path(__file__).parent.joinpath("out")


def test_snake_seq_node() -> None:
    pipe = Seq(
        [
            PyFunction("A", ["inpath"], ["outpath1"]),
            PyFunction("B", ["inpath"], ["outpath2"]),
            PyFunction("C", ["inpath"], ["outpath3"]),
            PyFunction("D", ["inpath"], ["outpath4"]),
        ]
    )
    backend = SnakeMakeBackend(pipe, SnakeMakeConfig())
    out_dir = get_test_out_path().joinpath("sm_backend")
    out_dir.mkdir(exist_ok=True, parents=True)
    backend.compile(out_dir)
