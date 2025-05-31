"""Stitch and crop commands."""

import csv
import json
from io import TextIOWrapper
from pathlib import Path
from subprocess import check_output, run

import polars as pl
from cellprofiler.modules.correctilluminationapply import (
    DOS_DIVIDE,
    CorrectIlluminationApply,
)
from cellprofiler.modules.exporttospreadsheet import (
    DELIMITER_COMMA,
    GP_NAME_METADATA,
    NANS_AS_NANS,
    ExportToSpreadsheet,
)
from cellprofiler.modules.flagimage import C_ANY, S_IMAGE, FlagImage
from cellprofiler.modules.measurecolocalization import (
    M_ACCURATE,
    M_IMAGES,
    MeasureColocalization,
)
from cellprofiler.modules.saveimages import (
    AXIS_T,
    BIT_DEPTH_16,
    FF_TIFF,
    FN_SINGLE_NAME,
    IF_IMAGE,
    WS_EVERY_CYCLE,
    SaveImages,
)
from cellprofiler_core.constants.modules.load_data import (
    ABSOLUTE_FOLDER_NAME,
    DEFAULT_OUTPUT_FOLDER_NAME,
    NO_FOLDER_NAME,
)
from cellprofiler_core.modules.align import (
    A_SIMILARLY,
    C_SAME_SIZE,
    M_CROSS_CORRELATION,
    Align,
)
from cellprofiler_core.modules.loaddata import LoadData
from cellprofiler_core.pipeline import Pipeline
from cellprofiler_core.pipeline.io import dump as dumpit
from cellprofiler_core.preferences import json
from cloudpathlib import AnyPath, CloudPath
from cpgdata.utils import parallel
from mako.template import Template
from tqdm import tqdm

from starrynight.algorithms.index import PCPIndex
from starrynight.modules.cp_illum_apply.constants import (
    CP_ILLUM_APPLY_OUT_PATH_SUFFIX,
)
from starrynight.modules.sbs_illum_calc.constants import (
    SBS_ILLUM_CALC_OUT_PATH_SUFFIX,
)
from starrynight.modules.sbs_preprocess.constants import (
    SBS_PREPROCESS_OUT_PATH_SUFFIX,
)
from starrynight.templates import get_templates_path
from starrynight.utils.cellprofiler import CellProfilerContext
from starrynight.utils.dfutils import (
    filter_df_by_hierarchy,
    filter_images,
    gen_image_hierarchy,
    gen_legacy_channel_map,
    get_channels_by_batch_plate,
    get_channels_from_df,
    get_cycles_by_batch_plate,
    get_cycles_from_df,
    get_default_path_prefix,
)
from starrynight.utils.globbing import flatten_dict, get_files_by
from starrynight.utils.misc import resolve_path_loaddata

###################################
## Fiji pipeline generation
###################################


def mkalldirs(path_list: list[Path]) -> None:
    for path in path_list:
        path.mkdir(parents=True, exist_ok=True)


def write_stitchcrop_pipeline(  # noqa: C901
    f: TextIOWrapper,
    images_dir: Path | CloudPath,
    out_dir: Path | CloudPath,
    level: str,
    exp_config_path: Path | CloudPath,
) -> None:
    mkalldirs(
        [
            images_dir.resolve(),
            out_dir.joinpath("stitched", level).resolve(),
            out_dir.joinpath("cropped", level).resolve(),
            out_dir.joinpath("downsampled", level).resolve(),
            out_dir.joinpath("fiji_temp", level).resolve(),
        ]
    )
    ref_stitchcrop = Template(
        text=get_templates_path()
        .joinpath("stitchcrop_legacy.py.mako")
        .read_text(),
        output_encoding="utf-8",
    ).render(
        images_dir=images_dir.resolve().__str__(),
        stitch_out_dir=out_dir.joinpath("stitched", level).resolve().__str__(),
        tile_out_dir=out_dir.joinpath("cropped", level).resolve().__str__(),
        downsample_out_dir=out_dir.joinpath("downsampled", level)
        .resolve()
        .__str__(),
        temp_dir=out_dir.joinpath("fiji_temp", level).resolve().__str__(),
        exp_config=json.loads(exp_config_path.read_text()),
    )
    ref_stitchcrop = ref_stitchcrop.decode("utf-8")
    f.write(ref_stitchcrop)


def gen_stitchcrop_pipeline(
    index_path: Path | CloudPath,
    pipe_out_dir: Path | CloudPath,
    workspace_dir: Path | CloudPath | None,
    images_path: Path | CloudPath,
    path_mask: str | None,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
    for_sbs: bool = False,
) -> None:
    """Generate load data for segcheck pipeline.

    Parameters
    ----------
    index_path : Path | CloudPath
        Path to index file.
    pipe_out_dir : Path | CloudPath
        Path to save pipeline file.
    workspace_dir : Path | CloudPath.
        Path to save generated output.
    images_path : Path | CloudPath
        Path | CloudPath to painting images directory.
    path_mask : str | None
        Path prefix mask to use.
    use_legacy : bool
        Use legacy cppipe and loaddata.
    exp_config_path : Path | CloudPath
        Path to experiment config json path.
    for_sbs: bool
        For SBS images.

    """
    # Construct images path if not given
    if workspace_dir is None:
        workspace_dir = workspace_dir.parents[1].joinpath("stitchcrop")
    if exp_config_path is None:
        exp_config_path = index_path.parents[1].joinpath(
            "experiment/experiment.json"
        )
    # Load index
    df = pl.scan_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    images_df = filter_images(df, for_sbs)

    # Query default path prefix
    default_path_prefix: str = get_default_path_prefix(images_df)

    # Setup path mask (required for resolving pathnames during the execution)
    if path_mask is None:
        path_mask = default_path_prefix

    # Setup chunking and write loaddata for parallel processing
    images_hierarchy_dict = gen_image_hierarchy(
        images_df, ["batch_id", "plate_id", "well_id", "site_id"]
    )
    levels_leaf = flatten_dict(images_hierarchy_dict)
    for levels, _ in levels_leaf:
        # Construct filename for the loaddata csv
        level_out_path = pipe_out_dir.joinpath(
            f"{'_'.join(levels)}-stitchcrop.py"
        )

        with level_out_path.open("w") as f:
            write_stitchcrop_pipeline(
                f,
                images_dir=images_path.joinpath("-".join(levels)),
                out_dir=workspace_dir,
                level="-".join(levels),
                exp_config_path=exp_config_path,
            )

    return pipe_out_dir


def run_fiji(
    pipeline_list: list[Path | CloudPath],
    fiji_path: Path | None = None,
    job_idx: int = 0,
) -> None:
    """Run stitch crop legacy pipeline.

    Parameters
    ----------
    pipeline_list : Path | CloudPath
        Path | CloudPath to load data csv dir.
    fiji_path : Path
        Path to fiji executable.
    job_idx : int, optional
        Job index for tqdm progress bar (default is 0).

    """
    for pipe_path in tqdm(pipeline_list, position=job_idx):
        cmd = []
        if fiji_path is None:
            cmd += ["fiji"]
        else:
            cmd += [fiji_path.resolve().__str__()]
        cmd += [
            "--ij2",
            "--headless",
            "--run",
            pipe_path.resolve().__str__(),
            "'--yes'",
        ]
        print(f"Executing: {cmd}")
        run(cmd, check=True)


def run_fiji_parallel(
    pipeline_list: list[Path],
    fiji_path: Path | None = None,
    jobs: int = 20,
) -> None:
    """Run cellprofiler on multiple unit-of-work (UOW) items in parallel.

    Parameters
    ----------
    pipeline_list : list of Path
        List of paths to the pipelines.
    fiji_path : Path
        Path to fiji executable.
    jobs : int, optional
        Number of parallel jobs to use (default is 20).

    Returns
    -------
    None

    """
    parallel(pipeline_list, run_fiji, [fiji_path], jobs)


# ------------------------------------------------------
# Run QC checks
# ------------------------------------------------------


def gen_stitch_crop_qc(
    workspace_path: Path | CloudPath,
):
    pass


def run_illum_apply_qc():
    pass
