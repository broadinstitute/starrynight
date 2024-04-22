from pathlib import Path
from pipecraft.pipeline import Parallel, Pipeline, Seq, PyFunction
from pipecraft.utils import save_pipeline_plot
from pydantic import BaseModel


def get_test_out_path() -> Path:
    return Path(__file__).parent.joinpath("out")


def test_seq_node():
    pipe = Seq(
        [
            PyFunction("A", ["in path"], ["out path"]),
            PyFunction("B", ["in path"], ["out path"]),
            PyFunction("C", ["in path"], ["out path"]),
            PyFunction("D", ["in path"], ["out path"]),
        ]
    )
    assert len(pipe.resolved_list) == 4
    pipe.compile()
    assert len(pipe.pipeline.nodes) == 4
    save_pipeline_plot(pipe.pipeline, get_test_out_path().joinpath("test_seq_node"))


def test_seq_pipe_node():
    pipe = Seq(
        [
            PyFunction("A", ["in path"], ["out path"]),
            Seq(
                [
                    PyFunction("B", ["in path"], ["out path"]),
                    PyFunction("C", ["in path"], ["out path"]),
                    Seq(
                        [
                            Seq(
                                [
                                    PyFunction("H", ["in path"], ["out path"]),
                                ]
                            ),
                            PyFunction("F", ["in path"], ["out path"]),
                            PyFunction("G", ["in path"], ["out path"]),
                        ]
                    ),
                ]
            ),
            PyFunction("D", ["in path"], ["out path"]),
        ]
    )
    assert len(pipe.resolved_list) == 3
    pipe.compile()
    assert len(pipe.pipeline.nodes) == 7
    print(pipe.pipeline.nodes)
    save_pipeline_plot(
        pipe.pipeline, get_test_out_path().joinpath("test_seq_pipe_node")
    )


def test_par_node():
    pipe = Parallel(
        [
            PyFunction("A", ["in path"], ["out path"]),
            PyFunction("B", ["in path"], ["out path"]),
            PyFunction("C", ["in path"], ["out path"]),
            PyFunction("D", ["in path"], ["out path"]),
        ]
    )
    assert len(pipe.resolved_list) == 6
    pipe.compile()
    assert len(pipe.pipeline.nodes) == 6
    print(pipe.node_list)
    save_pipeline_plot(pipe.pipeline, get_test_out_path().joinpath("test_par_node"))


def test_par_pipe_node():
    pipe = Parallel(
        [
            PyFunction("A", ["in path"], ["out path"]),
            PyFunction("B", ["in path"], ["out path"]),
            Parallel(
                [
                    PyFunction("E", ["in path"], ["out path"]),
                    PyFunction("F", ["in path"], ["out path"]),
                ]
            ),
            PyFunction("C", ["in path"], ["out path"]),
            PyFunction("D", ["in path"], ["out path"]),
        ]
    )
    assert len(pipe.resolved_list) == 7
    pipe.compile()
    assert len(pipe.pipeline.nodes) == 10
    print(pipe.node_list)
    save_pipeline_plot(
        pipe.pipeline, get_test_out_path().joinpath("test_par_pipe_node")
    )


def test_seq_par():
    pipe = Seq(
        [
            PyFunction("A", ["in path"], ["out path"]),
            Seq(
                [
                    PyFunction("B", ["in path"], ["out path"]),
                    PyFunction("C", ["in path"], ["out path"]),
                    Parallel(
                        [
                            Parallel(
                                [
                                    PyFunction("H", ["in path"], ["out path"]),
                                ]
                            ),
                            PyFunction("F", ["in path"], ["out path"]),
                            PyFunction("G", ["in path"], ["out path"]),
                        ]
                    ),
                ]
            ),
            PyFunction("D", ["in path"], ["out path"]),
        ]
    )
    assert len(pipe.resolved_list) == 3
    pipe.compile()
    assert len(pipe.pipeline.nodes) == 11
    print(pipe.pipeline.nodes)
    save_pipeline_plot(pipe.pipeline, get_test_out_path().joinpath("test_seq_par"))


class PCPImageProcessingPipeline(BaseModel):
    param1: str
    param2: int
    param3: dict

    def gen_pipe(self: "PCPImageProcessingPipeline") -> Pipeline:
        PCP_1 = Seq(
            [
                PyFunction("PCP1", ["in path"], ["out_path"]),
                PyFunction("Illum", ["in_path"], ["out"]),
            ]
        )
        PCP_2 = Seq([PyFunction("PCP2", ["in path"], ["out_path"])])
        PCP_3 = Seq([PyFunction("PCP3", ["in path"], ["out_path"])])
        pipe = Seq([PCP_1, Parallel([PCP_2, PCP_3])])
        return pipe


pcp_pipe = PCPImageProcessingPipeline(
    param1="param1",
    param2=1,
    param3={},
)
