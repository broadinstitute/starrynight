"""Pre seg check commands."""

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
from cellprofiler.modules.identifyprimaryobjects import (
    DEFAULT_MAXIMA_COLOR,
    FH_DECLUMP,
    LIMIT_NONE,
    UN_INTENSITY,
    UN_SHAPE,
    WA_NONE,
    WA_SHAPE,
    IdentifyPrimaryObjects,
)
from cellprofiler.modules.identifysecondaryobjects import (
    M_WATERSHED_I,
    IdentifySecondaryObjects,
)
from cellprofiler.modules.maskimage import MaskImage
from cellprofiler.modules.threshold import (
    O_BACKGROUND,
    O_FOREGROUND,
    O_THREE_CLASS,
    O_TWO_CLASS,
    RB_MEAN,
    RB_SD,
    TM_OTSU,
    TS_GLOBAL,
)
from cellprofiler_core.constants.modules.load_data import (
    ABSOLUTE_FOLDER_NAME,
    DEFAULT_OUTPUT_FOLDER_NAME,
    NO_FOLDER_NAME,
)
from cellprofiler_core.modules.loaddata import LoadData
from cellprofiler_core.pipeline import Pipeline
from cloudpathlib import AnyPath, CloudPath

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
    plate_channel_list: list[str],
    corr_images_path: Path | CloudPath,
    path_mask: str,
    f: TextIOWrapper,
) -> None:
    # setup csv headers and write the header first
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    metadata_heads = [
        f"Metadata_{col}" for col in ["Batch", "Plate", "Site", "Well", "Cycle"]
    ]
    filename_heads = [f"FileName_Corr{col}" for col in plate_channel_list]
    pathname_heads = [f"PathName_Corr{col}" for col in plate_channel_list]
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
            f"{index.batch_id}_{index.plate_id}_Well_{index.well_id}_Site_{int(index.site_id)}_Corr{col}.tiff"
            for col in plate_channel_list
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
                index.cycle_id or 0,
                # Filename heads
                *filenames,
                # Pathname heads
                *pathnames,
            ]
        )


def write_loaddata_csv_by_batch_plate(
    images_df: pl.DataFrame,
    out_path: Path | CloudPath,
    corr_images_path: Path | CloudPath,
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
    with batch_out_path.joinpath(f"pre_segcheck_{batch}_{plate}.csv").open("w") as f:
        write_loaddata(df_plate, plate_channel_list, corr_images_path, path_mask, f)


def write_loaddata_csv_by_batch_plate_cycle(
    images_df: pl.DataFrame,
    out_path: Path | CloudPath,
    corr_images_path: Path | CloudPath,
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
    with batch_plate_out_path.joinpath(
        f"pre_segcheck_{batch}_{plate}_{int(cycle):02}.csv"
    ).open("w") as f:
        write_loaddata(
            df_batch_plate_cycle,
            plate_channel_list,
            corr_images_path,
            path_mask,
            f,
        )


def gen_pre_segcheck_load_data_by_batch_plate(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    corr_images_path: Path | CloudPath | None = None,
    for_sbs: bool = False,
) -> None:
    """Generate load data for pre-segcheck pipeline.

    Parameters
    ----------
    index_path : Path | CloudPath
        Path to index file.
    out_path : Path | CloudPath
        Path to save output csv file.
    path_mask : str | None
        Path prefix mask to use.
    corr_images_path : Path | CloudPath
        Path | CloudPath to corr images directory.
    for_sbs : str | None
        Generate illums for SBS images.

    """
    # Construct illum path if not given
    if corr_images_path is None and not for_sbs:
        corr_images_path = index_path.parents[1].joinpath("illum/cp/illum_apply")
    elif corr_images_path is None and for_sbs:
        corr_images_path = index_path.parents[1].joinpath("illum/sbs/illum_apply")
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

    # Only subsample if df is large
    if len(images_df) > 10:
        images_df = images_df.sample(fraction=0.1)

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
                    images_df, out_path, corr_images_path, path_mask, batch, plate
                )
            else:
                # Write loaddata assuming image nesting with cycles
                plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)
                for cycle in plate_cycles_list:
                    write_loaddata_csv_by_batch_plate_cycle(
                        images_df,
                        out_path,
                        corr_images_path,
                        path_mask,
                        batch,
                        plate,
                        cycle,
                    )


###################################
## CellProfiler pipeline generation
###################################


def generate_pre_segcheck_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
    for_sbs: bool = False,
) -> Pipeline:
    load_data_df = pl.read_csv(load_data_path.resolve().__str__())
    channel_list = list(
        set(
            [
                col.split("_")[1].replace("Corr", "")
                for col in load_data_df.columns
                if col.startswith("FileName")
            ]
        )
    )
    channel_list.sort()
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
    # identifyPrimaryObject(confluent regions) -> mask -> identifyPrimaryObject(nuclei)
    # -> identifySecondaryObject(cells) -> ExportToSpreadSheet

    # Confluent regions identification
    identify_primary_object_cfregions = IdentifyPrimaryObjects()
    module_counter += 1
    identify_primary_object_cfregions.module_num = module_counter
    identify_primary_object_cfregions.x_name.value = f"Corr{nuclei_channel}"
    identify_primary_object_cfregions.y_name.value = "ConfluentRegions"
    identify_primary_object_cfregions.size_range.value = (500, 5000)
    identify_primary_object_cfregions.exclude_size.value = True
    identify_primary_object_cfregions.exclude_border_objects.value = False
    identify_primary_object_cfregions.unclump_method.value = UN_INTENSITY
    identify_primary_object_cfregions.watershed_method.value = WA_NONE
    identify_primary_object_cfregions.automatic_smoothing.value = True
    identify_primary_object_cfregions.smoothing_filter_size.value = 10
    identify_primary_object_cfregions.automatic_suppression.value = True
    identify_primary_object_cfregions.maxima_suppression_size.value = 7.0
    identify_primary_object_cfregions.low_res_maxima.value = True
    identify_primary_object_cfregions.fill_holes.value = FH_DECLUMP
    identify_primary_object_cfregions.limit_choice.value = LIMIT_NONE
    identify_primary_object_cfregions.maximum_object_count.value = 500
    identify_primary_object_cfregions.want_plot_maxima.value = True
    identify_primary_object_cfregions.maxima_color.value = DEFAULT_MAXIMA_COLOR
    identify_primary_object_cfregions.use_advanced.value = True
    identify_primary_object_cfregions.threshold_setting_version.value = 12
    identify_primary_object_cfregions.threshold.threshold_scope.value = TS_GLOBAL
    identify_primary_object_cfregions.threshold.global_operation.value = TM_OTSU
    identify_primary_object_cfregions.threshold.local_operation.value = TM_OTSU
    identify_primary_object_cfregions.threshold.threshold_smoothing_scale.value = 2.0
    identify_primary_object_cfregions.threshold.threshold_correction_factor.value = 0.5
    identify_primary_object_cfregions.threshold.threshold_range.value = (0.0, 1.0)
    identify_primary_object_cfregions.threshold.manual_threshold.value = 0.0
    identify_primary_object_cfregions.threshold.thresholding_measurement.value = None
    identify_primary_object_cfregions.threshold.two_class_otsu.value = O_TWO_CLASS
    identify_primary_object_cfregions.threshold.assign_middle_to_foreground.value = (
        O_FOREGROUND
    )
    identify_primary_object_cfregions.threshold.lower_outlier_fraction.value = 0.05
    identify_primary_object_cfregions.threshold.upper_outlier_fraction.value = 0.05
    identify_primary_object_cfregions.threshold.averaging_method.value = RB_MEAN
    identify_primary_object_cfregions.threshold.variance_method.value = RB_SD
    identify_primary_object_cfregions.threshold.number_of_deviations.value = 2.0
    identify_primary_object_cfregions.threshold.adaptive_window_size.value = 50
    identify_primary_object_cfregions.threshold.log_transform.value = False
    pipeline.add_module(identify_primary_object_cfregions)

    # Masking confluentRegions in all channels
    for ch in channel_list:
        mask_image_cfregion = MaskImage()
        module_counter += 1
        mask_image_cfregion.module_num = module_counter
        mask_image_cfregion.image_name.value = f"Corr{nuclei_channel}"
        mask_image_cfregion.masked_image_name.value = f"Masked{ch}"
        mask_image_cfregion.object_name.value = "ConfluentRegions"
        mask_image_cfregion.invert_mask.value = True
        pipeline.add_module(mask_image_cfregion)

    # identify nuclei with dna channel
    identify_primary_object_nuclei = IdentifyPrimaryObjects()
    module_counter += 1
    identify_primary_object_nuclei.module_num = module_counter
    identify_primary_object_nuclei.x_name.value = f"Corr{nuclei_channel}"
    identify_primary_object_nuclei.y_name.value = "Nuclei"
    identify_primary_object_nuclei.size_range.value = (10, 80)
    identify_primary_object_nuclei.exclude_size.value = True
    identify_primary_object_nuclei.exclude_border_objects.value = True
    identify_primary_object_nuclei.unclump_method.value = UN_SHAPE
    identify_primary_object_nuclei.watershed_method.value = WA_SHAPE
    identify_primary_object_nuclei.automatic_smoothing.value = False
    identify_primary_object_nuclei.smoothing_filter_size.value = 8
    identify_primary_object_nuclei.automatic_suppression.value = False
    identify_primary_object_nuclei.maxima_suppression_size.value = 8.0
    identify_primary_object_nuclei.low_res_maxima.value = True
    identify_primary_object_nuclei.fill_holes.value = FH_DECLUMP
    identify_primary_object_nuclei.limit_choice.value = LIMIT_NONE
    identify_primary_object_nuclei.maximum_object_count.value = 500
    identify_primary_object_nuclei.want_plot_maxima.value = False
    identify_primary_object_nuclei.maxima_color.value = DEFAULT_MAXIMA_COLOR
    identify_primary_object_nuclei.use_advanced.value = True
    identify_primary_object_nuclei.threshold_setting_version.value = 12
    identify_primary_object_nuclei.threshold.threshold_scope.value = TS_GLOBAL
    identify_primary_object_nuclei.threshold.global_operation.value = TM_OTSU
    identify_primary_object_nuclei.threshold.local_operation.value = TM_OTSU
    identify_primary_object_nuclei.threshold.threshold_smoothing_scale.value = 1.3488
    identify_primary_object_nuclei.threshold.threshold_correction_factor.value = 1.0
    identify_primary_object_nuclei.threshold.threshold_range.value = (0.0, 1.0)
    identify_primary_object_nuclei.threshold.manual_threshold.value = 0.0
    identify_primary_object_nuclei.threshold.thresholding_measurement.value = None
    identify_primary_object_nuclei.threshold.two_class_otsu.value = O_TWO_CLASS
    identify_primary_object_nuclei.threshold.assign_middle_to_foreground.value = (
        O_FOREGROUND
    )
    identify_primary_object_nuclei.threshold.lower_outlier_fraction.value = 0.05
    identify_primary_object_nuclei.threshold.upper_outlier_fraction.value = 0.05
    identify_primary_object_nuclei.threshold.averaging_method.value = RB_MEAN
    identify_primary_object_nuclei.threshold.variance_method.value = RB_SD
    identify_primary_object_nuclei.threshold.number_of_deviations.value = 2.0
    identify_primary_object_nuclei.threshold.adaptive_window_size.value = 50
    identify_primary_object_nuclei.threshold.log_transform.value = False
    pipeline.add_module(identify_primary_object_nuclei)

    # identify cells
    identify_secondary_object_cells = IdentifySecondaryObjects()
    module_counter += 1
    identify_secondary_object_cells.module_num = module_counter
    identify_secondary_object_cells.x_name.value = "Nuclei"
    identify_secondary_object_cells.y_name.value = "Cells"
    identify_secondary_object_cells.method.value = M_WATERSHED_I
    identify_secondary_object_cells.image_name.value = f"Masked{cell_channel}"
    identify_secondary_object_cells.distance_to_dilate.value = 10
    identify_secondary_object_cells.regularization_factor.value = 0.05
    identify_secondary_object_cells.wants_discard_edge.value = False
    identify_secondary_object_cells.wants_discard_primary.value = False
    identify_secondary_object_cells.fill_holes.value = False
    identify_secondary_object_cells.new_primary_objects_name.value = "FilteredNuclei"
    identify_secondary_object_cells.threshold_setting_version.value = 12
    identify_secondary_object_cells.threshold.threshold_scope.value = TS_GLOBAL
    identify_secondary_object_cells.threshold.global_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.local_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.threshold_smoothing_scale.value = 2.0
    identify_secondary_object_cells.threshold.threshold_correction_factor.value = 0.7
    identify_secondary_object_cells.threshold.threshold_range.value = (0.0005, 1.0)
    identify_secondary_object_cells.threshold.manual_threshold.value = 0.0
    identify_secondary_object_cells.threshold.thresholding_measurement.value = None
    identify_secondary_object_cells.threshold.two_class_otsu.value = O_THREE_CLASS
    identify_secondary_object_cells.threshold.assign_middle_to_foreground.value = (
        O_BACKGROUND
    )
    identify_secondary_object_cells.threshold.lower_outlier_fraction.value = 0.05
    identify_secondary_object_cells.threshold.upper_outlier_fraction.value = 0.05
    identify_secondary_object_cells.threshold.averaging_method.value = RB_MEAN
    identify_secondary_object_cells.threshold.variance_method.value = RB_SD
    identify_secondary_object_cells.threshold.number_of_deviations.value = 2.0
    identify_secondary_object_cells.threshold.adaptive_window_size.value = 50
    identify_secondary_object_cells.threshold.log_transform.value = False
    pipeline.add_module(identify_secondary_object_cells)

    # export measurements to spreadsheet
    export_measurements = ExportToSpreadsheet()
    module_counter += 1
    export_measurements.module_num = module_counter
    export_measurements.delimiter.value = DELIMITER_COMMA
    export_measurements.directory.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
    export_measurements.wants_prefix.value = True
    if not for_sbs:
        export_measurements.prefix.value = "PreSegcheck_"
    else:
        export_measurements.prefix.value = "PreSegcheck_"
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


def gen_pre_segcheck_cppipe_by_batch_plate(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
    for_sbs: bool = False,
) -> None:
    """Write out pre_segcheck pipeline to file.

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
    cell_channel : str
        Channel to use for cell segmentation
    for_sbs : bool
        Generate illums for SBS images.

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)

    # Get all the generated load data files by batch
    if not for_sbs:
        type_suffix = "painting"
        files_by_hierarchy = get_files_by(["batch"], load_data_path, "*.csv")
    else:
        type_suffix = "sbs"
        files_by_hierarchy = get_files_by(["batch", "plate"], load_data_path, "*.csv")

    # get one of the load data file for generating cppipe
    _, files = flatten_dict(files_by_hierarchy)[0]
    with CellProfilerContext(out_dir=workspace_path) as cpipe:
        cpipe = generate_pre_segcheck_pipeline(
            cpipe, files[0], nuclei_channel, cell_channel, for_sbs
        )
        filename = f"presegcheck_{type_suffix}.cppipe"
        with out_dir.joinpath(filename).open("w") as f:
            cpipe.dump(f)
