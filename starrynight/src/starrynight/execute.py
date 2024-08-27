"""Execute Illumination Calculate."""

from pathlib import Path

import cellprofiler_core.utilities.java
from cpgdata.utils import parallel
from tqdm import tqdm

from starrynight.utils.cellprofiler import CellProfilerContext


def run_illum(
    uow_list: list[tuple[Path, Path]], out_dir: Path, job_idx: int = 0
) -> None:
    for pipe_path, load_data_path in tqdm(uow_list, position=job_idx):
        with CellProfilerContext(
            out_dir=out_dir,
            loaddata_path=load_data_path,
            require_jvm=False,
        ) as cpipe:
            cpipe.load(str(pipe_path.resolve()))
            cpipe.run()


def run_illum_parallel(
    uow_list: list[tuple[Path, Path]], out_dir: Path, jobs: int = 20
) -> None:
    cellprofiler_core.utilities.java.start_java()
    parallel(uow_list, run_illum, [out_dir], jobs)
    cellprofiler_core.utilities.java.stop_java()
