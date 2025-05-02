"""Illum Calculate commands."""

import csv
import json
from io import TextIOWrapper
from pathlib import Path

import polars as pl
from cellprofiler.modules.correctilluminationcalculate import (
    EA_ALL_ACROSS,
    FI_MANUALLY,
    IC_REGULAR,
    SM_MEDIAN_FILTER,
    CorrectIlluminationCalculate,
)
from cellprofiler.modules.resize import (
    C_MANUAL,
    I_BILINEAR,
    R_BY_FACTOR,
    Resize,
)
from cellprofiler.modules.saveimages import (
    AXIS_T,
    FF_NPY,
    FN_SINGLE_NAME,
    IF_IMAGE,
    WS_LAST_CYCLE,
    SaveImages,
)
from cellprofiler_core.constants.modules.load_data import (
    ABSOLUTE_FOLDER_NAME,
    DEFAULT_OUTPUT_FOLDER_NAME,
    NO_FOLDER_NAME,
)
from cellprofiler_core.modules.loaddata import LoadData
from cellprofiler_core.pipeline import Pipeline
from cellprofiler_core.pipeline.io import dump as dumpit
from centrosome.bg_compensate import MODE_AUTO
from cloudpathlib import CloudPath

from starrynight.algorithms.index import PCPIndex
from starrynight.templates import get_templates_path
from starrynight.utils.cellprofiler import CellProfilerContext
from starrynight.utils.dfutils import (
    filter_df_by_hierarchy,
    filter_images,
    gen_image_hierarchy,
    gen_legacy_channel_map,
    get_channels_from_df,
    get_cycles_by_batch_plate,
    get_default_path_prefix,
)
from starrynight.utils.globbing import flatten_dict, get_files_by

###############################
## Load data generation
###############################


def write_loaddata_illum_calc(
    images_df: pl.LazyFrame,
    plate_channel_list: list[str],
    path_mask: str,
    f: TextIOWrapper,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
) -> None:
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)

    # Setup metadata headers
    metadata_heads = [
        f"Metadata_{col}" for col in ["Batch", "Plate", "Site", "Well", "Cycle"]
    ]

    if use_legacy:
        # Load experiment config
        exp_config = json.loads(exp_config_path.read_text())

        # setup legacy_channel_map
        legacy_channel_map = gen_legacy_channel_map(
            plate_channel_list, exp_config
        )
        plate_channel_list = [
            legacy_channel_map[ch] for ch in plate_channel_list
        ]

    # Setup FileName, PathName and FrameName headers
    filename_heads = [f"FileName_Orig{ch}" for ch in plate_channel_list]
    frame_heads = [f"Frame_Orig{ch}" for ch in plate_channel_list]
    pathname_heads = [f"PathName_Orig{ch}" for ch in plate_channel_list]

    # Write the headers first
    loaddata_writer.writerow(
        [*metadata_heads, *filename_heads, *frame_heads, *pathname_heads]
    )

    # Iterate over index and add all the files
    for index in images_df.collect().to_dicts():
        index = PCPIndex(**index)
        assert index.channel_dict is not None
        if use_legacy:
            index.channel_dict = [
                legacy_channel_map[ch] for ch in index.channel_dict
            ]
        # make sure frame heads are matched with their order in the filenames
        frame_index = [
            index.channel_dict.index(ch) for ch in plate_channel_list
        ]
        assert index.key is not None
        loaddata_writer.writerow(
            [
                # Metadata heads
                index.batch_id,
                index.plate_id,
                index.site_id,
                index.well_id,
                f"{int(index.cycle_id):02}"
                if index.cycle_id is not None
                else 0,
                # Filename heads
                *[f"{index.filename}" for _ in range(len(filename_heads))],
                # Frame heads
                *[str(i) for i in frame_index],
                # Pathname heads
                *[
                    # We need to remove the file name from the "key"
                    # (expected by cellprofiler)
                    f"{path_mask.rstrip('/')}/{'/'.join(index.key.split('/')[0:-1])}/"
                    for _ in range(len(pathname_heads))
                ],
            ]
        )


def gen_illum_calc_load_data(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    for_sbs: bool = False,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
) -> Path | CloudPath:
    """Generate load data for illum calc pipeline.

    Parameters
    ----------
    index_path : Path | CloudPath
        Path to index file.
    out_path : Path | CloudPath
        Path to save output csv file.
    path_mask : str | None
        Path prefix mask to use.
    for_sbs : bool
        Generate illums for SBS images.
    use_legacy : bool
        Use legacy cppipe and loaddata.
    exp_config_path : Path | CloudPath
        Path to experiment config json path.

    Returns
    -------
    Path | CloudPath:
        Path to the generated files

    References
    ----------
    Starrynight Generate Illum Calc LoadData module.

    This modules generates load data for the illum calculate step of the pipeline.

    """
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
    if not for_sbs:
        images_hierarchy_dict = gen_image_hierarchy(
            images_df, ["batch_id", "plate_id", "well_id"]
        )
    else:
        images_hierarchy_dict = gen_image_hierarchy(
            images_df, ["batch_id", "plate_id", "cycle_id", "well_id"]
        )
    levels_leaf = flatten_dict(images_hierarchy_dict)
    for levels, _ in levels_leaf:
        # setup filtered df for chunked levels
        levels_df = filter_df_by_hierarchy(images_df, levels, for_sbs)

        # Setup channel list for this level
        plate_channel_list = get_channels_from_df(levels_df)

        # Construct filename for the loaddata csv
        level_out_path = out_path.joinpath(f"{'_'.join(levels)}_illum_calc.csv")

        with level_out_path.open("w") as f:
            write_loaddata_illum_calc(
                levels_df,
                plate_channel_list,
                path_mask,
                f,
                use_legacy,
                exp_config_path,
            )
    return out_path


###################################
## CellProfiler pipeline generation
###################################


def generate_illum_calculate_pipeline(
    pipeline: Pipeline, load_data_path: Path | CloudPath, for_sbs: bool = False
) -> Pipeline:
    load_data_df = pl.read_csv(load_data_path.resolve().__str__())
    channel_list = [
        col.split("_")[1]
        for col in load_data_df.columns
        if col.startswith("Frame")
    ]
    module_counter = 0

    # INFO: Configure load data module
    load_data = LoadData()
    module_counter += 1
    load_data.module_num = module_counter
    load_data.csv_directory.value = f"{ABSOLUTE_FOLDER_NAME}|" + str(
        load_data_path.parent.resolve()
    )
    load_data.csv_file_name.value = str(load_data_path.name)
    load_data.wants_images.value = True
    load_data.image_directory.value = f"{NO_FOLDER_NAME}|"
    load_data.wants_rows.value = False
    # load_data.row_range.value = ""
    load_data.wants_image_groupings.value = True
    if not for_sbs:
        load_data.metadata_fields.value = "Batch,Plate"
    else:
        load_data.metadata_fields.value = "Batch,Plate,Cycle"
    load_data.rescale.value = True
    pipeline.add_module(load_data)

    # INFO: Create and configure required modules
    # resize(downsample) -> correct_illum_calculate -> resize(upsample)
    # -> save(upsample) modules -> create batch
    for col in channel_list:
        resize_down = Resize()
        module_counter += 1
        resize_down.module_num = module_counter
        resize_down.x_name.value = f"{col}"
        resize_down.y_name.value = f"Downsampled{col}"
        resize_down.size_method.value = R_BY_FACTOR
        resize_down.resizing_factor_x.value = 0.25
        resize_down.resizing_factor_y.value = 0.25
        # resize_down.resizing_factor_z.value = ""
        resize_down.specific_width.value = 100
        resize_down.specific_height.value = 100
        # resize_down.specific_planes.value = ""
        resize_down.interpolation.value = I_BILINEAR
        resize_down.use_manual_or_image.value = C_MANUAL
        resize_down.specific_image.value = None
        resize_down.additional_image_count.value = "0"
        pipeline.add_module(resize_down)

        correct_illum_calculate = CorrectIlluminationCalculate()
        module_counter += 1
        correct_illum_calculate.module_num = module_counter
        correct_illum_calculate.image_name.value = f"Downsampled{col}"
        correct_illum_calculate.illumination_image_name.value = f"Illum{col}"
        correct_illum_calculate.intensity_choice.value = IC_REGULAR
        correct_illum_calculate.dilate_objects.value = False
        correct_illum_calculate.object_dilation_radius.value = 1
        correct_illum_calculate.block_size.value = 60
        correct_illum_calculate.rescale_option.value = "Yes"
        correct_illum_calculate.each_or_all.value = EA_ALL_ACROSS
        correct_illum_calculate.smoothing_method.value = SM_MEDIAN_FILTER
        correct_illum_calculate.automatic_object_width.value = FI_MANUALLY
        correct_illum_calculate.object_width.value = 10
        correct_illum_calculate.size_of_smoothing_filter.value = 20
        correct_illum_calculate.save_average_image.value = False
        correct_illum_calculate.average_image_name.value = f"Illum{col}Avg"
        correct_illum_calculate.save_dilated_image.value = False
        correct_illum_calculate.dilated_image_name.value = f"Illum{col}Dilated"
        correct_illum_calculate.automatic_splines.value = True
        correct_illum_calculate.spline_bg_mode.value = MODE_AUTO
        correct_illum_calculate.spline_points.value = 5
        correct_illum_calculate.spline_threshold.value = 2
        correct_illum_calculate.spline_rescale.value = 2
        correct_illum_calculate.spline_maximum_iterations.value = 40
        correct_illum_calculate.spline_convergence.value = 0.001
        pipeline.add_module(correct_illum_calculate)

        resize_up = Resize()
        module_counter += 1
        resize_up.module_num = module_counter
        resize_up.x_name.value = f"Illum{col}"
        resize_up.y_name.value = f"UpsampledIllum{col}"
        resize_up.size_method.value = R_BY_FACTOR
        resize_up.resizing_factor_x.value = 4
        resize_up.resizing_factor_y.value = 4
        # resize_up.resizing_factor_z.value = ""
        resize_up.specific_width.value = 100
        resize_up.specific_height.value = 100
        # resize_up.specific_planes.value = ""
        resize_up.interpolation.value = I_BILINEAR
        resize_up.use_manual_or_image.value = C_MANUAL
        resize_up.specific_image.value = None
        resize_up.additional_image_count.value = "0"
        pipeline.add_module(resize_up)

        save_image = SaveImages()
        module_counter += 1
        save_image.module_num = module_counter
        save_image.save_image_or_figure.value = IF_IMAGE
        save_image.image_name.value = f"UpsampledIllum{col}"
        save_image.file_name_method.value = FN_SINGLE_NAME
        # save_image.file_image_name.value = ""
        save_image.number_of_digits.value = 4
        save_image.wants_file_name_suffix.value = False
        save_image.file_name_suffix.value = ""
        save_image.file_format.value = FF_NPY
        save_image.pathname.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
        # save_image.bit_depth.value = ""
        save_image.overwrite.value = False
        save_image.when_to_save.value = WS_LAST_CYCLE
        save_image.update_file_names.value = False
        save_image.create_subdirectories.value = False
        # save_image.root_dir.value = ""
        save_image.stack_axis.value = AXIS_T
        # save_image.tiff_compress.value = ""
        pipeline.add_module(save_image)

        # Do not add subfolders as cellprofiler won't create them automatically and fail
        if not for_sbs:
            save_image.single_file_name.value = (
                f"\\g<Batch>_\\g<Plate>_Illum{col}"
            )
        else:
            save_image.single_file_name.value = (
                f"\\g<Batch>_\\g<Plate>_\\g<Cycle>_Illum{col}"
            )

    # TODO: Figure out why having this makes the pipeline a noop
    # create_batch_files = CreateBatchFiles()
    # module_counter += 1
    # create_batch_files.module_num = module_counter
    # create_batch_files.wants_default_output_directory.value = True
    # # create_batch_files.custom_output_directory.value = ""
    # create_batch_files.remote_host_is_windows.value = False
    # create_batch_files.batch_mode.value = False
    # create_batch_files.distributed_mode.value = False
    # # create_batch_files.default_image_directory.value = ""
    # create_batch_files.revision.value = 0
    # create_batch_files.from_old_matlab.value = False
    # pipeline.add_module(create_batch_files)

    return pipeline


def gen_illum_calc_cppipe(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    for_sbs: bool = False,
    use_legacy: bool = False,
) -> None:
    """Write out illumination calculate pipeline to file.

    Parameters
    ----------
    load_data_path : Path | CloudPath
        Path | CloudPath to load data csv dir.
    out_dir : Path | CloudPath
        Path | CloudPath to output directory.
    workspace_path : Path | CloudPath
        Path | CloudPath to workspace directory.
    for_sbs : str | None
        Generate illums for SBS images.
    use_legacy : str | None
        Use legacy illumination calculate pipeline.

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)

    # Get all the generated load data files by batch
    if not for_sbs:
        type_suffix = "painting"
    else:
        type_suffix = "sbs"

    filename = f"illum_calc_{type_suffix}.cppipe"

    # Write old cppipe and return early if use_old is true
    if use_legacy:
        if not for_sbs:
            ref_cppipe = get_templates_path() / "cppipe/ref_1_CP_Illum.cppipe"
        else:
            ref_cppipe = get_templates_path() / "cppipe/ref_5_BC_Illum.cppipe"

        out_dir.joinpath(filename).write_text(ref_cppipe.read_text())
        return

    # get one of the load data for generating cpipe
    sample_loaddata_file = next(load_data_path.rglob("*.csv"))

    with CellProfilerContext(out_dir=workspace_path) as cpipe:
        cpipe = generate_illum_calculate_pipeline(
            cpipe, sample_loaddata_file, for_sbs
        )
        filename = f"illum_calc_{type_suffix}.cppipe"
        with out_dir.joinpath(filename).open("w") as f:
            cpipe.dump(f)
        filename = f"illum_calc_{type_suffix}.json"
        with out_dir.joinpath(filename).open("w") as f:
            dumpit(cpipe, f, version=6)
