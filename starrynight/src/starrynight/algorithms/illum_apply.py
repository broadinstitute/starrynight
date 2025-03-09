"""Illum Calculate commands."""

import csv
from io import TextIOWrapper
from pathlib import Path

import polars as pl
from cellprofiler.modules.correctilluminationapply import (
    DOS_DIVIDE,
    CorrectIlluminationApply,
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
from starrynight.utils.globbing import flatten_dict, get_files_by

###############################
## Load data generation
###############################


def write_loaddata(
    images_df: pl.DataFrame,
    plate_channel_list: list[str],
    illum_by_channel_dict: dict[str, Path],
    path_mask: str,
    f: TextIOWrapper,
) -> None:
    # setup csv headers and write the header first
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    metadata_heads = [
        f"Metadata_{col}" for col in ["Batch", "Plate", "Site", "Well", "Cycle"]
    ]
    filename_heads = [f"FileName_Orig{col}" for col in plate_channel_list]
    frame_heads = [f"Frame_Orig{col}" for col in plate_channel_list]
    pathname_heads = [f"PathName_Orig{col}" for col in plate_channel_list]
    # Add illum apply specific columns
    illum_pathname_heads = [f"PathName_Illum{col}" for col in plate_channel_list]
    # Assuming that paths already resolve with the path mask applied
    illum_pathname_values = [
        illum_by_channel_dict[ch].parent.resolve().__str__()
        for ch in plate_channel_list
    ]
    illum_filename_heads = [f"FileName_Illum{col}" for col in plate_channel_list]
    illum_filename_values = [
        illum_by_channel_dict[ch].name.__str__() for ch in plate_channel_list
    ]
    loaddata_writer.writerow(
        [
            *metadata_heads,
            *filename_heads,
            *frame_heads,
            *pathname_heads,
            *illum_filename_heads,
            *illum_pathname_heads,
        ]
    )
    for index in images_df.to_dicts():
        index = PCPIndex(**index)
        # make sure frame heads are matched with their order in the filenames
        frame_index = [
            index.channel_dict.index(channel.replace("Frame_Orig", ""))
            for channel in frame_heads
        ]
        assert index.key is not None
        loaddata_writer.writerow(
            [
                # Metadata heads
                index.batch_id,
                index.plate_id,
                index.site_id,
                index.well_id,
                index.cycle_id or 0,
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
                # Illum filename heads
                *illum_filename_values,
                # Illum Pathname heads
                *illum_pathname_values,
            ]
        )


def write_loaddata_csv_by_batch_plate(
    images_df: pl.DataFrame,
    out_path: Path | CloudPath,
    illum_path: Path | CloudPath,
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

    # find illum files for this plate
    illum_by_channel_dict = {
        ch: illum_path.joinpath(f"{batch}_{plate}_IllumOrig{ch}.npy")
        for ch in plate_channel_list
    }

    # Write load data csv for the plate
    batch_out_path = out_path.joinpath(batch)
    batch_out_path.mkdir(parents=True, exist_ok=True)
    with batch_out_path.joinpath(f"illum_apply_{batch}_{plate}.csv").open("w") as f:
        write_loaddata(
            df_plate, plate_channel_list, illum_by_channel_dict, path_mask, f
        )


def write_loaddata_csv_by_batch_plate_cycle(
    images_df: pl.DataFrame,
    out_path: Path | CloudPath,
    illum_path: Path | CloudPath,
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

    # find illum files for this plate and cycle
    illum_by_channel_dict = {
        ch: illum_path.joinpath(f"{batch}_{plate}_{int(cycle)}_IllumOrig{ch}.npy")
        for ch in plate_channel_list
    }

    # Write load data csv for the plate
    batch_plate_out_path = out_path.joinpath(batch, plate)
    batch_plate_out_path.mkdir(parents=True, exist_ok=True)
    with batch_plate_out_path.joinpath(
        f"illum_calc_{batch}_{plate}_{int(cycle):02}.csv"
    ).open("w") as f:
        write_loaddata(
            df_batch_plate_cycle,
            plate_channel_list,
            illum_by_channel_dict,
            path_mask,
            f,
        )


def gen_illum_apply_load_data_by_batch_plate(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    illum_path: Path | CloudPath | None = None,
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
    illum_path : Path | CloudPath
        Path | CloudPath to illum directory.
    for_sbs : str | None
        Generate illums for SBS images.

    """
    # Construct illum path if not given
    if illum_path is None and not for_sbs:
        illum_path = index_path.parents[1].joinpath("illum/cp/illum_calc")
    elif illum_path is None and for_sbs:
        illum_path = index_path.parents[1].joinpath("illum/sbs/illum_calc")
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
                    images_df, out_path, illum_path, path_mask, batch, plate
                )
            else:
                # Write loaddata assuming image nesting with cycles
                plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)
                for cycle in plate_cycles_list:
                    write_loaddata_csv_by_batch_plate_cycle(
                        images_df, out_path, illum_path, path_mask, batch, plate, cycle
                    )


###################################
## CellProfiler pipeline generation
###################################


def generate_illum_apply_pipeline(
    pipeline: Pipeline, load_data_path: Path | CloudPath, for_sbs: bool = False
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
    if not for_sbs:
        load_data.metadata_fields.value = "Batch,Plate"
    else:
        load_data.metadata_fields.value = "Batch,Plate,Cycle"
    load_data.rescale.value = True
    pipeline.add_module(load_data)

    correct_illum_apply = CorrectIlluminationApply()
    module_counter += 1
    correct_illum_apply.module_num = module_counter

    # INFO: Create and configure required modules
    # correct_illum_calculate -> save(corrected)
    for col in range(len(channel_list) - 1):  # One image is already added by default
        correct_illum_apply.add_image()

    for i, col in enumerate(channel_list):
        # image_name
        correct_illum_apply.images[i].settings[0].value = col
        # corrected_image_name
        correct_illum_apply.images[i].settings[1].value = col.replace("Orig", "Corr")
        # illum correct function image name
        correct_illum_apply.images[i].settings[2].value = col.replace("Orig", "Illum")
        # how illum function is applied
        correct_illum_apply.images[i].settings[3] = DOS_DIVIDE
    pipeline.add_module(correct_illum_apply)

    for col in channel_list:
        save_image = SaveImages()
        module_counter += 1
        save_image.module_num = module_counter
        save_image.save_image_or_figure.value = IF_IMAGE
        save_image.image_name.value = col.replace("Orig", "Corr")
        save_image.file_name_method.value = FN_SINGLE_NAME
        save_image.number_of_digits.value = 4
        save_image.wants_file_name_suffix.value = False
        save_image.file_name_suffix.value = ""
        save_image.file_format.value = FF_TIFF
        save_image.pathname.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
        save_image.bit_depth.value = BIT_DEPTH_16
        save_image.overwrite.value = False
        save_image.when_to_save.value = WS_EVERY_CYCLE
        save_image.update_file_names.value = False
        save_image.create_subdirectories.value = False
        # save_image.root_dir.value = ""
        save_image.stack_axis.value = AXIS_T
        # save_image.tiff_compress.value = ""

        if not for_sbs:
            save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_{col.replace('Orig', 'Corr')}"
        else:
            save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_\\g<Cycle>_Well_\\g<Well>_Site_\\g<Site>_{col.replace('Orig', 'Corr')}"
        pipeline.add_module(save_image)
    return pipeline


def gen_illum_apply_cppipe_by_batch_plate(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    for_sbs: bool = False,
) -> None:
    """Write out illumination apply pipeline to file.

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

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)

    # Get all the generated load data files by batch
    if not for_sbs:
        files_by_hierarchy = get_files_by(["batch"], load_data_path, "*.csv")
    else:
        files_by_hierarchy = get_files_by(["batch", "plate"], load_data_path, "*.csv")

    # flatten all the levels to reduce nested loops
    files_by_hierarchy_flatten = flatten_dict(files_by_hierarchy)
    for hierarchy, files in files_by_hierarchy_flatten:
        files_out_dir = out_dir.joinpath(*hierarchy)
        files_out_dir.mkdir(exist_ok=True, parents=True)
        for file in files:
            with CellProfilerContext(out_dir=workspace_path) as cpipe:
                cpipe = generate_illum_apply_pipeline(cpipe, file, for_sbs)
                filename = f"{file.stem}.cppipe"
                with files_out_dir.joinpath(filename).open("w") as f:
                    cpipe.dump(f)
