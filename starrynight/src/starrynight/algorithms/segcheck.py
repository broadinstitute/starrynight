"""Segmenation check commands."""

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
from cellprofiler.modules.graytocolor import SCHEME_RGB, GrayToColor
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
from cellprofiler.modules.overlayoutlines import (
    MAX_IMAGE,
    WANTS_COLOR,
    OverlayOutlines,
)
from cellprofiler.modules.rescaleintensity import (
    CUSTOM_VALUE,
    M_STRETCH,
    RescaleIntensity,
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
from starrynight.modules.cp_illum_apply.constants import (
    CP_ILLUM_APPLY_OUT_PATH_SUFFIX,
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
    get_default_path_prefix,
)
from starrynight.utils.globbing import flatten_dict, get_files_by
from starrynight.utils.misc import resolve_path_loaddata

###############################
## Load data generation
###############################


def get_filename_header(
    ch: str, use_legacy: bool = False, legacy_channel_map: dict = {}
) -> str:
    if not use_legacy:
        return f"FileName_Corr{ch}"
    else:
        return f"FileName_{legacy_channel_map[ch]}"


def get_filename_value(
    index: PCPIndex,
    ch: str,
    use_legacy: bool = False,
    legacy_channel_map: dict = {},
) -> str:
    if not use_legacy:
        return f"Plate_{index.plate_id}_Well_{index.well_id}_Site_{int(index.site_id)}_Corr{ch}.tiff"
    else:
        return f"Plate_{index.plate_id}_Well_{index.well_id}_Site_{int(index.site_id)}_Corr{legacy_channel_map[ch]}.tiff"


def get_pathname_header(
    ch: str, use_legacy: bool = False, legacy_channel_map: dict = {}
) -> str:
    if not use_legacy:
        return f"PathName_Corr{ch}"
    else:
        return f"PathName_{legacy_channel_map[ch]}"


def write_loaddata_segcheck(
    images_df: pl.LazyFrame,
    plate_channel_list: list[str],
    corr_images_path: Path | CloudPath,
    nuclei_channel: str | None,
    cell_channel: str | None,
    path_mask: str,
    f: TextIOWrapper,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
) -> None:
    # setup csv headers and write the header first
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    legacy_channel_map = {}

    if use_legacy:
        # Load experiment config
        exp_config = json.loads(exp_config_path.read_text())

        # setup legacy_channel_map
        legacy_channel_map = gen_legacy_channel_map(
            plate_channel_list, exp_config
        )
        # nuclei_channel = exp_config["cp_config"]["nuclei_channel"]
        # cell_channel = exp_config["cp_config"]["cell_channel"]

    metadata_heads = [
        f"Metadata_{col}"
        for col in ["Batch", "Plate", "Site", "Well", "Well_Value"]
    ]
    filename_heads = [
        get_filename_header(ch, use_legacy, legacy_channel_map)
        for ch in plate_channel_list
    ]
    pathname_heads = [
        get_pathname_header(ch, use_legacy, legacy_channel_map)
        for ch in plate_channel_list
    ]
    loaddata_writer.writerow(
        [
            *metadata_heads,
            *filename_heads,
            *pathname_heads,
        ]
    )
    for index in images_df.collect().to_dicts():
        index = PCPIndex(**index)
        filenames = [
            get_filename_value(index, ch, use_legacy, legacy_channel_map)
            for ch in plate_channel_list
        ]
        pathnames = [
            resolve_path_loaddata(AnyPath(path_mask), corr_images_path)
            for _ in range(len(pathname_heads))
        ]

        # Extract well value from well_id by stripping 'Well' prefix if present
        well_value = (
            index.well_id[4:]
            if index.well_id.startswith("Well")
            else index.well_id
        )

        # make sure frame heads are matched with their order in the filenames
        assert index.key is not None
        loaddata_writer.writerow(
            [
                # Metadata heads
                index.batch_id,
                index.plate_id,
                index.site_id,
                index.well_id,
                well_value,
                # Filename heads
                *filenames,
                # Pathname heads
                *pathnames,
            ]
        )


def gen_segcheck_load_data(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    nuclei_channel: str | None = None,
    cell_channel: str | None = None,
    corr_images_path: Path | CloudPath | None = None,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
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
    cell_channel: str
        Channel to use for doing cell segmentation
    corr_images_path : Path | CloudPath
        Path | CloudPath to corr images directory.
    use_legacy : bool
        Use legacy cppipe and loaddata.
    exp_config_path : Path | CloudPath
        Path to experiment config json path.

    """
    # Construct corr images path if not given
    if corr_images_path is None:
        corr_images_path = index_path.parents[1].joinpath(
            CP_ILLUM_APPLY_OUT_PATH_SUFFIX
        )

    df = pl.scan_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    images_df = filter_images(df, False)

    # Only subsample if df is large
    # TODO: implement contiguous sampling
    # if images_df.select(pl.len()).collect().item() > 10:
    #     images_df = images_df.sample(fraction=0.1)

    # Query default path prefix
    default_path_prefix = get_default_path_prefix(images_df)

    # Setup path mask (required for resolving pathnames during the execution)
    if path_mask is None:
        path_mask = default_path_prefix

    # Setup chunking and write loaddata for parallel processing
    images_hierarchy_dict = gen_image_hierarchy(
        images_df, ["batch_id", "plate_id", "well_id", "site_id"]
    )

    levels_leaf = flatten_dict(images_hierarchy_dict)
    for levels, _ in levels_leaf:
        # setup filtered df for chunked levels
        levels_df = filter_df_by_hierarchy(images_df, levels, False)

        # Setup channel list for this level
        plate_channel_list = get_channels_from_df(levels_df)

        # Construct filename for the loaddata csv
        level_out_path = out_path.joinpath(f"{'_'.join(levels)}-segcheck.csv")

        # Construct corr images path for this level
        corr_images_path_level = corr_images_path.joinpath("-".join(levels))
        with level_out_path.open("w") as f:
            write_loaddata_segcheck(
                levels_df,
                plate_channel_list,
                corr_images_path_level,
                nuclei_channel,
                cell_channel,
                path_mask,
                f,
                use_legacy,
                exp_config_path,
            )
    return out_path


###################################
## CellProfiler pipeline generation
###################################


def generate_segcheck_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
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
    load_data.metadata_fields.value = "Batch,Plate"
    load_data.rescale.value = True
    pipeline.add_module(load_data)

    # INFO: Create and configure required modules
    # identifyPrimaryObject(confluent regions) -> mask -> identifyPrimaryObject(nuclei)
    # -> identifySecondaryObject(cells) -> rescaleIntensity -> graytoColor -> OverlayOutlines
    # -> save(outlines) -> ExportToSpreadSheet

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
    identify_secondary_object_cells.image_name.value = f"Masked{cell_channel}"
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
        0.000001,
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

    # rescale intensity
    for ch in channel_list:
        rescale_intensity = RescaleIntensity()
        module_counter += 1
        rescale_intensity.module_num = module_counter
        rescale_intensity.x_name.value = f"Masked{ch}"
        rescale_intensity.y_name.value = f"Rescaled{ch}"
        rescale_intensity.rescale_method.value = M_STRETCH
        rescale_intensity.wants_automatic_high.value = CUSTOM_VALUE
        rescale_intensity.wants_automatic_low.value = CUSTOM_VALUE
        rescale_intensity.source_high.value = 1.0
        rescale_intensity.source_low.value = 0.0
        rescale_intensity.source_scale.value = (0.0, 1.0)
        rescale_intensity.dest_scale.value = (0.0, 1.0)
        rescale_intensity.matching_image_name.value = None
        rescale_intensity.divisor_value.value = 1.0
        rescale_intensity.divisor_measurement.value = None
        pipeline.add_module(rescale_intensity)

    # GrayToColor
    gray_to_color = GrayToColor()
    module_counter += 1
    gray_to_color.module_num = module_counter
    gray_to_color.scheme_choice.value = SCHEME_RGB
    gray_to_color.wants_rescale.value = False
    gray_to_color.red_image_name.value = f"Rescaled{nuclei_channel}"
    gray_to_color.green_image_name.value = f"Rescaled{cell_channel}"
    gray_to_color.blue_image_name.value = f"Rescaled{nuclei_channel}"
    gray_to_color.rgb_image_name.value = "ColorImage"
    gray_to_color.red_adjustment_factor.value = 1.0
    gray_to_color.green_adjustment_factor.value = 1.0
    gray_to_color.blue_adjustment_factor.value = 1.0
    pipeline.add_module(gray_to_color)

    # OverlayOutlines

    overlay_outlines = OverlayOutlines()
    module_counter += 1
    overlay_outlines.module_num = module_counter
    overlay_outlines.blank_image.value = False
    overlay_outlines.image_name.value = "ColorImage"
    overlay_outlines.output_image_name.value = "OrigOverlay"
    overlay_outlines.line_mode.value = "Inner"
    overlay_outlines.wants_color.value = WANTS_COLOR
    overlay_outlines.max_type.value = MAX_IMAGE

    # Add outlines for nuclei, cells and confluent regions
    for _ in range(
        len(["Nuclei", "Cells", "ConfluentRegions"]) - 1
    ):  # 1 outline is already added during init
        overlay_outlines.add_outline()

    colors = ["blue", "white", "#FF8000"]
    for i, obj in enumerate(["Nuclei", "Cells", "ConfluentRegions"]):
        overlay_outlines.outlines[i].objects_name.value = obj
        overlay_outlines.outlines[i].color.value = colors[i]
    pipeline.add_module(overlay_outlines)

    # Save image (combined overlay)
    save_image = SaveImages()
    module_counter += 1
    save_image.module_num = module_counter
    save_image.save_image_or_figure.value = IF_IMAGE
    save_image.image_name.value = "OrigOverlay"
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

    save_image.single_file_name.value = (
        "\\g<Batch>_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_OrigOverlay"
    )
    pipeline.add_module(save_image)

    # export measurements to spreadsheet
    export_measurements = ExportToSpreadsheet()
    module_counter += 1
    export_measurements.module_num = module_counter
    export_measurements.delimiter.value = DELIMITER_COMMA
    export_measurements.directory.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
    export_measurements.wants_prefix.value = True
    export_measurements.prefix.value = "Segcheck_"
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


def gen_segcheck_cppipe(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
    use_legacy: bool = False,
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
    cell_channel : str
        Channel to use for cell segmentation
    use_legacy : bool
        Use legacy segmentation pipeline.

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)

    filename = "segcheck_painting.cppipe"

    # Write old cppipe and return early if use_old is true
    if use_legacy:
        ref_cppipe = (
            get_templates_path() / "cppipe/ref_3_CP_SegmentationCheck.cppipe"
        )

        out_dir.joinpath(filename).write_text(ref_cppipe.read_text())
        return

    # get one of the load data file for generating cppipe
    sample_loaddata_file = next(load_data_path.rglob("*.csv"))

    with CellProfilerContext(out_dir=workspace_path) as cpipe:
        cpipe = generate_segcheck_pipeline(
            cpipe, sample_loaddata_file, nuclei_channel, cell_channel
        )
        with out_dir.joinpath(filename).open("w") as f:
            cpipe.dump(f)
        filename = "segcheck_painting.json"
        with out_dir.joinpath(filename).open("w") as f:
            dumpit(cpipe, f, version=6)
