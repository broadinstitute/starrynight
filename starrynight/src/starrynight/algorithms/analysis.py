"""Analysis commands."""

import csv
from io import TextIOWrapper
from pathlib import Path

import polars as pl
from cellprofiler.modules.calculatemath import (
    MC_IMAGE,
    O_DIVIDE,
    ROUNDING,
    CalculateMath,
)
from cellprofiler.modules.convertobjectstoimage import ConvertObjectsToImage
from cellprofiler.modules.enhanceorsuppressfeatures import (
    E_NEURITES,
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
from cellprofiler.modules.flagimage import C_ANY, S_AVERAGE_OBJECT, S_IMAGE, FlagImage
from cellprofiler.modules.graytocolor import SCHEME_RGB, GrayToColor
from cellprofiler.modules.identifyprimaryobjects import (
    DEFAULT_MAXIMA_COLOR,
    FH_DECLUMP,
    LIMIT_NONE,
    UN_INTENSITY,
    UN_SHAPE,
    WA_INTENSITY,
    WA_NONE,
    WA_SHAPE,
    IdentifyPrimaryObjects,
)
from cellprofiler.modules.identifysecondaryobjects import (
    M_PROPAGATION,
    IdentifySecondaryObjects,
)
from cellprofiler.modules.identifytertiaryobjects import IdentifyTertiaryObjects
from cellprofiler.modules.imagemath import (
    IM_IMAGE,
    IM_MEASUREMENT,
    O_INVERT,
    O_MAXIMUM,
    O_MINIMUM,
    O_MULTIPLY,
    O_NONE,
    ImageMath,
)
from cellprofiler.modules.maskimage import IO_IMAGE, IO_OBJECTS, MaskImage
from cellprofiler.modules.maskobjects import (
    MC_OBJECTS,
    P_REMOVE,
    R_RENUMBER,
    MaskObjects,
)
from cellprofiler.modules.measurecolocalization import (
    M_ACCURATE,
    M_FASTER,
    M_IMAGES,
    MeasureColocalization,
)
from cellprofiler.modules.measuregranularity import MeasureGranularity
from cellprofiler.modules.measureimageareaoccupied import (
    O_OBJECTS,
    MeasureImageAreaOccupied,
)
from cellprofiler.modules.measureimageintensity import MeasureImageIntensity
from cellprofiler.modules.measureimagequality import O_ALL_LOADED, MeasureImageQuality
from cellprofiler.modules.measureobjectintensity import MeasureObjectIntensity
from cellprofiler.modules.measureobjectintensitydistribution import (
    A_FRAC_AT_D,
    C_SELF,
    MeasureObjectIntensityDistribution,
)
from cellprofiler.modules.measureobjectneighbors import (
    D_ADJACENT,
    MeasureObjectNeighbors,
)
from cellprofiler.modules.measureobjectsizeshape import MeasureObjectSizeShape
from cellprofiler.modules.measureobjectskeleton import MeasureObjectSkeleton
from cellprofiler.modules.measuretexture import IO_BOTH, MeasureTexture
from cellprofiler.modules.morph import F_DISTANCE, R_ONCE, Morph
from cellprofiler.modules.morphologicalskeleton import MorphologicalSkeleton
from cellprofiler.modules.overlayoutlines import (
    MAX_IMAGE,
    WANTS_COLOR,
    WANTS_GRAYSCALE,
    OverlayOutlines,
)
from cellprofiler.modules.relateobjects import D_BOTH, RelateObjects
from cellprofiler.modules.rescaleintensity import (
    CUSTOM_VALUE,
    M_STRETCH,
    RescaleIntensity,
)
from cellprofiler.modules.resize import I_NEAREST_NEIGHBOR, R_BY_FACTOR, Resize
from cellprofiler.modules.resizeobjects import ResizeObjects
from cellprofiler.modules.saveimages import (
    AXIS_T,
    BIT_DEPTH_8,
    FF_PNG,
    FN_SINGLE_NAME,
    IF_IMAGE,
    WS_EVERY_CYCLE,
    SaveImages,
)
from cellprofiler.modules.threshold import (
    O_FOREGROUND,
    O_THREE_CLASS,
    O_TWO_CLASS,
    RB_MAD,
    RB_MEAN,
    RB_MEDIAN,
    RB_SD,
    TM_LI,
    TM_MANUAL,
    TM_OTSU,
    TM_ROBUST_BACKGROUND,
    TS_GLOBAL,
    Threshold,
)
from cellprofiler_core.constants.image import M_BOTH
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

from starrynight.algorithms.cp_plugin_callbarcodes import CallBarcodes
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
    cp_images_df: pl.DataFrame,
    cp_plate_channel_list: list[str],
    sbs_plate_channel_list: list[str],
    plate_cycles_list: list[str],
    cp_corr_images_path: Path | CloudPath,
    sbs_comp_images_path: Path | CloudPath,
    path_mask: str,
    f: TextIOWrapper,
) -> None:
    # setup csv headers and write the header first
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    metadata_heads = [f"Metadata_{col}" for col in ["Batch", "Plate", "Site", "Well"]]

    cp_filename_heads = [f"FileName_Corr{col}" for col in cp_plate_channel_list]
    cp_pathname_heads = [f"PathName_Corr{col}" for col in cp_plate_channel_list]
    sbs_filename_heads = [
        f"FileName_Cycle{int(cycle)}_{col}"
        for cycle in plate_cycles_list
        for col in sbs_plate_channel_list
    ]
    sbs_pathname_heads = [
        f"PathName_Cycle{int(cycle)}_{col}"
        for cycle in plate_cycles_list
        for col in sbs_plate_channel_list
    ]
    loaddata_writer.writerow(
        [
            *metadata_heads,
            *cp_filename_heads,
            *cp_pathname_heads,
            *sbs_filename_heads,
            *sbs_pathname_heads,
        ]
    )
    index = cp_images_df[0].to_dicts()[0]
    index = PCPIndex(**index)
    wells_sites = (
        cp_images_df.group_by("well_id").agg(pl.col("site_id").unique()).to_dicts()
    )
    for well_sites in wells_sites:
        index.well_id = well_sites["well_id"]
        for site_id in well_sites["site_id"]:
            index.site_id = site_id
            cp_filenames = [
                f"{index.batch_id}_{index.plate_id}_Well_{index.well_id}_Site_{int(index.site_id)}_Corr{col}.tiff"
                for col in cp_plate_channel_list
            ]
            sbs_filenames = [
                f"{index.batch_id}_{index.plate_id}_{int(cycle)}_Well_{index.well_id}_Site_{int(index.site_id)}_Compensated{col}.tiff"
                for col in sbs_plate_channel_list
                for cycle in plate_cycles_list
            ]
            cp_pathnames = [
                resolve_path_loaddata(AnyPath(path_mask), cp_corr_images_path)
                for _ in range(len(cp_pathname_heads))
            ]
            sbs_pathnames = [
                resolve_path_loaddata(AnyPath(path_mask), sbs_comp_images_path)
                for _ in range(len(sbs_pathname_heads))
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
                    # CP Filename and Pathname heads
                    *cp_filenames,
                    *cp_pathnames,
                    # SBS Filename and Pathname heads
                    *sbs_filenames,
                    *sbs_pathnames,
                ]
            )


def gen_analysis_load_data_by_batch_plate(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    cp_corr_images_path: Path | CloudPath | None = None,
    sbs_comp_images_path: Path | CloudPath | None = None,
) -> None:
    """Generate load data for analysis pipeline.

    Parameters
    ----------
    index_path : Path | CloudPath
        Path to index file.
    out_path : Path | CloudPath
        Path to save output csv file.
    path_mask : str | None
        Path prefix mask to use.
    cp_corr_images_path : Path | CloudPath
        Path | CloudPath to cp corr images directory.
    sbs_comp_images_path : Path | CloudPath
        Path | CloudPath to sbs compensated images directory.

    """
    # Construct illum path if not given
    if cp_corr_images_path is None:
        cp_corr_images_path = index_path.parents[1].joinpath("illum/cp/illum_apply")
    if sbs_comp_images_path is None:
        sbs_comp_images_path = index_path.parents[1].joinpath("preprocess/sbs")

    df = pl.read_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    cp_images_df = df.filter(
        pl.col("is_sbs_image").eq(False), pl.col("is_image").eq(True)
    )
    sbs_images_df = df.filter(
        pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True)
    )

    cp_images_hierarchy_dict = gen_image_hierarchy(cp_images_df)

    # Query default path prefix
    default_path_prefix = (
        cp_images_df.select("prefix").unique().to_series().to_list()[0]
    )

    # Setup path mask (required for resolving pathnames during the execution)
    if path_mask is None:
        path_mask = default_path_prefix

    # Setup chunking and write loaddata for each batch/plate
    for batch in cp_images_hierarchy_dict.keys():
        for plate in cp_images_hierarchy_dict[batch].keys():
            # Setup channel list for that plate
            cp_plate_channel_list = get_channels_by_batch_plate(
                cp_images_df, batch, plate
            )
            sbs_plate_channel_list = get_channels_by_batch_plate(
                sbs_images_df, batch, plate
            )

            # Get plate cycle list
            plate_cycles_list = get_cycles_by_batch_plate(sbs_images_df, batch, plate)

            # filter batch and plate images
            cp_df_plate = cp_images_df.filter(
                pl.col("batch_id").eq(batch) & pl.col("plate_id").eq(plate)
            )

            batch_plate_out_path = out_path.joinpath(batch, plate)
            batch_plate_out_path.mkdir(parents=True, exist_ok=True)
            with batch_plate_out_path.joinpath(f"preprocess_{batch}_{plate}.csv").open(
                "w"
            ) as f:
                write_loaddata(
                    cp_df_plate,
                    cp_plate_channel_list,
                    sbs_plate_channel_list,
                    plate_cycles_list,
                    cp_corr_images_path,
                    sbs_comp_images_path,
                    path_mask,
                    f,
                )


###################################
## CellProfiler pipeline generation
###################################


def generate_analysis_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
    barcode_csv_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
    mito_channel: str,
) -> Pipeline:
    load_data_df = pl.read_csv(load_data_path.resolve().__str__())
    cp_channel_list = list(
        # Remove duplicate channels
        set(
            [
                col.split("_")[-1].replace("Corr", "")
                for col in load_data_df.columns
                if col.startswith("FileName_Corr")
            ]
        )
    )
    sbs_channel_list = list(
        # Remove duplicate channels
        set(
            [
                col.split("_")[-1]
                for col in load_data_df.columns
                if col.startswith("FileName_Cycle")
            ]
        )
    )
    sbs_channel_list.remove(nuclei_channel)
    cycle_list = list(
        # Remove duplilcate cycels
        set(
            [
                int(col.split("_")[-2].replace("Cycle", ""))
                for col in load_data_df.columns
                if col.startswith("FileName_Cycle")
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
    # MeasureImageIntensity(CorrNuclei, Cycle1Nuclei)
    # -> FlagImage(Empty images)
    # -> Align(Cycle1Nuclei -> CorrNuclei, CorrOtherChannels)
    # -> Threshold (Cycle1Nuclei -> NonPaddedAreas)
    # -> Threshold (CorrNuclei -> NonPaddedAreas)
    # -> ImageMath ((NonPaddedAreasSBS, NonPaddedAreasCP) -> Min_NonPaddedAreasBoth)
    # -> ImageMath ((NonPaddedAreasSBS, NonPaddedAreasCP) -> Max_NonPaddedAreasBoth)
    # -> MaskImage (NucleiPainting -> EdgeMasked)
    # -> MaskImage (Cycle1Nuclei -> EdgeMasked)
    # -> MaskImage (Channel -> EdgeMasked)
    # -> MeasureColocalization (EdgeMaskedCycle1Nuclei, EdgeMaskedNuclei)
    # -> FlagImage(Alignment)
    # -> ImageMath (Invert, (PaddedAreasSBS, NonPaddedAreasAny))
    # -> Morph(Creates gradient of distance from foreground to background)
    # -> MeasureImageIntensity(PaddedAreasSBS)
    # -> ImageMath (Multiply, (WellEdgeDistance, WellEdgeDistancePreMultiply))
    # preserves morpths with well edge and zeros out spurious data
    # -> IdentifyPrimaryObjects (DAPI EdgedMasked, ConfluentRegions)
    # -> MeasureImageAreaOccupied (Objects, ConfluentRegions)
    # -> CalculateMath (Percent Confluent,  Divide)
    # -> for ch in (DAPI, Phalloidin): MaskImage(Image, ConfluentRegions)
    # -> IdentifyPrimaryObjects(MaskedDAPIPainting, Nuclei)
    # -> IdentifySecondaryObjects(MaksedPhalloidin, Cells)
    # -> IdentifyTertiaryObjects (Cells, Nuclei, Cytoplasm)
    # -> for obj in (ConfluentRegions, Cell, Nuclei): ResizeObjects(Objects, 0.5x)
    # -> OverlayOutlines(Celloutlines)
    # -> MaskImage (MaxOfCycle01, MaxOfCycle01_EdgeMasked)
    # -> IdentifyPrimaryObjects (MaxOfCycle01, Foci_PreMask)
    # -> MaskImage (Foci, ConfluentRegions)
    # -> FilterObjects (Foci, BarcodeFoci)
    # -> ResizeObjects (Foci, 0.5x)
    # -> for all cycles and channels: MeasureObjectIntensity
    # -> CallBarcodes(Foci)
    # -> ImageMath(BarcodeScores)
    # -> ImageMath(BarcodeScores)
    # -> MeasureObjectIntensity(BarcodeScores, Barcodes_Barcodes, Celloutlines)
    # -> MaskImage(BarcodeIntValue, BarcodeThres)
    # -> MaskImage(BarcodeFoci, BarcodeThres)
    # -> EnhanceOrSuppressFeatures (mito, MitoTubeness)
    # -> Threshold (MitoTubeness, mito_bw)
    # -> MorphologicalSkeleton (Nuclei, mito_skel)
    # -> MeasureObjectNeighbors (Cells, 10)
    # -> MeasureObjectNeighbors (Cells, 5)
    # -> MeasureObjectNeighbors (Nuclei, 2)
    # -> MeasureColocalization (cycle, dapi, Phalloidin)
    # -> FlagImage(PoorAlignment)
    # -> MeasureObjectIntensity( MaskedBarcodes, Cells)
    # -> MeasureObjectIntensity( Painting, (Cells, Nuclei, Cytoplasm))
    # -> MeasureObjectSizeShape(Cells, Cyto, Nuclei)
    # -> MeasureObjectIntensityDistribution (Painting)
    # -> MeasureObjectIntensityDistribution (mito_tubeness, mito_radial_heatmap)
    # -> MeasureGranularity (Painting, (Cells, Cyto, Nuclei))
    # -> MeasureTexture (Painting, (Cells, Cyto, Nuclei))
    # -> SaveImages(mito_radial_heatmap)
    # -> MeasureImageQuality(All loaded images)
    # -> MeasureColocalization (all cycles and channels)
    # -> FilterObjects(BarcodeFoci, Foci_NonCellEdge)
    # -> RelateObjects(Cells, BarcodeFoci)
    # -> Resize Images for Vis (Phalloidin, DAPI)
    # -> GraytoColor (Combine Painting for Vis)
    # -> OverlayOutlines(Resized Nuclei, Cells and Confluent)
    # -> SaveImages for Vis Alignment
    # -> Resize (MaxOfCycle01, MaxOfCycle01Spots)
    # -> RescaleIntensity(ResizedCycle01Spots)
    # -> OverlayOutlines (spotOverlay)
    # -> SaveImages (spotOverlay)
    # -> for obj in (Cells, Nuclei, Cyto): ConvertObjectsToImage(obj)
    # -> for img in (Cells, Nuclei, Cyto): SaveImages(img)
    # -> ExportToSpreadsheet(All measurements)

    # -> MeasureImageIntensity
    measure_image_intensity = MeasureImageIntensity()
    module_counter += 1
    measure_image_intensity.module_num = module_counter
    measure_image_intensity.images_list.value = (
        f"Corr{nuclei_channel}, Cycle1_{nuclei_channel}"
    )
    measure_image_intensity.wants_objects.value = False
    measure_image_intensity.objects_list.value = ""
    measure_image_intensity.wants_percentiles.value = False
    # measure_image_intensity.percentiles.value = ""
    pipeline.add_module(measure_image_intensity)

    # -> FlagImage (Empty Images)
    flag_empty_images = FlagImage()
    module_counter += 1
    flag_empty_images.module_num = module_counter

    images_to_flag = [f"Corr{nuclei_channel}", f"Cycle1_{nuclei_channel}"]

    # One flag is already created
    for _ in range(len(images_to_flag) - 1):
        flag_empty_images.add_flag()

    for i, flag_image in enumerate(images_to_flag):
        # Flag's category [3]
        flag_empty_images.flags[i].category.value = "Metadata"
        # Name of the flag [4]
        flag_empty_images.flags[i].feature_name.value = f"Empty_{flag_image}"
        # How should the measurements be linked [5]
        flag_empty_images.flags[i].combination_choice.value = C_ANY
        # Skip image set if flagged [6]
        flag_empty_images.flags[i].wants_skip.value = True

        # Measurement settings, One measurement is added by default for each flag
        flag_empty_images.flags[i].measurement_settings[0].source_choice.value = S_IMAGE
        flag_empty_images.flags[i].measurement_settings[0].object_name.value = None
        flag_empty_images.flags[i].measurement_settings[
            0
        ].measurement.value = f"Intensity_MaxIntensity_{flag_image}"
        flag_empty_images.flags[i].measurement_settings[0].wants_minimum.value = True
        flag_empty_images.flags[i].measurement_settings[
            0
        ].minimum_value.value = 0.000001
        flag_empty_images.flags[i].measurement_settings[0].wants_maximum.value = False
    pipeline.add_module(flag_empty_images)

    # -> Align
    align = Align()
    module_counter += 1
    align.module_num = module_counter
    align.alignment_method.value = M_CROSS_CORRELATION
    align.crop_mode.value = C_SAME_SIZE

    # make a copy of channel list and remove nuclei_channel
    align_channel_list = cp_channel_list.copy()
    align_channel_list.remove(nuclei_channel)
    align.first_input_image.value = f"Cycle1_{nuclei_channel}"
    align.first_output_image.value = "AlignedCycle1Nuclei"
    align.second_input_image.value = f"Corr{nuclei_channel}"
    align.second_output_image.value = f"Aligned{nuclei_channel}"

    for i, ch in enumerate(align_channel_list):
        align.add_image()
        align.additional_images[i].input_image_name.value = f"Corr{ch}"
        align.additional_images[i].output_image_name.value = f"Aligned{ch}"
        align.additional_images[i].align_choice.value = A_SIMILARLY
    pipeline.add_module(align)

    # -> Threshold
    images_to_threshold = [f"Aligned{nuclei_channel}", f"Cycle1_{nuclei_channel}"]
    for image in images_to_threshold:
        threshold_image = Threshold()
        module_counter += 1
        threshold_image.module_num = module_counter
        threshold_image.x_name.value = image
        threshold_image.y_name.value = f"NonPaddedAreas_{image}"
        threshold_image.threshold_scope.value = TS_GLOBAL
        threshold_image.global_operation.value = TM_MANUAL
        threshold_image.threshold_smoothing_scale.value = 0
        threshold_image.threshold_correction_factor.value = 1
        threshold_image.threshold_range.value = (0, 1)
        threshold_image.manual_threshold.value = 0.00001
        threshold_image.thresholding_measurement.value = None
        threshold_image.two_class_otsu.value = O_TWO_CLASS
        threshold_image.assign_middle_to_foreground.value = O_FOREGROUND
        threshold_image.lower_outlier_fraction.value = 0.05
        threshold_image.upper_outlier_fraction.value = 0.05
        threshold_image.averaging_method.value = RB_MEAN
        threshold_image.number_of_deviations.value = 2
        threshold_image.adaptive_window_size.value = 50
        threshold_image.log_transform.value = False
        pipeline.add_module(threshold_image)

    # Calculate Min and Max of f"NonPaddedAreas_{image}"
    images_to_minmax = [
        f"NonPaddedAreas_Aligned{nuclei_channel}",
        f"NonPaddedAreas_Cycle1_{nuclei_channel}",
    ]
    for op in [O_MINIMUM, O_MAXIMUM]:
        minmax = ImageMath()
        module_counter += 1
        minmax.module_num = module_counter
        minmax.operation.value = op
        minmax.exponent.value = 1
        minmax.after_factor.value = 1
        minmax.addend.value = 0
        minmax.truncate_low.value = True
        minmax.truncate_high.value = True
        minmax.replace_nan.value = True
        minmax.ignore_mask.value = False
        minmax.output_image_name.value = f"NonPaddedAreas_{op}"
        # Create all the image slots (two of the are initialized by default)
        for _ in range(len(images_to_minmax) - 2):
            minmax.add_image()
        # Add images
        for i, image in enumerate(images_to_minmax):
            # Image or measurement?
            minmax.images[i].image_or_measurement.value = IM_IMAGE
            # Image name
            minmax.images[i].image_name.value = image
            # Measurement
            minmax.images[i].measurement.value = ""
            # Factor
            minmax.images[i].factor.value = 1
        pipeline.add_module(minmax)

    # -> MaskImage (Nuclei, Cyto, Cycle01 -> EdgeMasked)
    images_to_mask = [
        f"Aligned{nuclei_channel}",
        f"Cycle1_{nuclei_channel}",
        f"Aligned{cell_channel}",
    ]
    for image in images_to_mask:
        mask_image_edge = MaskImage()
        module_counter += 1
        mask_image_edge.module_num = module_counter
        mask_image_edge.image_name.value = image
        mask_image_edge.masked_image_name.value = f"EdgeMasked_{image}"
        mask_image_edge.source_choice.value = IO_IMAGE
        mask_image_edge.object_name.value = f"PaddedObjects_{O_MINIMUM}"
        mask_image_edge.masking_image_name.value = f"NonPaddedAreas_{O_MINIMUM}"
        mask_image_edge.invert_mask.value = True
        pipeline.add_module(mask_image_edge)

    # -> MeasureColocalization (EdgeMaskedCycle1Nuclei, EdgeMaskedNuclei)
    measure_colocal = MeasureColocalization()
    module_counter += 1
    measure_colocal.module_num = module_counter
    measure_colocal.images_list.value = (
        f"EdgeMasked_Aligned{nuclei_channel}, EdgeMasked_Cycle1_{nuclei_channel}"
    )
    measure_colocal.thr.value = 15.0
    measure_colocal.images_or_objects.value = M_IMAGES
    measure_colocal.do_all.value = False
    measure_colocal.do_corr_and_slope.value = True
    measure_colocal.do_manders.value = False
    measure_colocal.do_rwc.value = False
    measure_colocal.do_overlap.value = False
    measure_colocal.do_costes.value = False
    measure_colocal.fast_costes.value = M_FASTER
    pipeline.add_module(measure_colocal)

    # -> FlagImage (Alignment)
    flag_align_images = FlagImage()
    module_counter += 1
    flag_align_images.module_num = module_counter
    # One flag is already created
    flag_align_images.flags[0].category.value = "Metadata"
    flag_align_images.flags[0].feature_name.value = "AlignmentFlag"
    flag_align_images.flags[0].combination_choice.value = C_ANY
    flag_align_images.flags[0].wants_skip.value = False

    # Measurement settings, One measurement is added by default for each flag
    flag_align_images.flags[0].measurement_settings[0].source_choice.value = S_IMAGE
    flag_align_images.flags[0].measurement_settings[0].object_name.value = None
    flag_align_images.flags[0].measurement_settings[
        0
    ].measurement.value = f"Correlation_Correlation_EdgeMasked_Aligned{nuclei_channel}_EdgeMasked_Cycle1_{nuclei_channel}"
    flag_align_images.flags[0].measurement_settings[0].wants_minimum.value = True
    flag_align_images.flags[0].measurement_settings[0].minimum_value.value = 0.7
    flag_align_images.flags[0].measurement_settings[0].wants_maximum.value = False
    pipeline.add_module(flag_align_images)

    # -> ImageMath invert edge mask
    invertedge = ImageMath()
    module_counter += 1
    invertedge.module_num = module_counter
    invertedge.operation.value = O_INVERT
    invertedge.exponent.value = 1
    invertedge.after_factor.value = 1
    invertedge.addend.value = 0
    invertedge.truncate_low.value = True
    invertedge.truncate_high.value = True
    invertedge.replace_nan.value = True
    invertedge.ignore_mask.value = False
    invertedge.output_image_name.value = "PaddedAreas_SBS"
    # two images are initialized by default
    # Image or measurement?
    invertedge.images[0].image_or_measurement.value = IM_IMAGE
    # Image name
    invertedge.images[0].image_name.value = f"NonPaddedAreas_{O_MAXIMUM}"
    # Measurement
    invertedge.images[0].measurement.value = ""
    # Factor
    invertedge.images[0].factor.value = 1
    pipeline.add_module(invertedge)

    # -> Morph (something related to edges is happening here)
    morph_edge = Morph()
    module_counter += 1
    morph_edge.module_num = module_counter
    morph_edge.image_name.value = f"NonPaddedAreas_Cycle1_{nuclei_channel}"
    morph_edge.output_image_name.value = "WellEdgeDistancePreMultiply"
    morph_edge.functions[0].function.value = F_DISTANCE
    morph_edge.functions[0].repeats_choice.value = R_ONCE
    morph_edge.functions[0].custom_repeats.value = 2
    morph_edge.functions[0].rescale_values.value = False
    pipeline.add_module(morph_edge)

    # -> MeasureImageIntensity (In binary padded areas)
    measure_image_intensity_padded = MeasureImageIntensity()
    module_counter += 1
    measure_image_intensity_padded.module_num = module_counter
    measure_image_intensity_padded.images_list.value = "PaddedAreas_SBS"
    measure_image_intensity_padded.wants_objects.value = False
    measure_image_intensity_padded.objects_list.value = ""
    measure_image_intensity_padded.wants_percentiles.value = False
    # measure_image_intensity_padded.percentiles.value = ""
    pipeline.add_module(measure_image_intensity_padded)

    # ImageMath
    edgepadding = ImageMath()
    module_counter += 1
    edgepadding.module_num = module_counter
    edgepadding.operation.value = O_MULTIPLY
    edgepadding.exponent.value = 1
    edgepadding.after_factor.value = 1
    edgepadding.addend.value = 0
    edgepadding.truncate_low.value = False
    edgepadding.truncate_high.value = False
    edgepadding.replace_nan.value = True
    edgepadding.ignore_mask.value = False
    edgepadding.output_image_name.value = "WellEdgeDistance"
    # two images are initialized by default
    # Image or measurement?
    edgepadding.images[0].image_or_measurement.value = IM_IMAGE
    # Image name
    edgepadding.images[0].image_name.value = "WellEdgeDistancePreMultiply"
    # Measurement
    edgepadding.images[0].measurement.value = ""
    # Factor
    edgepadding.images[0].factor.value = 1
    # Image or measurement?
    edgepadding.images[1].image_or_measurement.value = IM_MEASUREMENT
    # Image name
    edgepadding.images[1].image_name.value = None
    # Measurement
    edgepadding.images[1].measurement.value = "Intensity_MaxIntensity_PaddedAreas_SBS"
    # Factor
    edgepadding.images[1].factor.value = 1
    pipeline.add_module(edgepadding)

    # Confluent regions identification
    identify_primary_object_cfregions = IdentifyPrimaryObjects()
    module_counter += 1
    identify_primary_object_cfregions.module_num = module_counter
    identify_primary_object_cfregions.x_name.value = (
        f"EdgeMasked_Aligned{nuclei_channel}"
    )
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

    # MeasureImageAreaOccupied by ConfluentRegions
    measure_cfregion_area = MeasureImageAreaOccupied()
    module_counter += 1
    measure_cfregion_area.module_num = module_counter
    measure_cfregion_area.operand_choice.value = O_OBJECTS
    measure_cfregion_area.objects_list.value = "ConfluentRegions"
    pipeline.add_module(measure_cfregion_area)

    # Calculate Math Percent of image confluent
    calc_cfregion_pct = CalculateMath()
    module_counter += 1
    calc_cfregion_pct.module_num = module_counter
    calc_cfregion_pct.output_feature_name.value = "PercentConfluent"
    calc_cfregion_pct.operation.value = O_DIVIDE

    # Numerator
    calc_cfregion_pct.operands[0].operand_choice.value = MC_IMAGE
    calc_cfregion_pct.operands[0].operand_objects.value = None
    calc_cfregion_pct.operands[
        0
    ].operand_measurement.value = "AreaOccupied_AreaOccupied_ConfluentRegions"
    calc_cfregion_pct.operands[0].multiplicand.value = 100
    calc_cfregion_pct.operands[0].exponent.value = 1.0

    # Denominator
    calc_cfregion_pct.operands[1].operand_choice.value = MC_IMAGE
    calc_cfregion_pct.operands[1].operand_objects.value = None
    calc_cfregion_pct.operands[
        1
    ].operand_measurement.value = "AreaOccupied_TotalArea_ConfluentRegions"
    calc_cfregion_pct.operands[1].multiplicand.value = 1.0
    calc_cfregion_pct.operands[1].exponent.value = 1.0

    calc_cfregion_pct.wants_log.value = False
    calc_cfregion_pct.final_multiplicand.value = 1.0
    calc_cfregion_pct.final_exponent.value = 1.0
    calc_cfregion_pct.final_addend.value = 0

    calc_cfregion_pct.constrain_lower_bound.value = False
    calc_cfregion_pct.lower_bound.value = 0
    calc_cfregion_pct.constrain_upper_bound.value = False
    calc_cfregion_pct.upper_bound.value = 1.0
    calc_cfregion_pct.rounding.value = ROUNDING[0]
    pipeline.add_module(calc_cfregion_pct)

    # Masking confluentRegions in all channels
    for ch in [nuclei_channel, cell_channel]:
        mask_image_cfregion = MaskImage()
        module_counter += 1
        mask_image_cfregion.module_num = module_counter
        mask_image_cfregion.image_name.value = f"EdgeMasked_Aligned{ch}"
        mask_image_cfregion.masked_image_name.value = f"Masked{ch}"
        mask_image_cfregion.object_name.value = "ConfluentRegions"
        mask_image_cfregion.invert_mask.value = True
        pipeline.add_module(mask_image_cfregion)

    # IdentifyPrimaryObjects(Nuclei channel painting)
    identify_primary_object_nuclei = IdentifyPrimaryObjects()
    module_counter += 1
    identify_primary_object_nuclei.module_num = module_counter
    identify_primary_object_nuclei.x_name.value = f"EdgeMasked_Aligned{nuclei_channel}"
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
    identify_primary_object_nuclei.threshold.global_operation.value = TM_LI
    identify_primary_object_nuclei.threshold.local_operation.value = TM_LI
    identify_primary_object_nuclei.threshold.threshold_smoothing_scale.value = 1.3488
    identify_primary_object_nuclei.threshold.threshold_correction_factor.value = 1.4
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
        f"EdgeMasked_Aligned{cell_channel}"
    )
    identify_secondary_object_cells.distance_to_dilate.value = 10
    identify_secondary_object_cells.regularization_factor.value = 0.0005
    identify_secondary_object_cells.wants_discard_edge.value = False
    identify_secondary_object_cells.wants_discard_primary.value = False
    identify_secondary_object_cells.fill_holes.value = True
    identify_secondary_object_cells.new_primary_objects_name.value = "FilteredNuclei"
    identify_secondary_object_cells.threshold_setting_version.value = 12
    identify_secondary_object_cells.threshold.threshold_scope.value = TS_GLOBAL
    identify_secondary_object_cells.threshold.global_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.local_operation.value = TM_OTSU
    identify_secondary_object_cells.threshold.threshold_smoothing_scale.value = 2.0
    identify_secondary_object_cells.threshold.threshold_correction_factor.value = 1.0
    identify_secondary_object_cells.threshold.threshold_range.value = (
        0.012610598,
        0.021547333,
    )
    identify_secondary_object_cells.threshold.manual_threshold.value = 0.0
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

    # IdentifyTertiaryObjects (Cyto)
    identify_tertiary_object_cyto = IdentifyTertiaryObjects()
    module_counter += 1
    identify_tertiary_object_cyto.module_num = module_counter
    identify_tertiary_object_cyto.secondary_objects_name.value = "Cells"
    identify_tertiary_object_cyto.primary_objects_name.value = "Nuclei"
    identify_tertiary_object_cyto.subregion_objects_name.value = "Cytoplasm"
    identify_tertiary_object_cyto.shrink_primary.value = True
    pipeline.add_module(identify_tertiary_object_cyto)

    # Resize Objects (ConfluentRegions, Cells, Nuclei)
    objects_to_resize = ["ConfluentRegions", "Cells", "Nuclei"]
    for obj in objects_to_resize:
        resize_obj = ResizeObjects()
        module_counter += 1
        resize_obj.module_num = module_counter
        resize_obj.x_name.value = obj
        resize_obj.y_name.value = f"Resize{obj}"
        resize_obj.method.value = "Factor"
        resize_obj.factor_x.value = 0.50
        resize_obj.factor_y.value = 0.50
        resize_obj.factor_z.value = 0.50
        pipeline.add_module(resize_obj)

    # OverlayOutlines
    cell_outline_image = OverlayOutlines()
    module_counter += 1
    cell_outline_image.module_num = module_counter
    cell_outline_image.blank_image.value = True
    cell_outline_image.image_name.value = None
    cell_outline_image.output_image_name.value = "CellOutlineImage"
    cell_outline_image.line_mode.value = "Inner"
    cell_outline_image.wants_color.value = WANTS_GRAYSCALE
    cell_outline_image.max_type.value = MAX_IMAGE
    # 1 outline is already added during init
    cell_outline_image.outlines[0].objects_name.value = "Cells"
    cell_outline_image.outlines[0].color.value = "white"
    pipeline.add_module(cell_outline_image)

    # ImageMath MaxOfCycle01
    maxofcy01 = ImageMath()
    module_counter += 1
    maxofcy01.module_num = module_counter
    maxofcy01.operation.value = O_MAXIMUM
    maxofcy01.exponent.value = 1
    maxofcy01.after_factor.value = 1
    maxofcy01.addend.value = 0
    maxofcy01.truncate_low.value = True
    maxofcy01.truncate_high.value = True
    maxofcy01.replace_nan.value = True
    maxofcy01.ignore_mask.value = False
    maxofcy01.output_image_name.value = "MaxOfCycle01"
    # Create all the image slots (two of the are initialized by default)
    for _ in range(len(sbs_channel_list) - 2):
        maxofcy01.add_image()
    # Add images
    for i, ch in enumerate(sbs_channel_list):
        # Image or measurement?
        maxofcy01.images[i].image_or_measurement.value = IM_IMAGE
        # Image name
        maxofcy01.images[i].image_name.value = f"Cycle1_{ch}"
        # Measurement
        maxofcy01.images[i].measurement.value = ""
        # Factor
        maxofcy01.images[i].factor.value = 1
    pipeline.add_module(maxofcy01)

    # -> MaskImage maxofcy01
    mask_image_maxofcy01 = MaskImage()
    module_counter += 1
    mask_image_maxofcy01.module_num = module_counter
    mask_image_maxofcy01.image_name.value = "MaxOfCycle01"
    mask_image_maxofcy01.masked_image_name.value = "EdgeMasked_MaxOfCycle01"
    mask_image_maxofcy01.source_choice.value = IO_IMAGE
    mask_image_maxofcy01.object_name.value = "WellEdgeObjects"
    mask_image_maxofcy01.masking_image_name.value = f"NonPaddedAreas_{O_MINIMUM}"
    mask_image_maxofcy01.invert_mask.value = False
    pipeline.add_module(mask_image_maxofcy01)

    # IdentifyPrimaryObjects (Foci)
    identify_primary_object_foci = IdentifyPrimaryObjects()
    module_counter += 1
    identify_primary_object_foci.module_num = module_counter
    identify_primary_object_foci.x_name.value = "MaxOfCycle01"
    identify_primary_object_foci.y_name.value = "PreMask_Foci"
    identify_primary_object_foci.size_range.value = (7, 20)
    identify_primary_object_foci.exclude_size.value = True
    identify_primary_object_foci.exclude_border_objects.value = True
    identify_primary_object_foci.unclump_method.value = UN_INTENSITY
    identify_primary_object_foci.watershed_method.value = WA_INTENSITY
    identify_primary_object_foci.automatic_smoothing.value = False
    identify_primary_object_foci.smoothing_filter_size.value = 3.0
    identify_primary_object_foci.automatic_suppression.value = False
    identify_primary_object_foci.maxima_suppression_size.value = 4.0
    identify_primary_object_foci.low_res_maxima.value = True
    identify_primary_object_foci.fill_holes.value = FH_DECLUMP
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
    identify_primary_object_foci.threshold.threshold_correction_factor.value = 4.0
    identify_primary_object_foci.threshold.threshold_range.value = (0.0002, 1.0)
    identify_primary_object_foci.threshold.manual_threshold.value = 0.0
    identify_primary_object_foci.threshold.thresholding_measurement.value = None
    identify_primary_object_foci.threshold.two_class_otsu.value = O_THREE_CLASS
    identify_primary_object_foci.threshold.assign_middle_to_foreground.value = (
        O_FOREGROUND
    )
    identify_primary_object_foci.threshold.lower_outlier_fraction.value = 0.05
    identify_primary_object_foci.threshold.upper_outlier_fraction.value = 0.05
    identify_primary_object_foci.threshold.averaging_method.value = RB_MEDIAN
    identify_primary_object_foci.threshold.variance_method.value = RB_MAD
    identify_primary_object_foci.threshold.number_of_deviations.value = 3.0
    identify_primary_object_foci.threshold.adaptive_window_size.value = 50
    identify_primary_object_foci.threshold.log_transform.value = False
    pipeline.add_module(identify_primary_object_foci)

    # -> MaskObjects foci
    mask_object_foci = MaskObjects()
    module_counter += 1
    mask_object_foci.module_num = module_counter
    mask_object_foci.object_name.value = "PreMask_Foci"
    mask_object_foci.remaining_objects.value = "Foci"
    mask_object_foci.mask_choice.value = MC_OBJECTS
    mask_object_foci.masking_objects.value = "ConfluentRegions"
    mask_object_foci.masking_image.value = None
    mask_object_foci.wants_inverted_mask.value = False
    mask_object_foci.overlap_choice.value = P_REMOVE
    mask_object_foci.overlap_fraction.value = 0.5
    mask_object_foci.retain_or_renumber.value = R_RENUMBER
    pipeline.add_module(mask_object_foci)

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

    # -> ResizeObjects foci
    resize_obj = ResizeObjects()
    module_counter += 1
    resize_obj.module_num = module_counter
    resize_obj.x_name.value = "Foci"
    resize_obj.y_name.value = "ResizeFoci"
    resize_obj.method.value = "Factor"
    resize_obj.factor_x.value = 0.50
    resize_obj.factor_y.value = 0.50
    resize_obj.factor_z.value = 0.50
    pipeline.add_module(resize_obj)

    # -> MeasureObjectIntensity(for all channels and cycles and Foci)
    measure_object_intensity = MeasureObjectIntensity()
    module_counter += 1
    measure_object_intensity.module_num = module_counter
    measure_object_intensity.images_list.value = ", ".join(
        [f"Cycle{cycle}_{ch}" for ch in sbs_channel_list for cycle in cycle_list]
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
        f"Intensity_MaxIntensity_Cycle1_{sbs_channel_list[0]}"
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
        ["Barcodes_Scores", "Barcodes_Barcodes", "CellOutlineImage"]
    )
    measure_object_intensity_barcodes.objects_list.value = ", ".join(["BarcodeFoci"])
    pipeline.add_module(measure_object_intensity_barcodes)

    # -> MaskImage barcode intvals
    mask_image_bintvals = MaskImage()
    module_counter += 1
    mask_image_bintvals.module_num = module_counter
    mask_image_bintvals.image_name.value = "Barcodes_IntValues"
    mask_image_bintvals.masked_image_name.value = "Masked_Barcodes_IntValues"
    mask_image_bintvals.source_choice.value = IO_OBJECTS
    mask_image_bintvals.object_name.value = "BarcodeFoci"
    mask_image_bintvals.masking_image_name.value = "Barcode_Thresh"
    mask_image_bintvals.invert_mask.value = False
    pipeline.add_module(mask_image_bintvals)

    # -> MaskImage barcode scores intvals
    mask_image_bscore = MaskImage()
    module_counter += 1
    mask_image_bscore.module_num = module_counter
    mask_image_bscore.image_name.value = "Barcodes_Scores"
    mask_image_bscore.masked_image_name.value = "Masked_Barcodes_Scores_IntValues"
    mask_image_bscore.source_choice.value = IO_OBJECTS
    mask_image_bscore.object_name.value = "BarcodeFoci"
    mask_image_bscore.masking_image_name.value = "Barcode_Thresh"
    mask_image_bscore.invert_mask.value = False
    pipeline.add_module(mask_image_bscore)

    # Enhance or Suppress features
    eos_features = EnhanceOrSuppressFeatures()
    module_counter += 1
    eos_features.module_num = module_counter
    eos_features.x_name.value = f"Aligned{mito_channel}"
    eos_features.y_name.value = "mito_tubeness"
    eos_features.method.value = ENHANCE
    eos_features.object_size.value = 10
    eos_features.enhance_method.value = E_NEURITES
    eos_features.hole_size.value = (1, 10)
    eos_features.smoothing.value = 1.0
    eos_features.angle.value = 0.0
    eos_features.decay.value = 0.95
    eos_features.neurite_choice.value = N_TUBENESS
    eos_features.speckle_accuracy.value = S_FAST
    eos_features.wants_rescale.value = True
    pipeline.add_module(eos_features)

    # -> Threshold Mito
    threshold_mito = Threshold()
    module_counter += 1
    threshold_mito.module_num = module_counter
    threshold_mito.x_name.value = "mito_tubeness"
    threshold_mito.y_name.value = "mito_bw"
    threshold_mito.threshold_scope.value = TS_GLOBAL
    threshold_mito.global_operation.value = TM_LI
    threshold_mito.threshold_smoothing_scale.value = 1.3488
    threshold_mito.threshold_correction_factor.value = 1
    threshold_mito.threshold_range.value = (0, 1)
    threshold_mito.manual_threshold.value = 0.0
    threshold_mito.thresholding_measurement.value = None
    threshold_mito.two_class_otsu.value = O_TWO_CLASS
    threshold_mito.assign_middle_to_foreground.value = O_FOREGROUND
    threshold_mito.lower_outlier_fraction.value = 0.05
    threshold_mito.upper_outlier_fraction.value = 0.05
    threshold_mito.averaging_method.value = RB_MEAN
    threshold_mito.number_of_deviations.value = 2
    threshold_mito.adaptive_window_size.value = 10
    threshold_mito.log_transform.value = False
    pipeline.add_module(threshold_mito)

    # -> MorphologicalSkeleton
    morph_skel = MorphologicalSkeleton()
    module_counter += 1
    morph_skel.module_num = module_counter
    morph_skel.x_name.value = "mito_bw"
    morph_skel.y_name.value = "mito_skel"
    pipeline.add_module(morph_skel)

    # -> MeasureObjectSkeleton
    measure_obj_skel = MeasureObjectSkeleton()
    module_counter += 1
    measure_obj_skel.module_num = module_counter
    measure_obj_skel.seed_objects_name.value = "Nuclei"
    measure_obj_skel.image_name.value = "mito_skel"
    measure_obj_skel.wants_branchpoint_image.value = True
    measure_obj_skel.branchpoint_image_name.value = "BranchpointImage"
    measure_obj_skel.wants_to_fill_holes.value = True
    measure_obj_skel.maximum_hole_size.value = 10
    measure_obj_skel.wants_objskeleton_graph.value = False
    measure_obj_skel.intensity_image_name.value = None
    measure_obj_skel.directory.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
    measure_obj_skel.vertex_file_name.value = "vertices.csv"
    measure_obj_skel.edge_file_name.value = "edges.csv"
    pipeline.add_module(measure_obj_skel)

    # MeasureObjectNeighbors
    obj_neig_to_measure = [("Cells", 10), ("Cells", 5), ("Nuclei", 2)]
    for obj, param in obj_neig_to_measure:
        measure_obj_neigh = MeasureObjectNeighbors()
        module_counter += 1
        measure_obj_neigh.module_num = module_counter
        measure_obj_neigh.object_name.value = obj
        measure_obj_neigh.neighbors_name.value = obj
        measure_obj_neigh.distance_method.value = D_ADJACENT
        measure_obj_neigh.distance.value = param
        measure_obj_neigh.wants_count_image.value = False
        measure_obj_neigh.count_image_name.value = "ObjectNeighborCount"
        measure_obj_neigh.wants_percent_touching_image.value = False
        measure_obj_neigh.touching_image_name.value = "PercentTouching"
        measure_obj_neigh.wants_excluded_objects.value = True

        pipeline.add_module(measure_obj_neigh)

    # MeasureColocalization Cycle01Nuclei and Painting channels
    measure_colocal_cp_sbs = MeasureColocalization()
    module_counter += 1
    measure_colocal_cp_sbs.module_num = module_counter
    measure_colocal_cp_sbs.images_list.value = ", ".join(
        [f"Aligned{ch}" for ch in cp_channel_list] + [f"Cycle1_{nuclei_channel}"]
    )
    measure_colocal_cp_sbs.thr.value = 15.0
    measure_colocal_cp_sbs.images_or_objects.value = M_BOTH
    measure_colocal_cp_sbs.objects_list.value = "Cytoplasm, Cells, Nuclei"
    measure_colocal_cp_sbs.do_all.value = True
    measure_colocal_cp_sbs.do_corr_and_slope.value = True
    measure_colocal_cp_sbs.do_manders.value = False
    measure_colocal_cp_sbs.do_rwc.value = False
    measure_colocal_cp_sbs.do_overlap.value = True
    measure_colocal_cp_sbs.do_costes.value = False
    measure_colocal_cp_sbs.fast_costes.value = M_FASTER
    pipeline.add_module(measure_colocal_cp_sbs)

    # -> FlagImage (Alignment)
    flag_align_all_images = FlagImage()
    module_counter += 1
    flag_align_all_images.module_num = module_counter
    # One flag is already created
    flag_align_all_images.flags[0].category.value = "Metadata"
    flag_align_all_images.flags[0].feature_name.value = "PoorAlignment"
    flag_align_all_images.flags[0].combination_choice.value = C_ANY
    flag_align_all_images.flags[0].wants_skip.value = False

    # Measurement settings, One measurement is added by default for each flag
    flag_align_all_images.flags[0].measurement_settings[
        0
    ].source_choice.value = S_AVERAGE_OBJECT
    flag_align_all_images.flags[0].measurement_settings[0].object_name.value = "Nuclei"
    flag_align_all_images.flags[0].measurement_settings[
        0
    ].measurement.value = (
        f"Correlation_Correlation_Aligned{nuclei_channel}_Cycle1_{nuclei_channel}"
    )
    flag_align_all_images.flags[0].measurement_settings[0].wants_minimum.value = True
    flag_align_all_images.flags[0].measurement_settings[0].minimum_value.value = 0.9
    flag_align_all_images.flags[0].measurement_settings[0].wants_maximum.value = False
    pipeline.add_module(flag_align_all_images)

    # -> MeasureObjectIntensity(Barcode related)
    measure_barcode_object_intensity = MeasureObjectIntensity()
    module_counter += 1
    measure_barcode_object_intensity.module_num = module_counter
    measure_barcode_object_intensity.images_list.value = ", ".join(
        [
            "Masked_Barcodes_IntValues",
            "Masked_Barcodes_Scores_IntValues",
            "WellEdgeDistance",
        ]
    )
    measure_barcode_object_intensity.objects_list.value = ", ".join(["Cells"])
    pipeline.add_module(measure_barcode_object_intensity)

    # -> MeasureObjectIntensity(Barcode related)
    measure_painting_object_intensity = MeasureObjectIntensity()
    module_counter += 1
    measure_painting_object_intensity.module_num = module_counter
    measure_painting_object_intensity.images_list.value = ", ".join(
        [f"Aligned{ch}" for ch in cp_channel_list]
    )
    measure_painting_object_intensity.objects_list.value = ", ".join(
        ["Cells", "Cytoplasm", "Nuclei"]
    )
    pipeline.add_module(measure_painting_object_intensity)

    # -> MeasureObjectSizeShape
    measure_obj_size_shape = MeasureObjectSizeShape()
    module_counter += 1
    measure_obj_size_shape.module_num = module_counter
    measure_obj_size_shape.objects_list.value = ", ".join(
        ["Cells", "Cytoplasm", "Nuclei"]
    )
    measure_obj_size_shape.calculate_zernikes.value = True
    measure_obj_size_shape.calculate_advanced.value = True
    pipeline.add_module(measure_obj_size_shape)

    # -> MeasureObjectIntensityDistribution (Painting)
    measure_obj_int_dist_paint = MeasureObjectIntensityDistribution()
    module_counter += 1
    measure_obj_int_dist_paint.module_num = module_counter
    measure_obj_int_dist_paint.images_list.value = ", ".join(
        [f"Aligned{ch}" for ch in cp_channel_list]
    )
    measure_obj_int_dist_paint.wants_zernikes.value = False
    obj_int_dist_paint_painting = ["Cells", "Cytoplasm", "Nuclei"]
    for _ in range(len(obj_int_dist_paint_painting) - 1):  # one object is already added
        measure_obj_int_dist_paint.add_object(False)
    for i, obj in enumerate(obj_int_dist_paint_painting):
        measure_obj_int_dist_paint.objects[i].object_name.value = obj
        measure_obj_int_dist_paint.objects[i].center_choice.value = C_SELF
        measure_obj_int_dist_paint.objects[i].center_object_name.value = None
    measure_obj_int_dist_paint.bin_counts[0].wants_scaled.value = True
    measure_obj_int_dist_paint.bin_counts[0].bin_count.value = 4
    measure_obj_int_dist_paint.bin_counts[0].maximum_radius.value = 100
    pipeline.add_module(measure_obj_int_dist_paint)

    # -> MeasureObjectIntensityDistribution (mito)
    measure_obj_int_dist_mito = MeasureObjectIntensityDistribution()
    module_counter += 1
    measure_obj_int_dist_mito.module_num = module_counter
    measure_obj_int_dist_mito.images_list.value = ", ".join(["mito_tubeness"])
    measure_obj_int_dist_mito.wants_zernikes.value = False
    obj_int_dist_mito = [("Cells", True, 16, 100), ("Cytoplasm", False, 20, 200)]
    for _ in range(len(obj_int_dist_mito) - 1):  # one object is already added
        measure_obj_int_dist_mito.add_object(False)
        measure_obj_int_dist_mito.add_bin_count(False)
    for i, tup in enumerate(obj_int_dist_mito):
        measure_obj_int_dist_mito.objects[i].object_name.value = tup[0]
        measure_obj_int_dist_mito.objects[i].center_choice.value = C_SELF
        measure_obj_int_dist_mito.objects[i].center_object_name.value = "Nuclei"
        measure_obj_int_dist_mito.bin_counts[i].wants_scaled.value = tup[1]
        measure_obj_int_dist_mito.bin_counts[i].bin_count.value = tup[2]
        measure_obj_int_dist_mito.bin_counts[i].maximum_radius.value = tup[3]
    measure_obj_int_dist_mito.add_heatmap()
    measure_obj_int_dist_mito.heatmaps[0].image_name.value = None
    measure_obj_int_dist_mito.heatmaps[0].object_name.value = "Cytoplasm"
    measure_obj_int_dist_mito.heatmaps[0].bin_count.value = 16
    measure_obj_int_dist_mito.heatmaps[0].measurement.value = A_FRAC_AT_D
    measure_obj_int_dist_mito.heatmaps[0].wants_to_save_display.value = True
    measure_obj_int_dist_mito.heatmaps[0].display_name.value = "mito_radial_heatmap"
    pipeline.add_module(measure_obj_int_dist_mito)

    # -> MeasureGranularity
    measure_granularity = MeasureGranularity()
    module_counter += 1
    measure_granularity.module_num = module_counter
    measure_granularity.images_list.value = ", ".join(
        [f"Aligned{ch}" for ch in cp_channel_list]
    )
    measure_granularity.wants_objects.value = True
    measure_granularity.objects_list.value = ", ".join(["Cells", "Cytoplasm", "Nuclei"])
    measure_granularity.subsample_size.value = 0.25
    measure_granularity.image_sample_size.value = 0.25
    measure_granularity.element_size.value = 10
    measure_granularity.granular_spectrum_length.value = 16
    pipeline.add_module(measure_granularity)

    # -> MeasureTexture
    measure_texture = MeasureTexture()
    module_counter += 1
    measure_texture.module_num = module_counter
    measure_texture.images_list.value = ", ".join(
        [f"Aligned{ch}" for ch in cp_channel_list]
    )
    measure_texture.objects_list.value = ", ".join(["Cells", "Cytoplasm", "Nuclei"])
    measure_texture.gray_levels.value = 256
    for _ in range(2):  # we need 3, one is added by default
        measure_texture.add_scale()
    for param in [5, 10, 20]:
        measure_texture.scale_groups[i].scale.value = param
    measure_texture.images_or_objects.value = IO_BOTH
    pipeline.add_module(measure_texture)

    # -> SaveImage mito radial heatmap
    save_mito_radial = SaveImages()
    module_counter += 1
    save_mito_radial.module_num = module_counter
    save_mito_radial.save_image_or_figure.value = IF_IMAGE
    save_mito_radial.image_name.value = "mito_radial_heatmap"
    save_mito_radial.file_name_method.value = FN_SINGLE_NAME
    save_mito_radial.number_of_digits.value = 4
    save_mito_radial.wants_file_name_suffix.value = False
    save_mito_radial.file_name_suffix.value = ""
    save_mito_radial.file_format.value = FF_PNG
    save_mito_radial.pathname.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|heatmap"
    save_mito_radial.bit_depth.value = BIT_DEPTH_8
    save_mito_radial.overwrite.value = True
    save_mito_radial.when_to_save.value = WS_EVERY_CYCLE
    save_mito_radial.update_file_names.value = True
    save_mito_radial.create_subdirectories.value = False
    # save_mito_radial.root_dir.value = ""
    save_mito_radial.stack_axis.value = AXIS_T
    # save_mito_radial.tiff_compress.value = ""
    save_mito_radial.single_file_name.value = (
        f"\\g<Batch>_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_mito_radial_heatmap"
    )
    pipeline.add_module(save_mito_radial)

    # MeasureImageQuality
    measure_img_quality = MeasureImageQuality()
    module_counter += 1
    measure_img_quality.module_num = module_counter
    measure_img_quality.images_choice.value = O_ALL_LOADED
    measure_img_quality.image_groups[0].include_image_scalings.value = False
    measure_img_quality.image_groups[0].check_blur.value = False
    measure_img_quality.image_groups[0].scale_groups[0].scale.value = 50
    measure_img_quality.image_groups[0].check_saturation.value = True
    measure_img_quality.image_groups[0].check_intensity.value = True
    measure_img_quality.image_groups[0].calculate_threshold.value = False
    measure_img_quality.image_groups[0].use_all_threshold_methods.value = False
    pipeline.add_module(measure_img_quality)

    # MeasureColocalization sbs
    measure_colocal_sbs = MeasureColocalization()
    module_counter += 1
    measure_colocal_sbs.module_num = module_counter
    measure_colocal_sbs.images_list.value = ", ".join(
        [f"Cycle{cycle}_{ch}" for ch in sbs_channel_list for cycle in cycle_list]
    )
    measure_colocal_sbs.thr.value = 15.0
    measure_colocal_sbs.images_or_objects.value = M_IMAGES
    measure_colocal_sbs.objects_list.value = ""
    measure_colocal_sbs.do_all.value = False
    measure_colocal_sbs.do_corr_and_slope.value = True
    measure_colocal_sbs.do_manders.value = False
    measure_colocal_sbs.do_rwc.value = False
    measure_colocal_sbs.do_overlap.value = False
    measure_colocal_sbs.do_costes.value = False
    measure_colocal_sbs.fast_costes.value = M_ACCURATE
    pipeline.add_module(measure_colocal_sbs)

    # -> Filter objects Edge foci
    filter_edge_foci = FilterObjects()
    module_counter += 1
    filter_edge_foci.module_num = module_counter
    filter_edge_foci.x_name.value = "BarcodeFoci"
    filter_edge_foci.y_name.value = "Foci_NonCellEdge"
    filter_edge_foci.mode.value = MODE_MEASUREMENTS
    filter_edge_foci.filter_choice.value = FI_LIMITS
    filter_edge_foci.per_object_assignment.value = PO_BOTH
    filter_edge_foci.enclosing_object_name.value = None
    # Select the measurement to filter by
    filter_edge_foci.measurements[0].settings[
        0
    ].value = "Intensity_MaxIntensity_CellOutlineImage"
    # Filter using a minimum measurement value
    filter_edge_foci.measurements[0].settings[1].value = True
    # Minimum value
    filter_edge_foci.measurements[0].settings[2].value = 0.0
    # Filter using a maximum measurement value
    filter_edge_foci.measurements[0].settings[3].value = True
    # Maximum value
    filter_edge_foci.measurements[0].settings[4].value = 0.5
    pipeline.add_module(filter_edge_foci)

    # RelateObjects
    relate_objects = RelateObjects()
    module_counter += 1
    relate_objects.module_num = module_counter
    relate_objects.x_name.value = "Cells"
    relate_objects.y_name.value = "BarcodeFoci"
    relate_objects.find_parent_child_distances.value = D_BOTH
    relate_objects.wants_per_parent_means.value = True
    relate_objects.wants_step_parent_distances.value = False
    relate_objects.wants_child_objects_saved.value = True
    relate_objects.output_child_objects_name.value = "RelateObjects"
    pipeline.add_module(relate_objects)

    # Resize Objects (Painting nuclei and cyto channel)
    objects_to_resize = [f"Aligned{nuclei_channel}", f"Corr{cell_channel}"]
    for obj in objects_to_resize:
        resize_obj = ResizeObjects()
        module_counter += 1
        resize_obj.module_num = module_counter
        resize_obj.x_name.value = obj
        resize_obj.y_name.value = f"Resize{obj}Vis"
        resize_obj.method.value = "Factor"
        resize_obj.factor_x.value = 0.50
        resize_obj.factor_y.value = 0.50
        resize_obj.factor_z.value = 0.50
        pipeline.add_module(resize_obj)

    # GrayToColor
    gray_to_color = GrayToColor()
    module_counter += 1
    gray_to_color.module_num = module_counter
    gray_to_color.scheme_choice.value = SCHEME_RGB
    gray_to_color.wants_rescale.value = True
    gray_to_color.red_image_name.value = None
    gray_to_color.green_image_name.value = f"Resize{cell_channel}Vis"
    gray_to_color.blue_image_name.value = f"Resize{nuclei_channel}Vis"
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
        len(["ResizeNuclei", "ResizeCells", "ResizeConfluentRegions"]) - 1
    ):  # 1 outline is already added during init
        overlay_outlines.add_outline()

    colors = ["yellow", "white", "#FF8000"]
    for i, obj in enumerate(["ResizeNuclei", "ResizeCells", "ResizeConfluentRegions"]):
        overlay_outlines.outlines[i].objects_name.value = obj
        overlay_outlines.outlines[i].color.value = colors[i]
    pipeline.add_module(overlay_outlines)

    # Save image
    for img in ["ColorImage", "OrigOverlay"]:
        save_image = SaveImages()
        module_counter += 1
        save_image.module_num = module_counter
        save_image.save_image_or_figure.value = IF_IMAGE
        save_image.image_name.value = img
        save_image.file_name_method.value = FN_SINGLE_NAME
        save_image.number_of_digits.value = 4
        save_image.wants_file_name_suffix.value = False
        save_image.file_name_suffix.value = ""
        save_image.file_format.value = FF_PNG
        save_image.pathname.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
        save_image.bit_depth.value = BIT_DEPTH_8
        save_image.overwrite.value = False
        save_image.when_to_save.value = WS_EVERY_CYCLE
        save_image.update_file_names.value = False
        save_image.create_subdirectories.value = False
        # save_image.root_dir.value = ""
        save_image.stack_axis.value = AXIS_T
        # save_image.tiff_compress.value = ""
        save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_VisualizeAlignment{img}"
        pipeline.add_module(save_image)

    # Resize image
    resize = Resize()
    module_counter += 1
    resize.module_num = module_counter
    resize.x_name.value = "MaxOfCycle01"
    resize.y_name.value = "ResizedMaxOfCycle01"
    resize.size_method.value = R_BY_FACTOR
    resize.resizing_factor_x.value = 0.5
    resize.resizing_factor_y.value = 0.5
    resize.resizing_factor_z.value = 0.5
    resize.interpolation.value = I_NEAREST_NEIGHBOR
    pipeline.add_module(resize)

    # Rescale maxofcy01
    rescale = RescaleIntensity()
    module_counter += 1
    rescale.module_num = module_counter
    rescale.x_name.value = "ResizedMaxOfCycle01"
    rescale.y_name.value = "ResclaedMaxOfCycle01"
    rescale.rescale_method.value = M_STRETCH
    rescale.wants_automatic_low.value = CUSTOM_VALUE
    rescale.wants_automatic_high.value = CUSTOM_VALUE
    rescale.source_low.value = 0.0
    rescale.source_high.value = 1.0
    rescale.source_scale.value = (0.0, 1.0)
    rescale.dest_scale.value = (0.0, 1.0)
    rescale.matching_image_name.value = None
    rescale.divisor_value.value = 1.0
    rescale.divisor_measurement.value = None
    pipeline.add_module(rescale)

    # OverlayOutlines
    overlay_outlines = OverlayOutlines()
    module_counter += 1
    overlay_outlines.module_num = module_counter
    overlay_outlines.blank_image.value = False
    overlay_outlines.image_name.value = "ResclaedMaxOfCycle01"
    overlay_outlines.output_image_name.value = "SpotOverlay"
    overlay_outlines.line_mode.value = "Inner"
    overlay_outlines.wants_color.value = WANTS_COLOR
    overlay_outlines.max_type.value = MAX_IMAGE
    overlay_outlines.outlines[0].objects_name.value = "ResizeFoci"
    overlay_outlines.outlines[0].color.value = "Red"

    # Save resized spot overlay
    save_image = SaveImages()
    module_counter += 1
    save_image.module_num = module_counter
    save_image.save_image_or_figure.value = IF_IMAGE
    save_image.image_name.value = "SpotOverlay"
    save_image.file_name_method.value = FN_SINGLE_NAME
    save_image.number_of_digits.value = 4
    save_image.wants_file_name_suffix.value = False
    save_image.file_name_suffix.value = ""
    save_image.file_format.value = FF_PNG
    save_image.pathname.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
    save_image.bit_depth.value = BIT_DEPTH_8
    save_image.overwrite.value = False
    save_image.when_to_save.value = WS_EVERY_CYCLE
    save_image.update_file_names.value = False
    save_image.create_subdirectories.value = False
    # save_image.root_dir.value = ""
    save_image.stack_axis.value = AXIS_T
    # save_image.tiff_compress.value = ""
    save_image.single_file_name.value = "\\g<Batch>_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_VisualizeAlignment_SpotOverlay"
    pipeline.add_module(save_image)

    # ConvertObjectsToImage
    obj_to_img = ["Cells", "Cytoplasm", "Nuclei"]
    for obj in obj_to_img:
        convert_obj_to_img = ConvertObjectsToImage()
        module_counter += 1
        convert_obj_to_img.module_num = module_counter
        convert_obj_to_img.object_name.value = obj
        convert_obj_to_img.image_name.value = f"{obj}_Objects"
        convert_obj_to_img.image_mode.value = "unit16"
        pipeline.add_module(convert_obj_to_img)

    for img in ["Cells_Objects", "Cytoplasm_Objects", "Nuclei_Objects"]:
        save_image = SaveImages()
        module_counter += 1
        save_image.module_num = module_counter
        save_image.save_image_or_figure.value = IF_IMAGE
        save_image.image_name.value = img
        save_image.file_name_method.value = FN_SINGLE_NAME
        save_image.number_of_digits.value = 4
        save_image.wants_file_name_suffix.value = False
        save_image.file_name_suffix.value = ""
        save_image.file_format.value = FF_PNG
        save_image.pathname.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
        save_image.bit_depth.value = BIT_DEPTH_8
        save_image.overwrite.value = False
        save_image.when_to_save.value = WS_EVERY_CYCLE
        save_image.update_file_names.value = False
        save_image.create_subdirectories.value = False
        # save_image.root_dir.value = ""
        save_image.stack_axis.value = AXIS_T
        # save_image.tiff_compress.value = ""
        save_image.single_file_name.value = (
            f"\\g<Batch>_\\g<Plate>_Well_\\g<Well>_Site_\\g<Site>_{img}"
        )
        pipeline.add_module(save_image)

    # ExportToSpreadsheet
    export_measurements = ExportToSpreadsheet()
    module_counter += 1
    export_measurements.module_num = module_counter
    export_measurements.delimiter.value = DELIMITER_COMMA
    export_measurements.directory.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
    export_measurements.wants_prefix.value = True
    export_measurements.prefix.value = "Analysis_"
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

    return pipeline


def gen_analysis_cppipe_by_batch_plate(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    barcode_csv_path: Path | CloudPath,
    nuclei_channel: str,
    cell_channel: str,
    mito_channel: str,
) -> None:
    """Write out analysis pipeline to file.

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
    cell_channel : str
        Channel to use for cell segmentation
    mito_channel : str
        Channel to use for mito segmentation

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
                cpipe = generate_analysis_pipeline(
                    cpipe,
                    file,
                    barcode_csv_path,
                    nuclei_channel,
                    cell_channel,
                    mito_channel,
                )
                filename = f"{file.stem}.cppipe"
                with files_out_dir.joinpath(filename).open("w") as f:
                    cpipe.dump(f)
