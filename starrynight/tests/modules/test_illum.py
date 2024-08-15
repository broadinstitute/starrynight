"""Illum tests."""

from pathlib import Path

from starrynight.modules.illum import create_pcp_illum
from starrynight.utils.cellprofiler import CellProfilerContext
from starrynight.utils.misc import get_scratch_path


def test_illum_pipe_gen():
    write_path = Path(__file__).parent.joinpath("test.cppipe")
    with CellProfilerContext(get_scratch_path()) as cpipe:
        cpipe = create_pcp_illum(cpipe, [get_scratch_path().joinpath("index.parquet")])
        with write_path.open("w") as f:
            cpipe.dump(f)

    # with CellProfilerContext(get_scratch_path()) as cpipe:
    #     cpipe.load(write_path)
    #     cpipe.run()
