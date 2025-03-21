"""Preprocess commands."""

import csv
from io import TextIOWrapper
from pathlib import Path

import polars as pl
from cellprofiler.modules.calculatemath import (
    MC_IMAGE,
    O_NONE,
    O_SUBTRACT,
    ROUNDING,
    CalculateMath,
)
from cellprofiler.modules.correctilluminationapply import (
    DOS_SUBTRACT,
    CorrectIlluminationApply,
)
from cellprofiler.modules.correctilluminationcalculate import (
    EA_EACH,
    FI_MANUALLY,
    IC_BACKGROUND,
    SM_GAUSSIAN_FILTER,
    CorrectIlluminationCalculate,
)
from cellprofiler.modules.enhanceorsuppressfeatures import (
    E_SPECKLES,
    ENHANCE,
    N_TUBENESS,
    S_FAST,
    EnhanceOrSuppressFeatures,
)
from cellprofiler.modules.exporttospreadsheet import (
    DELIMITER_COMMA,
    GP_NAME_METADATA,
    NANS_AS_NANS,
    ExportToSpreadsheet,
)
from cellprofiler.modules.filterobjects import (
    FI_LIMITS,
    MODE_MEASUREMENTS,
    PO_BOTH,
    FilterObjects,
)
from cellprofiler.modules.flagimage import C_ANY, S_IMAGE, FlagImage
from cellprofiler.modules.identifyprimaryobjects import (
    DEFAULT_MAXIMA_COLOR,
    FH_ALL,
    LIMIT_NONE,
    UN_INTENSITY,
    WA_INTENSITY,
    IdentifyPrimaryObjects,
)
from cellprofiler.modules.identifysecondaryobjects import (
    M_PROPAGATION,
    IdentifySecondaryObjects,
)
from cellprofiler.modules.imagemath import (
    IM_IMAGE,
    O_AVERAGE,
    O_NONE,
    O_STDEV,
    ImageMath,
)
from cellprofiler.modules.measureobjectintensity import MeasureObjectIntensity
from cellprofiler.modules.overlayoutlines import MAX_IMAGE, WANTS_COLOR, OverlayOutlines
from cellprofiler.modules.relateobjects import D_NONE, RelateObjects
from cellprofiler.modules.rescaleintensity import (
    CUSTOM_VALUE,
    M_STRETCH,
    RescaleIntensity,
)
from cellprofiler.modules.saveimages import (
    AXIS_T,
    BIT_DEPTH_16,
    FF_PNG,
    FF_TIFF,
    FN_SINGLE_NAME,
    IF_IMAGE,
    WS_EVERY_CYCLE,
    SaveImages,
)
from cellprofiler.modules.threshold import (
    O_FOREGROUND,
    O_THREE_CLASS,
    O_TWO_CLASS,
    RB_MEAN,
    RB_SD,
    TM_LI,
    TM_OTSU,
    TM_ROBUST_BACKGROUND,
    TS_GLOBAL,
)
from cellprofiler_core.constants.modules.load_data import (
    ABSOLUTE_FOLDER_NAME,
    DEFAULT_OUTPUT_FOLDER_NAME,
    NO_FOLDER_NAME,
)
from cellprofiler_core.modules.loaddata import LoadData
from cellprofiler_core.pipeline import Pipeline
from centrosome.bg_compensate import MODE_AUTO
from cloudpathlib import AnyPath, CloudPath

from starrynight.algorithms.cp_plugin_callbarcodes import CallBarcodes
from starrynight.algorithms.cp_plugin_compensate_colors import (
    CC_OBJECTS,
    CompensateColors,
)
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
    plate_cycles_list: list[str],
    corr_images_path: Path | CloudPath,
    align_images_path: Path | CloudPath,
    nuclei_channel: str,
    path_mask: str,
    f: TextIOWrapper,
) -> None:
    # setup csv headers and write the header first
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    metadata_heads = [f"Metadata_{col}" for col in ["Batch", "Plate", "Site", "Well"]]

    filename_heads = [
        f"FileName_Align_Cycle_{int(cycle)}_{col}"
        for cycle in plate_cycles_list
        for col in plate_channel_list
    ]
    pathname_heads = [
        f"PathName_Align_Cycle_{int(cycle)}_{col}"
        for cycle in plate_cycles_list
        for col in plate_channel_list
    ]
    loaddata_writer.writerow(
        [
            *metadata_heads,
            *filename_heads,
            *pathname_heads,
        ]
    )
    index = images_df[0].to_dicts()[0]
    index = PCPIndex(**index)
    wells_sites = (
        images_df.group_by("well_id").agg(pl.col("site_id").unique()).to_dicts()
    )
    for well_sites in wells_sites:
        index.well_id = well_sites["well_id"]
        for site_id in well_sites["site_id"]:
            index.site_id = site_id
            filenames = [
                f"{index.batch_id}_{index.plate_id}_{int(cycle)}_Well_{index.well_id}_Site_{int(index.site_id)}_Aligned{col}.tiff"
                for col in plate_channel_list
                for cycle in plate_cycles_list
            ]
            if int(index.cycle_id) != 1:
                pathnames = [
                    resolve_path_loaddata(AnyPath(path_mask), align_images_path)
                    for _ in range(len(pathname_heads))
                ]
            else:
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


def gen_preprocess_load_data_by_batch_plate(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    nuclei_channel: str,
    corr_images_path: Path | CloudPath | None = None,
    align_images_path: Path | CloudPath | None = None,
) -> None:
    """Generate load data for preprocess pipeline.

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
    align_images_path : Path | CloudPath
        Path | CloudPath to aligned images directory.

    """
    # Construct illum path if not given
    if corr_images_path is None:
        corr_images_path = index_path.parents[1].joinpath("illum/sbs/illum_apply")
    if align_images_path is None:
        align_images_path = index_path.parents[1].joinpath("align/sbs")

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
            # Setup channel list for that plate
            plate_channel_list = get_channels_by_batch_plate(images_df, batch, plate)

            # Get plate cycle list
            plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)

            # filter batch and plate images
            df_plate = images_df.filter(
                pl.col("batch_id").eq(batch) & pl.col("plate_id").eq(plate)
            )

            batch_plate_out_path = out_path.joinpath(batch, plate)
            batch_plate_out_path.mkdir(parents=True, exist_ok=True)
            with batch_plate_out_path.joinpath(f"preprocess_{batch}_{plate}.csv").open(
                "w"
            ) as f:
                write_loaddata(
                    df_plate,
                    plate_channel_list,
                    plate_cycles_list,
                    corr_images_path,
                    align_images_path,
                    nuclei_channel,
                    path_mask,
                    f,
                )


###################################
## CellProfiler pipeline generation
###################################


def generate_preprocess_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
    barcode_csv_path: Path | CloudPath,
    nuclei_channel: str,
) -> Pipeline:
    load_data_df = pl.read_csv(load_data_path.resolve().__str__())
    channel_list = list(
        # Remove duplicate channels
        set(
            [
                col.split("_")[-1]
                for col in load_data_df.columns
                if col.startswith("FileName")
            ]
        )
    )
    sbs_channel_list = channel_list.copy()
    sbs_channel_list.remove(nuclei_channel)
    cycle_list = list(
        # Remove duplilcate cycels
        set(
            [
                int(col.split("_")[-2])
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
    # for all channels ImageMath(MeanOfAllCycles)
    # -> for all channels CorrectIllumCalculate(MeanOfAllCycles)
    # -> for all channels CorrectIllumApply(for all cycle, subtract)
    # -> for all channels ImageMath(StDevOfAllCycles)
    # -> ImageMath(average of StDevOfAllCycles for all channel)
    # -> IdentifyPrimaryObjects(Cycle01_Nuclei)
    # -> IdentifySecondaryObjects(Cells)
    # -> EnhanceOrSuppressFeatures(MeanOfAllStDevs, Enhance)
    # -> IdentifyPrimaryObjects(Foci) -> FilterObjects(Foci)
    # -> CompensateColors(for all cycles and channels)
    # -> MeasureObjectIntensity(for all channels and cycles and Foci)
    # -> CallBarcodes(Foci)
    # -> ImageMath(BarcodeScores)
    # -> ImageMath(BarcodeScores)
    # -> MeasureObjectIntensity(BarcodeScores, Barcodes_Barcodes)
    # -> RelateObjects(Cells, BarcodeFoci)
    # -> for all cycles and channels save(preprocessed images)
    # -> ExportToSpreadsheet
    # -> CalculateMath(Divide20)
    # -> CalculateMath(Divide20floor)
    # -> CalculateMath(Divide20diff)
    # -> FlagImage
    # -> ImageMath(MeanOfAllStDevs -> StdSqrt)
    # -> RescaleIntensity(StdSqrt)
    # -> OverlayOutlines(StdDevOverlay)
    # -> SaveImages(png,tiff)

    # Calculate MeanOfAllCycles
    for ch in sbs_channel_list:
        mean_cycles = ImageMath()
        module_counter += 1
        mean_cycles.module_num = module_counter
        mean_cycles.operation.value = O_AVERAGE
        mean_cycles.exponent.value = 1
        mean_cycles.after_factor.value = 1
        mean_cycles.addend.value = 0
        mean_cycles.truncate_low.value = True
        mean_cycles.truncate_high.value = True
        mean_cycles.replace_nan.value = True
        mean_cycles.ignore_mask.value = False
        mean_cycles.output_image_name.value = f"MeanOfAllCycles_{ch}"
        # Create all the image slots (two of the are initialized by default)
        for _ in range(len(cycle_list) - 2):
            mean_cycles.add_image()
        # Add cycle images
        for i, cycle in enumerate(cycle_list):
            # Image or measurement?
            mean_cycles.images[i].image_or_measurement.value = IM_IMAGE
            # Image name
            mean_cycles.images[i].image_name.value = f"Align_Cycle_{cycle}_{ch}"
            # Measurement
            mean_cycles.images[i].measurement.value = ""
            # Factor
            mean_cycles.images[i].factor.value = 1

        pipeline.add_module(mean_cycles)

    # CorrectIlluminationCalculate
    for ch in sbs_channel_list:
        correct_illum_calculate = CorrectIlluminationCalculate()
        module_counter += 1
        correct_illum_calculate.module_num = module_counter
        correct_illum_calculate.image_name.value = f"MeanOfAllCycles_{ch}"
        correct_illum_calculate.illumination_image_name.value = f"IllumMean{ch}"
        correct_illum_calculate.intensity_choice.value = IC_BACKGROUND
        correct_illum_calculate.dilate_objects.value = False
        correct_illum_calculate.object_dilation_radius.value = 1
        correct_illum_calculate.block_size.value = 40
        correct_illum_calculate.rescale_option.value = "No"
        correct_illum_calculate.each_or_all.value = EA_EACH
        correct_illum_calculate.smoothing_method.value = SM_GAUSSIAN_FILTER
        correct_illum_calculate.automatic_object_width.value = FI_MANUALLY
        correct_illum_calculate.object_width.value = 10
        correct_illum_calculate.size_of_smoothing_filter.value = 60
        correct_illum_calculate.save_average_image.value = False
        correct_illum_calculate.average_image_name.value = f"Illum{ch}Avg"
        correct_illum_calculate.save_dilated_image.value = False
        correct_illum_calculate.dilated_image_name.value = f"Illum{ch}Dilated"
        correct_illum_calculate.automatic_splines.value = True
        correct_illum_calculate.spline_bg_mode.value = MODE_AUTO
        correct_illum_calculate.spline_points.value = 5
        correct_illum_calculate.spline_threshold.value = 2
        correct_illum_calculate.spline_rescale.value = 2
        correct_illum_calculate.spline_maximum_iterations.value = 40
        correct_illum_calculate.spline_convergence.value = 0.001
        pipeline.add_module(correct_illum_calculate)

    # CorrectIlluminationApply
    for ch in sbs_channel_list:
        correct_illum_apply = CorrectIlluminationApply()
        module_counter += 1
        correct_illum_apply.module_num = module_counter

        # add image slots
        for _ in range(len(cycle_list) - 1):  # One image is already added by default
            correct_illum_apply.add_image()

        for i, cycle in enumerate(cycle_list):
            # image_name
            correct_illum_apply.images[i].image_name.value = f"Align_Cycle_{cycle}_{ch}"
            # corrected_image_name
            correct_illum_apply.images[
                i
            ].corrected_image_name.value = f"Align_Cycle_{cycle}_{ch}_BackSub"

            # illum correct function image name
            correct_illum_apply.images[
                i
            ].illum_correct_function_image_name.value = f"IllumMean{ch}"

            # how illum function is applied
            correct_illum_apply.images[i].divide_or_subtract.value = DOS_SUBTRACT
        pipeline.add_module(correct_illum_apply)

    # Calculate StdDev
    for ch in sbs_channel_list:
        std_dev_cycles = ImageMath()
        module_counter += 1
        std_dev_cycles.module_num = module_counter
        std_dev_cycles.operation.value = O_STDEV
        std_dev_cycles.exponent.value = 1
        std_dev_cycles.after_factor.value = 1
        std_dev_cycles.addend.value = 0
        std_dev_cycles.truncate_low.value = True
        std_dev_cycles.truncate_high.value = True
        std_dev_cycles.replace_nan.value = True
        std_dev_cycles.ignore_mask.value = False
        std_dev_cycles.output_image_name.value = f"StdDevOfAllCycles_{ch}"
        # Create all the image slots (two of the are initialized by default)
        for _ in range(len(cycle_list) - 2):
            std_dev_cycles.add_image()
        # Add cycle images
        for i, cycle in enumerate(cycle_list):
            # Image or measurement?
            std_dev_cycles.images[i].settings[0].value = IM_IMAGE
            # Image name
            std_dev_cycles.images[i].settings[
                1
            ].value = f"Align_Cycle_{int(cycle)}_{ch}"
            # Measurement
            std_dev_cycles.images[i].settings[2].value = ""
            # Factor
            std_dev_cycles.images[i].settings[3].value = 1

        pipeline.add_module(std_dev_cycles)

    # Calculate average of Mean and StdDev
    mean_std_avg_ch = ImageMath()
    module_counter += 1
    mean_std_avg_ch.module_num = module_counter
    mean_std_avg_ch.operation.value = O_AVERAGE
    mean_std_avg_ch.exponent.value = 1
    mean_std_avg_ch.after_factor.value = 1
    mean_std_avg_ch.addend.value = 0
    mean_std_avg_ch.truncate_low.value = True
    mean_std_avg_ch.truncate_high.value = True
    mean_std_avg_ch.replace_nan.value = True
    mean_std_avg_ch.ignore_mask.value = False
    mean_std_avg_ch.output_image_name.value = "MeanStdDevOfAllCycles"

    # image slots (two of the are initialized by default)
    for ch in range(len(sbs_channel_list) - 2):
        mean_std_avg_ch.add_image()
    # Add cycle images
    for i, ch in enumerate(sbs_channel_list):
        # Image or measurement?
        mean_std_avg_ch.images[i].settings[0].value = IM_IMAGE
        # Image name
        mean_std_avg_ch.images[i].settings[1].value = f"StdDevOfAllCycles_{ch}"
        # Measurement
        mean_std_avg_ch.images[i].settings[2].value = ""
        # Factor
        mean_std_avg_ch.images[i].settings[3].value = 1

    pipeline.add_module(mean_std_avg_ch)

    # IdentifyPrimaryObjects(Cycle01_Nuclei)
    identify_primary_object_nuclei = IdentifyPrimaryObjects()
    module_counter += 1
    identify_primary_object_nuclei.module_num = module_counter
    identify_primary_object_nuclei.x_name.value = f"Align_Cycle_1_{nuclei_channel}"
    identify_primary_object_nuclei.y_name.value = "Nuclei"
    identify_primary_object_nuclei.size_range.value = (6, 25)
    identify_primary_object_nuclei.exclude_size.value = True
    identify_primary_object_nuclei.exclude_border_objects.value = True
    identify_primary_object_nuclei.unclump_method.value = UN_INTENSITY
    identify_primary_object_nuclei.watershed_method.value = WA_INTENSITY
    identify_primary_object_nuclei.automatic_smoothing.value = False
    identify_primary_object_nuclei.smoothing_filter_size.value = 4
    identify_primary_object_nuclei.automatic_suppression.value = False
    identify_primary_object_nuclei.maxima_suppression_size.value = 4.0
    identify_primary_object_nuclei.low_res_maxima.value = True
    identify_primary_object_nuclei.fill_holes.value = FH_ALL
    identify_primary_object_nuclei.limit_choice.value = LIMIT_NONE
    identify_primary_object_nuclei.maximum_object_count.value = 500
    identify_primary_object_nuclei.want_plot_maxima.value = False
    identify_primary_object_nuclei.maxima_color.value = DEFAULT_MAXIMA_COLOR
    identify_primary_object_nuclei.use_advanced.value = True
    identify_primary_object_nuclei.threshold_setting_version.value = 12
    identify_primary_object_nuclei.threshold.threshold_scope.value = TS_GLOBAL
    identify_primary_object_nuclei.threshold.global_operation.value = TM_LI
    identify_primary_object_nuclei.threshold.local_operation.value = TM_LI
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

    # Identify cells
    identify_secondary_object_cells = IdentifySecondaryObjects()
    module_counter += 1
    identify_secondary_object_cells.module_num = module_counter
    identify_secondary_object_cells.x_name.value = "Nuclei"
    identify_secondary_object_cells.y_name.value = "Cells"
    identify_secondary_object_cells.method.value = M_PROPAGATION
    identify_secondary_object_cells.image_name.value = (
        f"Align_Cycle_{1}_{sbs_channel_list[0]}"
    )
    identify_secondary_object_cells.distance_to_dilate.value = 20
    identify_secondary_object_cells.regularization_factor.value = 0.05
    identify_secondary_object_cells.wants_discard_edge.value = False
    identify_secondary_object_cells.wants_discard_primary.value = False
    identify_secondary_object_cells.fill_holes.value = True
    identify_secondary_object_cells.new_primary_objects_name.value = "FilteredNuclei"
    identify_secondary_object_cells.threshold_setting_version.value = 12
    identify_secondary_object_cells.threshold.threshold_scope.value = TS_GLOBAL
    identify_secondary_object_cells.threshold.global_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.local_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.threshold_smoothing_scale.value = 0.0
    identify_secondary_object_cells.threshold.threshold_correction_factor.value = 0.9
    identify_secondary_object_cells.threshold.threshold_range.value = (0.002, 0.02)
    identify_secondary_object_cells.threshold.manual_threshold.value = 0.000000000001
    identify_secondary_object_cells.threshold.thresholding_measurement.value = None
    identify_secondary_object_cells.threshold.two_class_otsu.value = O_THREE_CLASS
    identify_secondary_object_cells.threshold.assign_middle_to_foreground.value = (
        O_FOREGROUND
    )
    identify_secondary_object_cells.threshold.lower_outlier_fraction.value = 0.05
    identify_secondary_object_cells.threshold.upper_outlier_fraction.value = 0.05
    identify_secondary_object_cells.threshold.averaging_method.value = RB_MEAN
    identify_secondary_object_cells.threshold.variance_method.value = RB_SD
    identify_secondary_object_cells.threshold.number_of_deviations.value = 2.0
    identify_secondary_object_cells.threshold.adaptive_window_size.value = 50
    identify_secondary_object_cells.threshold.log_transform.value = True
    pipeline.add_module(identify_secondary_object_cells)

    # Enhance or Suppress features
    eos_features = EnhanceOrSuppressFeatures()
    module_counter += 1
    eos_features.module_num = module_counter
    eos_features.x_name.value = "MeanStdDevOfAllCycles"
    eos_features.y_name.value = "EOSFeatures"
    eos_features.method.value = ENHANCE
    eos_features.object_size.value = 5
    eos_features.enhance_method.value = E_SPECKLES
    eos_features.hole_size.value = (1, 10)
    eos_features.smoothing.value = 2.0
    eos_features.angle.value = 0.0
    eos_features.decay.value = 0.95
    eos_features.neurite_choice.value = N_TUBENESS
    eos_features.speckle_accuracy.value = S_FAST
    eos_features.wants_rescale.value = True
    pipeline.add_module(eos_features)

    # IdentifyPrimaryObjects (Foci)
    identify_primary_object_foci = IdentifyPrimaryObjects()
    module_counter += 1
    identify_primary_object_foci.module_num = module_counter
    identify_primary_object_foci.x_name.value = "EOSFeatures"
    identify_primary_object_foci.y_name.value = "Foci"
    identify_primary_object_foci.size_range.value = (2, 10)
    identify_primary_object_foci.exclude_size.value = True
    identify_primary_object_foci.exclude_border_objects.value = True
    identify_primary_object_foci.unclump_method.value = UN_INTENSITY
    identify_primary_object_foci.watershed_method.value = WA_INTENSITY
    identify_primary_object_foci.automatic_smoothing.value = False
    identify_primary_object_foci.smoothing_filter_size.value = 10
    identify_primary_object_foci.automatic_suppression.value = False
    identify_primary_object_foci.maxima_suppression_size.value = 7.0
    identify_primary_object_foci.low_res_maxima.value = True
    identify_primary_object_foci.fill_holes.value = FH_ALL
    identify_primary_object_foci.limit_choice.value = LIMIT_NONE
    identify_primary_object_foci.maximum_object_count.value = 500
    identify_primary_object_foci.want_plot_maxima.value = False
    identify_primary_object_foci.maxima_color.value = DEFAULT_MAXIMA_COLOR
    identify_primary_object_foci.use_advanced.value = True
    identify_primary_object_foci.threshold_setting_version.value = 12
    identify_primary_object_foci.threshold.threshold_scope.value = TS_GLOBAL
    identify_primary_object_foci.threshold.global_operation.value = TM_ROBUST_BACKGROUND
    identify_primary_object_foci.threshold.local_operation.value = TM_ROBUST_BACKGROUND
    identify_primary_object_foci.threshold.threshold_smoothing_scale.value = 1.3488
    identify_primary_object_foci.threshold.threshold_correction_factor.value = 1.0
    identify_primary_object_foci.threshold.threshold_range.value = (0.0008, 1.0)
    identify_primary_object_foci.threshold.manual_threshold.value = 0.0
    identify_primary_object_foci.threshold.thresholding_measurement.value = None
    identify_primary_object_foci.threshold.two_class_otsu.value = O_THREE_CLASS
    identify_primary_object_foci.threshold.assign_middle_to_foreground.value = (
        O_FOREGROUND
    )
    identify_primary_object_foci.threshold.lower_outlier_fraction.value = 0.025
    identify_primary_object_foci.threshold.upper_outlier_fraction.value = 0.05
    identify_primary_object_foci.threshold.averaging_method.value = RB_MEAN
    identify_primary_object_foci.threshold.variance_method.value = RB_SD
    identify_primary_object_foci.threshold.number_of_deviations.value = 4.0
    identify_primary_object_foci.threshold.adaptive_window_size.value = 50
    identify_primary_object_foci.threshold.log_transform.value = False
    pipeline.add_module(identify_primary_object_foci)

    # Filter Objects (Foci -> BarcodeFoci)
    filter_foci = FilterObjects()
    module_counter += 1
    filter_foci.module_num = module_counter
    filter_foci.x_name.value = "Foci"
    filter_foci.y_name.value = "BarcodeFoci"
    filter_foci.mode.value = MODE_MEASUREMENTS
    filter_foci.filter_choice.value = FI_LIMITS
    filter_foci.per_object_assignment.value = PO_BOTH
    filter_foci.enclosing_object_name.value = None
    # Select the measurement to filter by
    filter_foci.measurements[0].settings[0].value = "Number_Object_Number"
    # Filter using a minimum measurement value
    filter_foci.measurements[0].settings[1].value = True
    # Minimum value
    filter_foci.measurements[0].settings[2].value = 0.5
    # Filter using a maximum measurement value
    filter_foci.measurements[0].settings[3].value = False
    # Maximum value
    filter_foci.measurements[0].settings[4].value = 1.0
    pipeline.add_module(filter_foci)

    # CompensateColors (using the edited version that ships with starrynight)
    compensate = CompensateColors()
    module_counter += 1
    compensate.module_num = module_counter
    for i, ch in enumerate(sbs_channel_list):
        for j, cycle in enumerate(cycle_list):
            offset = i * len(cycle_list)
            compensate.add_image()
            # Select an image to measure
            compensate.image_groups[offset + j].settings[
                1
            ].value = f"Align_Cycle_{cycle}_{ch}_BackSub"
            # What compensation class it belongs to?
            compensate.image_groups[offset + j].settings[2].value = i + 1
            # Select an output image
            compensate.image_groups[offset + j].settings[
                3
            ].value = f"Align_Cycle_{cycle}_{ch}_Compensated"

    compensate.images_or_objects.value = CC_OBJECTS
    compensate.object_groups[0].object_name.value = "Foci"
    compensate.do_rescale_input.value = "No"
    compensate.do_rescale_after_mask.value = "No"
    compensate.do_match_histograms.value = "Yes, post-masking to objects"
    compensate.histogram_match_class.value = len(sbs_channel_list)
    compensate.do_rescale_output.value = "No"
    compensate.do_scalar_multiply.value = "No"
    compensate.scalar_percentile.value = 4
    compensate.do_tophat_filter.value = False
    # compensate.tophat_radius = False
    compensate.do_LoG_filter.value = True
    compensate.LoG_radius.value = 1
    compensate.do_DoG_filter.value = False
    # compensate.DoG_low_radius.value = ""
    compensate.DoG_high_radius.value = 1
    pipeline.add_module(compensate)

    # -> MeasureObjectIntensity(for all channels and cycles and Foci)
    measure_object_intensity = MeasureObjectIntensity()
    module_counter += 1
    measure_object_intensity.module_num = module_counter
    measure_object_intensity.images_list.value = ", ".join(
        [
            f"Align_Cycle_{cycle}_{ch}_Compensated"
            for ch in sbs_channel_list
            for cycle in cycle_list
        ]
    )
    measure_object_intensity.objects_list.value = ", ".join(["Foci"])
    pipeline.add_module(measure_object_intensity)

    # CallBarcodes
    call_barcodes = CallBarcodes()
    module_counter += 1
    call_barcodes.module_num = module_counter
    call_barcodes.ncycles.value = len(cycle_list)
    call_barcodes.input_object_name.value = "Foci"
    call_barcodes.cycle1measure.value = (
        f"Intensity_MaxIntensity_Align_Cycle_1_{channel_list[0]}_Compensated"
    )
    call_barcodes.csv_directory.value = (
        f"{ABSOLUTE_FOLDER_NAME}|{barcode_csv_path.parent.resolve().__str__()}"
    )
    call_barcodes.csv_file_name.value = barcode_csv_path.name
    call_barcodes.metadata_field_barcode.value = "sgRNA"
    call_barcodes.metadata_field_tag.value = "gene_symbol"
    call_barcodes.wants_call_image.value = True
    call_barcodes.outimage_calls_name.value = "Barcodes_IntValues"
    call_barcodes.wants_score_image.value = True
    call_barcodes.outimage_score_name.value = "BarcodeScores_IntValues"
    call_barcodes.has_empty_vector_barcode.value = ""
    call_barcodes.empty_vector_barcode_sequence.value = ""
    pipeline.add_module(call_barcodes)

    # Some math with barcode output images
    for out_name, in_name in [
        ("Barcodes_Barcodes", "Barcodes_IntValues"),
        ("Barcodes_Scores", "BarcodeScores_IntValues"),
    ]:
        math_barcode_out = ImageMath()
        module_counter += 1
        math_barcode_out.module_num = module_counter
        math_barcode_out.operation.value = O_NONE
        math_barcode_out.exponent.value = 1
        math_barcode_out.after_factor.value = 1
        math_barcode_out.addend.value = 0
        math_barcode_out.truncate_low.value = True
        math_barcode_out.truncate_high.value = True
        math_barcode_out.replace_nan.value = True
        math_barcode_out.ignore_mask.value = False
        math_barcode_out.output_image_name.value = out_name
        # Image or measurement
        math_barcode_out.images[0].settings[0].value = IM_IMAGE
        # Image name
        math_barcode_out.images[0].settings[1].value = in_name
        # Measurement
        math_barcode_out.images[0].settings[2].value = ""
        # Factor
        math_barcode_out.images[0].settings[3].value = 0.000015259021897
        pipeline.add_module(math_barcode_out)

    # MeasureObjectIntensity
    measure_object_intensity_barcodes = MeasureObjectIntensity()
    module_counter += 1
    measure_object_intensity_barcodes.module_num = module_counter
    measure_object_intensity_barcodes.images_list.value = ", ".join(
        [
            "Barcodes_Scores",
            "Barcodes_Barcodes",
        ]
    )
    measure_object_intensity_barcodes.objects_list.value = ", ".join(["BarcodeFoci"])
    pipeline.add_module(measure_object_intensity_barcodes)

    # RelateObjects
    relate_objects = RelateObjects()
    module_counter += 1
    relate_objects.module_num = module_counter
    relate_objects.x_name.value = "Cells"
    relate_objects.y_name.value = "BarcodeFoci"
    relate_objects.find_parent_child_distances.value = D_NONE
    relate_objects.wants_per_parent_means.value = True
    relate_objects.wants_step_parent_distances.value = False
    relate_objects.wants_child_objects_saved.value = False
    relate_objects.output_child_objects_name.value = "RelateObjects"
    pipeline.add_module(relate_objects)

    # Save image (compensated images)
    for cycle in cycle_list:
        for ch in channel_list:
            save_image = SaveImages()
            module_counter += 1
            save_image.module_num = module_counter
            save_image.save_image_or_figure.value = IF_IMAGE
            if ch == nuclei_channel:
                save_image.image_name.value = f"Align_Cycle_{cycle}_{ch}"
            else:
                save_image.image_name.value = f"Align_Cycle_{cycle}_{ch}_Compensated"
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
            save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_{cycle}_Well_\\g<Well>_Site_\\g<Site>_Compensated{ch}"
            pipeline.add_module(save_image)

    # ExportToSpreadsheet
    export_measurements = ExportToSpreadsheet()
    module_counter += 1
    export_measurements.module_num = module_counter
    export_measurements.delimiter.value = DELIMITER_COMMA
    export_measurements.directory.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
    export_measurements.wants_prefix.value = True
    export_measurements.prefix.value = "\\g<Batch>_\\g<Plate>_PreProcess"
    export_measurements.wants_overwrite_without_warning.value = False
    export_measurements.add_metadata.value = True
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

    # Calculate Math
    # TODO: Figure out why this is here
    for out_name, op, round_val in [
        ("Divide20", O_NONE, ROUNDING[0]),
        ("Divide20floor", O_NONE, ROUNDING[2]),
        ("Divide20diff", O_SUBTRACT, ROUNDING[0]),
    ]:
        calc_math_div20 = CalculateMath()
        module_counter += 1
        calc_math_div20.module_num = module_counter
        calc_math_div20.output_feature_name.value = out_name
        calc_math_div20.operation.value = op

        # Numerator
        calc_math_div20.operands[0].operand_choice.value = MC_IMAGE
        calc_math_div20.operands[0].operand_objects.value = None

        if op != O_SUBTRACT:
            calc_math_div20.operands[0].operand_measurement.value = "Metadata_Site"
        else:
            calc_math_div20.operands[0].operand_measurement.value = "Math_Divide20"

        calc_math_div20.operands[0].multiplicand.value = 0.05
        calc_math_div20.operands[0].exponent.value = 1.0

        # Denominator
        calc_math_div20.operands[1].operand_choice.value = MC_IMAGE
        calc_math_div20.operands[1].operand_objects.value = None

        if op != O_SUBTRACT:
            calc_math_div20.operands[1].operand_measurement.value = None
        else:
            calc_math_div20.operands[1].operand_measurement.value = "Math_Divide20floor"

        calc_math_div20.operands[1].multiplicand.value = 1.0
        calc_math_div20.operands[1].exponent.value = 1.0

        calc_math_div20.wants_log.value = False
        calc_math_div20.final_multiplicand.value = 1.0
        calc_math_div20.final_exponent.value = 1.0
        calc_math_div20.final_addend.value = 0

        calc_math_div20.constrain_lower_bound.value = False
        calc_math_div20.lower_bound.value = 0
        calc_math_div20.constrain_upper_bound.value = False
        calc_math_div20.upper_bound.value = 1.0
        calc_math_div20.rounding.value = round_val
        pipeline.add_module(calc_math_div20)

    # -> Flag Image (Divide20)
    flag_images = FlagImage()
    module_counter += 1
    flag_images.module_num = module_counter
    # Flag's category [3]
    flag_images.flags[0].category.value = "Divide20"
    # Name of the flag [4]
    flag_images.flags[0].feature_name.value = "Divide20Flag"
    # How should the measurements be linked [5]
    flag_images.flags[0].combination_choice.value = C_ANY
    # Skip image set if flagged [6]
    flag_images.flags[0].wants_skip.value = True

    # Measurement settings, One measurement is added by default for each flag
    flag_images.flags[0].measurement_settings[0].source_choice.value = S_IMAGE
    flag_images.flags[0].measurement_settings[0].object_name.value = None
    flag_images.flags[0].measurement_settings[0].measurement.value = "Math_Divide20diff"
    flag_images.flags[0].measurement_settings[0].wants_minimum.value = False
    flag_images.flags[0].measurement_settings[0].minimum_value.value = 0.0
    flag_images.flags[0].measurement_settings[0].wants_maximum.value = True
    flag_images.flags[0].measurement_settings[0].maximum_value.value = 0.0000000001
    pipeline.add_module(flag_images)

    # ImageMath
    # TODO: Is something really happening here?
    math_stdsqrt = ImageMath()
    module_counter += 1
    math_stdsqrt.module_num = module_counter
    math_stdsqrt.operation.value = O_NONE
    math_stdsqrt.exponent.value = 1
    math_stdsqrt.after_factor.value = 1
    math_stdsqrt.addend.value = 0
    math_stdsqrt.truncate_low.value = True
    math_stdsqrt.truncate_high.value = True
    math_stdsqrt.replace_nan.value = True
    math_stdsqrt.ignore_mask.value = False
    math_stdsqrt.output_image_name.value = "StdSqrt"
    # Image or measurement
    math_stdsqrt.images[0].settings[0].value = IM_IMAGE
    # Image name
    math_stdsqrt.images[0].settings[1].value = "MeanStdDevOfAllCycles"
    # Measurement
    math_stdsqrt.images[0].settings[2].value = ""
    # Factor
    math_stdsqrt.images[0].settings[3].value = 1.0
    pipeline.add_module(math_stdsqrt)

    # Rescale Intensity
    rescale_intensity = RescaleIntensity()
    module_counter += 1
    rescale_intensity.module_num = module_counter
    rescale_intensity.x_name.value = "StdSqrt"
    rescale_intensity.y_name.value = "RescaledStdSqrt"
    rescale_intensity.rescale_method.value = M_STRETCH
    rescale_intensity.wants_automatic_low.value = CUSTOM_VALUE
    rescale_intensity.wants_automatic_high.value = CUSTOM_VALUE
    rescale_intensity.source_low.value = 0.0
    rescale_intensity.source_high.value = 1.0
    rescale_intensity.source_scale.value = (0.0, 1.0)
    rescale_intensity.dest_scale.value = (0.0, 1.0)
    rescale_intensity.matching_image_name.value = None
    rescale_intensity.divisor_value.value = 1.0
    rescale_intensity.divisor_measurement.value = None
    pipeline.add_module(rescale_intensity)

    # OverlayOutlines
    overlay_outlines = OverlayOutlines()
    module_counter += 1
    overlay_outlines.module_num = module_counter
    overlay_outlines.blank_image.value = False
    overlay_outlines.image_name.value = "RescaledStdSqrt"
    overlay_outlines.output_image_name.value = "StdSqrt_Overlay"
    overlay_outlines.line_mode.value = "Inner"
    overlay_outlines.wants_color.value = WANTS_COLOR
    overlay_outlines.max_type.value = MAX_IMAGE

    # Add outlines for nuclei, cells and confluent regions
    for _ in range(
        len(["Foci", "Cells"]) - 1
    ):  # 1 outline is already added during init
        overlay_outlines.add_outline()

    colors = ["red", "#0080FF"]
    for i, obj in enumerate(["Foci", "Cells"]):
        overlay_outlines.outlines[i].objects_name.value = obj
        overlay_outlines.outlines[i].color.value = colors[i]
    pipeline.add_module(overlay_outlines)

    # Save outlines
    for fmt in [FF_PNG, FF_TIFF]:
        save_image = SaveImages()
        module_counter += 1
        save_image.module_num = module_counter
        save_image.save_image_or_figure.value = IF_IMAGE
        save_image.image_name.value = "StdSqrt_Overlay"
        save_image.file_name_method.value = FN_SINGLE_NAME
        save_image.number_of_digits.value = 4
        save_image.wants_file_name_suffix.value = False
        save_image.file_name_suffix.value = ""
        save_image.file_format.value = fmt
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
            "\\g<Batch>_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_StdSqrt_Overlay"
        )
        pipeline.add_module(save_image)

    return pipeline


def gen_preprocess_cppipe_by_batch_plate(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    barcode_csv_path: Path | CloudPath,
    nuclei_channel: str,
) -> None:
    """Write out preprocess pipeline to file.

    Parameters
    ----------
    load_data_path : Path | CloudPath
        Path | CloudPath to load data csv dir.
    out_dir : Path | CloudPath
        Path | CloudPath to output directory.
    workspace_path : Path | CloudPath
        Path | CloudPath to workspace directory.
    barcode_csv_path : Path | CloudPath
        Path | CloudPath to barcode csv.
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
                cpipe = generate_preprocess_pipeline(
                    cpipe, file, barcode_csv_path, nuclei_channel
                )
                filename = f"{file.stem}.cppipe"
                with files_out_dir.joinpath(filename).open("w") as f:
                    cpipe.dump(f)
