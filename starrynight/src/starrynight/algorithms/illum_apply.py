"""Illum Calculate commands."""

import csv
from io import TextIOWrapper
from pathlib import Path

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
from cellprofiler.modules.saveimages import (
    AXIS_T,
    BIT_DEPTH_16,
    FF_TIFF,
    FN_SINGLE_NAME,
    IF_IMAGE,
    WS_EVERY_CYCLE,
    SaveImages,
)
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
from cellprofiler_core.pipeline.io import dump as dumpit
from cellprofiler_core.preferences import json
from cloudpathlib import AnyPath, CloudPath

from starrynight.algorithms.index import PCPIndex
from starrynight.modules.cp_illum_calc.constants import (
    CP_ILLUM_CALC_OUT_PATH_SUFFIX,
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
    get_default_path_prefix,
)
from starrynight.utils.globbing import flatten_all, flatten_dict, get_files_by

###############################
## Load data generation
###############################


def write_loaddata_illum_apply(
    images_df: pl.LazyFrame,
    plate_channel_list: list[str],
    illum_by_channel_dict: dict[str, Path],
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

        # Adapt channel names in all the required lists
        plate_channel_list = [
            legacy_channel_map[ch] for ch in plate_channel_list
        ]

        illum_by_channel_dict = {
            legacy_channel_map[ch]: AnyPath(
                str(v.resolve()).replace(ch, legacy_channel_map[ch])
            )
            for ch, v in illum_by_channel_dict.items()
        }

    # Setup FileName, PathName and FrameName headers
    filename_heads = [f"FileName_Orig{ch}" for ch in plate_channel_list]
    frame_heads = [f"Frame_Orig{ch}" for ch in plate_channel_list]
    pathname_heads = [f"PathName_Orig{ch}" for ch in plate_channel_list]

    # Add illum apply specific columns
    illum_pathname_heads = [f"PathName_Illum{ch}" for ch in plate_channel_list]
    # Assuming that paths already resolve with the path mask applied
    illum_pathname_values = [
        illum_by_channel_dict[ch].parent.resolve().__str__()
        for ch in plate_channel_list
    ]
    illum_filename_heads = [f"FileName_Illum{ch}" for ch in plate_channel_list]
    illum_filename_values = [
        illum_by_channel_dict[ch].name.__str__() for ch in plate_channel_list
    ]

    # Write the headers first
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


def gen_illum_apply_load_data(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    illum_path: Path | CloudPath | None = None,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
    uow_hierarchy: list[str] | None = None,
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
    use_legacy : bool
        Use legacy cppipe and loaddata.
    exp_config_path : Path | CloudPath
        Path to experiment config json path.
    uow_hierarchy : list[str] | None
        Unit of work list

    """
    # Construct illum path if not given
    if not illum_path:
        illum_path = index_path.parents[1].joinpath(
            CP_ILLUM_CALC_OUT_PATH_SUFFIX
        )

    # Load index
    df = pl.scan_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    images_df = filter_images(df, False)

    # Query default path prefix
    default_path_prefix: str = get_default_path_prefix(images_df)

    # Setup path mask (required for resolving pathnames during the execution)
    if path_mask is None:
        path_mask = default_path_prefix

    # Setup chunking and write loaddata for parallel processing
    uow_hierarchy = uow_hierarchy or [
        "batch_id",
        "plate_id",
        "well_id",
        "site_id",
    ]
    images_hierarchy_dict = gen_image_hierarchy(images_df, uow_hierarchy)
    levels = flatten_all(images_hierarchy_dict)
    for level in levels:
        # setup filtered df for chunked levels
        level_df = filter_df_by_hierarchy(images_df, level, False)

        # Setup channel list for this level
        plate_channel_list = get_channels_from_df(level_df)

        # Find illum files for this level
        illum_by_channel_dict = {
            ch: illum_path.joinpath(
                # INFO: This is not optimal, output form previous step is calculated per plate
                # INFO: So, level[:2] is used and not just levels
                f"{'-'.join(level[:2])}/{level[1]}_Illum{ch}.npy"
            )
            for ch in plate_channel_list
        }

        # Construct filename for the loaddata csv
        level_out_path = out_path.joinpath(f"{'^'.join(level)}#illum_apply.csv")

        with level_out_path.open("w") as f:
            write_loaddata_illum_apply(
                level_df,
                plate_channel_list,
                illum_by_channel_dict,
                path_mask,
                f,
                use_legacy,
                exp_config_path,
            )
    return out_path


###################################
## CellProfiler pipeline generation
###################################


def generate_illum_apply_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
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
    load_data.metadata_fields.value = "Batch,Plate"
    load_data.rescale.value = True
    pipeline.add_module(load_data)

    # INFO: Create and configure required modules
    # correct_illum_calculate -> save(corrected)
    correct_illum_apply = CorrectIlluminationApply()
    module_counter += 1
    correct_illum_apply.module_num = module_counter

    for col in range(
        len(channel_list) - 1
    ):  # One image is already added by default
        correct_illum_apply.add_image()

    for i, col in enumerate(channel_list):
        # image_name
        correct_illum_apply.images[i].settings[0].value = col
        # corrected_image_name
        correct_illum_apply.images[i].settings[1].value = col.replace(
            "Orig", "Corr"
        )
        # illum correct function image name
        correct_illum_apply.images[i].settings[2].value = col.replace(
            "Orig", "Illum"
        )
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
        save_image.single_file_name.value = f"Plate_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_{col.replace('Orig', 'Corr')}"
        pipeline.add_module(save_image)

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
    identify_primary_object_cfregions.threshold.threshold_scope.value = (
        TS_GLOBAL
    )
    identify_primary_object_cfregions.threshold.global_operation.value = TM_OTSU
    identify_primary_object_cfregions.threshold.local_operation.value = TM_OTSU
    identify_primary_object_cfregions.threshold.threshold_smoothing_scale.value = 2.0
    identify_primary_object_cfregions.threshold.threshold_correction_factor.value = 0.5
    identify_primary_object_cfregions.threshold.threshold_range.value = (
        0.0,
        1.0,
    )
    identify_primary_object_cfregions.threshold.manual_threshold.value = 0.0
    identify_primary_object_cfregions.threshold.thresholding_measurement.value = None
    identify_primary_object_cfregions.threshold.two_class_otsu.value = (
        O_TWO_CLASS
    )
    identify_primary_object_cfregions.threshold.assign_middle_to_foreground.value = O_FOREGROUND
    identify_primary_object_cfregions.threshold.lower_outlier_fraction.value = (
        0.05
    )
    identify_primary_object_cfregions.threshold.upper_outlier_fraction.value = (
        0.05
    )
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
    identify_primary_object_nuclei.threshold.threshold_smoothing_scale.value = (
        1.3488
    )
    identify_primary_object_nuclei.threshold.threshold_correction_factor.value = 1.0
    identify_primary_object_nuclei.threshold.threshold_range.value = (0.0, 1.0)
    identify_primary_object_nuclei.threshold.manual_threshold.value = 0.0
    identify_primary_object_nuclei.threshold.thresholding_measurement.value = (
        None
    )
    identify_primary_object_nuclei.threshold.two_class_otsu.value = O_TWO_CLASS
    identify_primary_object_nuclei.threshold.assign_middle_to_foreground.value = O_FOREGROUND
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
    identify_secondary_object_cells.image_name.value = (
        f"MaskedOrig{cell_channel}"
    )
    identify_secondary_object_cells.distance_to_dilate.value = 10
    identify_secondary_object_cells.regularization_factor.value = 0.05
    identify_secondary_object_cells.wants_discard_edge.value = False
    identify_secondary_object_cells.wants_discard_primary.value = False
    identify_secondary_object_cells.fill_holes.value = False
    identify_secondary_object_cells.new_primary_objects_name.value = (
        "FilteredNuclei"
    )
    identify_secondary_object_cells.threshold_setting_version.value = 12
    identify_secondary_object_cells.threshold.threshold_scope.value = TS_GLOBAL
    identify_secondary_object_cells.threshold.global_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.local_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.threshold_smoothing_scale.value = 2.0
    identify_secondary_object_cells.threshold.threshold_correction_factor.value = 0.7
    identify_secondary_object_cells.threshold.threshold_range.value = (
        0.0005,
        1.0,
    )
    identify_secondary_object_cells.threshold.manual_threshold.value = 0.0
    identify_secondary_object_cells.threshold.thresholding_measurement.value = (
        None
    )
    identify_secondary_object_cells.threshold.two_class_otsu.value = (
        O_THREE_CLASS
    )
    identify_secondary_object_cells.threshold.assign_middle_to_foreground.value = O_BACKGROUND
    identify_secondary_object_cells.threshold.lower_outlier_fraction.value = (
        0.05
    )
    identify_secondary_object_cells.threshold.upper_outlier_fraction.value = (
        0.05
    )
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


def gen_illum_apply_cppipe(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
    use_legacy: bool = False,
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
    nuclei_channel : str
        Channel to use for nuclei segmentation
    cell_channel : str
        Channel to use for cell segmentation
    use_legacy : str | None
        Use legacy illumination apply pipeline.

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)

    filename = "illum_apply_painting.cppipe"

    # Write old cppipe and return early if use_old is true
    if use_legacy:
        ref_cppipe = get_templates_path() / "cppipe/ref_2_CP_Apply_Illum.cppipe"

        out_dir.joinpath(filename).write_text(ref_cppipe.read_text())
        return

    # get one of the load data file for generating cppipe
    sample_loaddata_file = next(load_data_path.rglob("*.csv"))

    with CellProfilerContext(out_dir=workspace_path) as cpipe:
        cpipe = generate_illum_apply_pipeline(
            cpipe, sample_loaddata_file, nuclei_channel, cell_channel
        )
        with out_dir.joinpath(filename).open("w") as f:
            cpipe.dump(f)
        filename = "illum_apply_painting.json"
        with out_dir.joinpath(filename).open("w") as f:
            dumpit(cpipe, f, version=6)
