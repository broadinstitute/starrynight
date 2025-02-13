"""Illum Calculate commands."""

import csv
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
from cellprofiler.modules.resize import C_MANUAL, I_BILINEAR, R_BY_FACTOR, Resize
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
from centrosome.bg_compensate import MODE_AUTO
from cloudpathlib import CloudPath

from starrynight.algorithms.index import PCPIndex
from starrynight.utils.cellprofiler import CellProfilerContext
from starrynight.utils.dfutils import (
    gen_image_hierarchy,
    get_channels_by_batch_plate,
    get_cycles_by_batch_plate,
)

###############################
## Load data generation
###############################


def write_loaddata(
    images_df: pl.DataFrame,
    plate_channel_list: list[str],
    path_mask: str,
    f: TextIOWrapper,
) -> None:
    # setup csv headers and write the header first
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    metadata_heads = [f"Metadata_{col}" for col in ["Plate", "Site", "Well"]]
    filename_heads = [f"FileName_Orig{col}" for col in plate_channel_list]
    frame_heads = [f"Frame_Orig{col}" for col in plate_channel_list]
    pathname_heads = [f"PathName_Orig{col}" for col in plate_channel_list]
    loaddata_writer.writerow(
        [*metadata_heads, *filename_heads, *frame_heads, *pathname_heads]
    )
    for index in images_df.to_dicts():
        index = PCPIndex(**index)
        # make sure frame heads are matched with their order in the filenames
        frame_index = [index.channel_dict.index(channel) for channel in frame_heads]
        assert index.key is not None
        loaddata_writer.writerow(
            [
                # Metadata heads
                index.plate_id,
                index.site_id,
                index.well_id,
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


def write_loaddata_csv_by_batch_plate(
    images_df: pl.DataFrame,
    out_path: Path | CloudPath,
    path_mask: str,
    batch: str,
    plate: str,
) -> None:
    pass

    # Setup channel list for that plate
    plate_channel_list = get_channels_by_batch_plate(images_df, batch, plate)

    # setup df by filtering for plate id
    df_plate = images_df.filter(
        pl.col("batch_id").eq(batch) & pl.col("plate_id").eq(plate)
    )

    # Write load data csv for the plate
    batch_out_path = out_path.joinpath(batch)
    batch_out_path.mkdir(parents=True, exist_ok=True)
    with batch_out_path.joinpath(f"illum_calc_{batch}_{plate}.csv").open("w") as f:
        write_loaddata(df_plate, plate_channel_list, path_mask, f)


def write_loaddata_csv_by_batch_plate_cycle(
    images_df: pl.DataFrame,
    out_path: Path | CloudPath,
    path_mask: str,
    batch: str,
    plate: str,
    cycle: str,
) -> None:
    pass

    # Setup channel list for that plate
    plate_channel_list = get_channels_by_batch_plate(images_df, batch, plate)

    # setup df by filtering for plate id
    df_batch_plate_cycle = images_df.filter(
        pl.col("batch_id").eq(batch)
        & pl.col("plate_id").eq(plate)
        & pl.col("cycle_id").eq(cycle)
    )

    # Write load data csv for the plate
    batch_plate_out_path = out_path.joinpath(batch, plate)
    batch_plate_out_path.mkdir(parents=True, exist_ok=True)
    with batch_plate_out_path.joinpath(f"illum_calc_{batch}_{plate}_{cycle}.csv").open(
        "w"
    ) as f:
        write_loaddata(df_batch_plate_cycle, plate_channel_list, path_mask, f)


def gen_illum_calc_load_data_by_batch_plate(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    for_sbs: bool = False,
) -> None:
    """Generate load data for illum calc pipeline.

    Parameters
    ----------
    index_path : Path | CloudPath
        Path to index file.
    out_path : Path | CloudPath
        Path to save output csv file.
    path_mask : str | None
        Path prefix mask to use.
    for_sbs : str | None
        Generate illums for SBS images.

    """
    df = pl.read_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    if not for_sbs:
        images_df = df.filter(
            pl.col("is_sbs_image").ne(True), pl.col("is_image").eq(True)
        )
    else:
        images_df = df.filter(
            pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True)
        )

    images_hierarchy_dict = gen_image_hierarchy(images_df)

    # Query default path prefix
    default_path_prefix = images_df.select("prefix").unique().to_series().to_list()[0]

    # Setup path mask (required for resolving pathnames during the execution)
    if path_mask is None:
        path_mask = default_path_prefix

    # Setup chunking and write loaddata for each batch/plate
    for batch in images_hierarchy_dict.keys():
        for plate in images_hierarchy_dict[batch].keys():
            if not for_sbs:
                # Write loaddata assuming no image nesting with cycles
                write_loaddata_csv_by_batch_plate(
                    images_df, out_path, path_mask, batch, plate
                )
            else:
                # Write loaddata assuming image nesting with cycles
                plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)
                for cycle in plate_cycles_list:
                    write_loaddata_csv_by_batch_plate_cycle(
                        images_df, out_path, path_mask, batch, plate, cycle
                    )


###################################
## CellProfiler pipeline generation
###################################


def generate_illum_calculate_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
) -> Pipeline:
    load_data_df = pl.read_csv(load_data_path.resolve().__str__())
    channel_list = [
        col.split("_")[1] for col in load_data_df.columns if col.startswith("Frame")
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
    load_data.metadata_fields.value = "Plate"
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
        correct_illum_calculate.average_image_name.value = "IllumBlueAvg"
        correct_illum_calculate.save_dilated_image.value = False
        correct_illum_calculate.dilated_image_name.value = "IllumBlueDilated"
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
        save_image.single_file_name.value = f"\\g<Plate>_Illum{col}"
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


def gen_illum_calculate_cppipe_by_batch_plate(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
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

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)
    # Get all the generated load data files by batch
    batches = [batch.stem for batch in load_data_path.glob("*") if batch.is_dir()]
    files_by_batch = {
        batch: [file for file in load_data_path.joinpath(batch).glob("*.csv")]
        for batch in batches
    }

    # Generate cppipe file for each load data file

    for batch in batches:
        batch_out_dir = out_dir.joinpath(batch)
        batch_out_dir.mkdir(exist_ok=True, parents=True)
        for file in files_by_batch[batch]:
            with CellProfilerContext(out_dir=workspace_path) as cpipe:
                cpipe = generate_illum_calculate_pipeline(cpipe, file)
                filename = f"{file.stem}.cppipe"
                with batch_out_dir.joinpath(filename).open("w") as f:
                    cpipe.dump(f)
