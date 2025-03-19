"""Alignment commands."""

import csv
from io import TextIOWrapper
from pathlib import Path

import polars as pl
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
from cloudpathlib import AnyPath, CloudPath
from numpy import exp

from starrynight.algorithms.index import PCPIndex
from starrynight.utils.cellprofiler import CellProfilerContext
from starrynight.utils.dfutils import (
    gen_image_hierarchy,
    get_channels_by_batch_plate,
    get_cycles_by_batch_plate,
)
from starrynight.utils.globbing import flatten_dict, get_files_by
from starrynight.utils.misc import resolve_path_loaddata

###############################
## Load data generation
###############################


def write_loaddata(
    images_df: pl.DataFrame,
    plate_cycles_list: list[str],
    plate_channel_list: list[str],
    corr_images_path: Path | CloudPath,
    nuclei_channel: str,
    path_mask: str,
    f: TextIOWrapper,
) -> None:
    # setup csv headers and write the header first
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    metadata_heads = [f"Metadata_{col}" for col in ["Batch", "Plate", "Site", "Well"]]

    filename_heads = [
        f"FileName_Corr_Cycle_{int(cycle)}_{col}"
        for col in plate_channel_list
        for cycle in plate_cycles_list
    ]
    pathname_heads = [
        f"PathName_Corr_Cycle_{int(cycle)}_{col}"
        for col in plate_channel_list
        for cycle in plate_cycles_list
    ]
    loaddata_writer.writerow(
        [
            *metadata_heads,
            *filename_heads,
            *pathname_heads,
        ]
    )
    for index in images_df.to_dicts():
        index = PCPIndex(**index)
        filenames = [
            f"{index.batch_id}_{index.plate_id}_{int(cycle)}_Well_{index.well_id}_Site_{int(index.site_id)}_Corr{col}.tiff"
            for col in plate_channel_list
            for cycle in plate_cycles_list
        ]
        pathnames = [
            resolve_path_loaddata(AnyPath(path_mask), corr_images_path)
            for _ in range(len(pathname_heads))
        ]

        # make sure frame heads are matched with their order in the filenames
        assert index.key is not None
        loaddata_writer.writerow(
            [
                # Metadata heads
                index.batch_id,
                index.plate_id,
                index.site_id,
                index.well_id,
                # Filename heads
                *filenames,
                # Pathname heads
                *pathnames,
            ]
        )


def write_loaddata_csv_by_batch_plate_cycle(
    images_df: pl.DataFrame,
    out_path: Path | CloudPath,
    corr_images_path: Path | CloudPath,
    nuclei_channel: str,
    path_mask: str,
    batch: str,
    plate: str,
) -> None:
    pass

    # Setup cycles list
    plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)
    # Setup channel list for that plate
    plate_channel_list = get_channels_by_batch_plate(images_df, batch, plate)

    # setup df by filtering for batch id and plate id
    df_batch_plate_cycle = images_df.filter(
        pl.col("batch_id").eq(batch) & pl.col("plate_id").eq(plate)
    )

    # Write load data csv for the plate
    batch_plate_out_path = out_path.joinpath(batch, plate)
    batch_plate_out_path.mkdir(parents=True, exist_ok=True)
    with batch_plate_out_path.joinpath(f"align_{batch}_{plate}.csv").open("w") as f:
        write_loaddata(
            df_batch_plate_cycle,
            plate_cycles_list,
            plate_channel_list,
            corr_images_path,
            nuclei_channel,
            path_mask,
            f,
        )


def gen_align_load_data_by_batch_plate(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    nuclei_channel: str,
    corr_images_path: Path | CloudPath | None = None,
) -> None:
    """Generate load data for segcheck pipeline.

    Parameters
    ----------
    index_path : Path | CloudPath
        Path to index file.
    out_path : Path | CloudPath
        Path to save output csv file.
    path_mask : str | None
        Path prefix mask to use.
    nuclei_channel: str
        Channel to use for doing nuclei segmentation
    corr_images_path : Path | CloudPath
        Path | CloudPath to corr images directory.

    """
    # Construct illum path if not given
    if corr_images_path is None:
        corr_images_path = index_path.parents[1].joinpath("illum/sbs/illum_apply")

    df = pl.read_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    images_df = df.filter(pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True))

    images_hierarchy_dict = gen_image_hierarchy(images_df)

    # Query default path prefix
    default_path_prefix = images_df.select("prefix").unique().to_series().to_list()[0]

    # Setup path mask (required for resolving pathnames during the execution)
    if path_mask is None:
        path_mask = default_path_prefix

    # Setup chunking and write loaddata for each batch/plate
    for batch in images_hierarchy_dict.keys():
        for plate in images_hierarchy_dict[batch].keys():
            write_loaddata_csv_by_batch_plate_cycle(
                images_df,
                out_path,
                corr_images_path,
                nuclei_channel,
                path_mask,
                batch,
                plate,
            )


###################################
## CellProfiler pipeline generation
###################################


def generate_align_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
    nuclei_channel: str,
) -> Pipeline:
    load_data_df = pl.read_csv(load_data_path.resolve().__str__())
    channel_list = list(
        set(
            [
                col.split("_")[-1]
                for col in load_data_df.columns
                if col.startswith("FileName")
            ]
        )
    )
    channel_list.sort()

    cycle_list = list(
        set(
            [
                col.split("_")[-2]
                for col in load_data_df.columns
                if col.startswith("FileName")
            ]
        )
    )
    cycle_list.sort()

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
    load_data.metadata_fields.value = "Batch,Plate"
    load_data.rescale.value = True
    pipeline.add_module(load_data)

    # INFO: Create and configure required modules
    # Align(to cycle 1 nuclei channel) -> MeasureColocalization -> FlagImage
    # -> save(aligned images) -> ExportToSpreadsheet

    for cycle in cycle_list:
        align = Align()
        module_counter += 1
        align.module_num = module_counter
        align.alignment_method.value = M_CROSS_CORRELATION
        align.crop_mode.value = C_SAME_SIZE

        # make a copy of channel list and remove nuclei_channel
        align_channel_list = channel_list.copy()
        align_channel_list.remove(nuclei_channel)
        align.first_input_image.value = f"Corr_Cycle_1_{nuclei_channel}"
        align.first_output_image.value = f"Aligned_Corr_Cycle_1_{nuclei_channel}"
        align.second_input_image.value = f"Corr_Cycle_{cycle}_{nuclei_channel}"
        align.second_output_image.value = f"Aligned_Corr_Cycle_{cycle}_{nuclei_channel}"

        for i, ch in enumerate(align_channel_list):
            align.add_image()
            # input_image_name
            align.additional_images[i].settings[1].value = f"Corr_Cycle_{cycle}_{ch}"
            # output_image_name
            align.additional_images[i].settings[
                2
            ].value = f"Aligned_Corr_Cycle_{cycle}_{ch}"
            # align_choice
            align.additional_images[i].settings[3].value = A_SIMILARLY
        pipeline.add_module(align)

    # MeasureColocalization sbs
    measure_colocal_sbs = MeasureColocalization()
    module_counter += 1
    measure_colocal_sbs.module_num = module_counter
    measure_colocal_sbs.images_list.value = ",".join(
        [f"Corr_Cycle_{cycle}_{ch}" for ch in channel_list for cycle in cycle_list]
    )
    measure_colocal_sbs.thr.value = 15.0
    measure_colocal_sbs.images_or_objects.value = M_IMAGES
    measure_colocal_sbs.objects_list.value = ""
    measure_colocal_sbs.do_all.value = False
    measure_colocal_sbs.do_corr_and_slope.value = True
    measure_colocal_sbs.do_manders.value = False
    measure_colocal_sbs.do_rwc.value = False
    measure_colocal_sbs.do_overlap.value = True
    measure_colocal_sbs.do_costes.value = False
    measure_colocal_sbs.fast_costes.value = M_ACCURATE
    pipeline.add_module(measure_colocal_sbs)

    # -> FlagImage (Unaligned)
    flag_unaligned = FlagImage()
    module_counter += 1
    flag_unaligned.module_num = module_counter

    images_to_flag = [f"Corr_Cycle_{cycle}_{nuclei_channel}" for cycle in cycle_list]
    # One flag is already created
    for _ in range(len(images_to_flag) - 1):
        flag_unaligned.add_flag()

    for i, flag_image in enumerate(images_to_flag):
        # Flag's category [3]
        flag_unaligned.flags[i].category.value = "Metadata"
        # Name of the flag [4]
        flag_unaligned.flags[i].feature_name.value = "Unaligned"
        # How should the measurements be linked [5]
        flag_unaligned.flags[i].combination_choice.value = C_ANY
        # Skip image set if flagged [6]
        flag_unaligned.flags[i].wants_skip.value = False

        # Measurement settings, One measurement is added by default for each flag
        flag_unaligned.flags[i].measurement_settings[0].source_choice.value = S_IMAGE
        flag_unaligned.flags[i].measurement_settings[0].object_name.value = None
        flag_unaligned.flags[i].measurement_settings[
            0
        ].measurement.value = (
            f"Correlation_Correlation_Corr_Cycle_1_{nuclei_channel}_{flag_image}"
        )
        flag_unaligned.flags[i].measurement_settings[0].wants_minimum.value = True
        flag_unaligned.flags[i].measurement_settings[0].minimum_value.value = 0.9
        flag_unaligned.flags[i].measurement_settings[0].wants_maximum.value = False
    pipeline.add_module(flag_unaligned)

    # Save image (combined overlay)
    for cycle in cycle:
        for ch in channel_list:
            save_image = SaveImages()
            module_counter += 1
            save_image.module_num = module_counter
            save_image.save_image_or_figure.value = IF_IMAGE
            save_image.image_name.value = f"Aligned_Corr_Cycle_{cycle}_{ch}"
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
            save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_\\{cycle}_Well_\\g<Well>_Site_\\g<Site>_Aligned{ch}"
            pipeline.add_module(save_image)

    # export measurements to spreadsheet
    export_measurements = ExportToSpreadsheet()
    module_counter += 1
    export_measurements.module_num = module_counter
    export_measurements.delimiter.value = DELIMITER_COMMA
    export_measurements.directory.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
    export_measurements.wants_prefix.value = True
    export_measurements.prefix.value = "Align_"
    export_measurements.wants_overwrite_without_warning.value = False
    export_measurements.add_metadata.value = False
    export_measurements.add_filepath.value = False
    export_measurements.nan_representation.value = NANS_AS_NANS
    export_measurements.pick_columns.value = False
    export_measurements.wants_aggregate_means.value = False
    export_measurements.wants_aggregate_medians.value = False
    export_measurements.wants_aggregate_std.value = False
    export_measurements.wants_genepattern_file.value = False
    export_measurements.how_to_specify_gene_name.value = GP_NAME_METADATA
    export_measurements.gene_name_column.value = None
    export_measurements.use_which_image_for_gene_name.value = None
    export_measurements.wants_everything.value = True

    pipeline.add_module(export_measurements)

    return pipeline


def gen_align_cppipe_by_batch_plate(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    nuclei_channel: str,
) -> None:
    """Write out segcheck pipeline to file.

    Parameters
    ----------
    load_data_path : Path | CloudPath
        Path | CloudPath to load data csv dir.
    out_dir : Path | CloudPath
        Path | CloudPath to output directory.
    workspace_path : Path | CloudPath
        Path | CloudPath to workspace directory.
    nuclei_channel : str
        Channel to use for nuclei segmentation

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)

    # Get all the generated load data files by batch
    files_by_hierarchy = get_files_by(["batch", "plate"], load_data_path, "*.csv")

    # flatten all the levels to reduce nested loops
    files_by_hierarchy_flatten = flatten_dict(files_by_hierarchy)
    for hierarchy, files in files_by_hierarchy_flatten:
        files_out_dir = out_dir.joinpath(*hierarchy)
        files_out_dir.mkdir(exist_ok=True, parents=True)
        for file in files:
            with CellProfilerContext(out_dir=workspace_path) as cpipe:
                cpipe = generate_align_pipeline(cpipe, file, nuclei_channel)
                filename = f"{file.stem}.cppipe"
                with files_out_dir.joinpath(filename).open("w") as f:
                    cpipe.dump(f)
