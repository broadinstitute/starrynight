# """Illum tests."""

# from pathlib import Path

# from starrynight.modules.cp_illum_calc import create_pipe_cp_illum
# from starrynight.utils.cellprofiler import CellProfilerContext
# from starrynight.utils.misc import get_scratch_path


# def test_illum_pipe_gen():
#     write_path = Path(__file__).parent.parent.joinpath("fixtures/test.cppipe")
#     with CellProfilerContext(get_scratch_path()) as cpipe:
#         cpipe = create_pipe_cp_illum(
#             cpipe, [get_scratch_path().joinpath("index.parquet")]
#         )
#         with write_path.open("w") as f:
#             cpipe.dump(f)

#     # with CellProfilerContext(get_scratch_path()) as cpipe:
#     #     cpipe.load(write_path)
#     #     cpipe.run()
