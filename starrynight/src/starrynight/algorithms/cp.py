"""Invoke cellprofiler."""

from pathlib import Path

import cellprofiler_core.utilities.java
from cpgdata.utils import parallel
from tqdm import tqdm

from starrynight.utils.cellprofiler import CellProfilerContext


def run_cp(
    uow_list: list[tuple[Path, Path]],
    out_dir: Path,
    plugin_dir: Path | None = None,
    job_idx: int = 0,
) -> None:
    """Run cellprofiler for a list of unit-of-work (UOW) items.

    Parameters
    ----------
    uow_list : list[tuple[Path, Path]]
        List of tuples containing the paths to the pipeline and load data files.
    out_dir : Path
        Output directory path.
    plugin_dir : Path
        Path to cellprofiler plugin directory.
    job_idx : int, optional
        Job index for tqdm progress bar (default is 0).

    Returns
    -------
    None

    Notes
    -----
    This function loads each UOW item from the list, runs the CellProfilerContext,
    and saves the results to the specified output directory.

    """
    for pipe_path, load_data_path in tqdm(uow_list, position=job_idx):
        with CellProfilerContext(
            out_dir=out_dir,
            loaddata_path=load_data_path,
            require_jvm=False,
            plugin_dir=plugin_dir,
        ) as cpipe:
            cpipe.load(str(pipe_path.resolve()))
            cpipe.run()


def run_cp_parallel(
    uow_list: list[tuple[Path, Path]],
    out_dir: Path,
    plugin_dir: Path | None = None,
    jobs: int = 20,
) -> None:
    """Run cellprofiler on multiple unit-of-work (UOW) items in parallel.

    Parameters
    ----------
    uow_list : list of tuple of Path
        List of tuples containing the paths to the pipeline and load data files.
    out_dir : Path
        Output directory path.
    plugin_dir : Path
        Path to cellprofiler plugin directory.
    jobs : int, optional
        Number of parallel jobs to use (default is 20).

    Returns
    -------
    None

    Notes
    -----
    This function starts a Java Virtual Machine (JVM) instance using the CellProfiler
    library, runs the Illumination Calculate pipeline on each UOW item in parallel,
    and saves the results to the specified output directory.

    """
    cellprofiler_core.utilities.java.start_java()
    parallel(uow_list, run_cp, [out_dir, plugin_dir], jobs)
    cellprofiler_core.utilities.java.stop_java()
