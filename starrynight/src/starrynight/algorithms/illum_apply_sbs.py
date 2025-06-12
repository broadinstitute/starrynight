"""Merged Illum apply sbs commands."""

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

from starrynight.algorithms.index import PCPIndex
from starrynight.modules.sbs_illum_calc.constants import (
    SBS_ILLUM_CALC_OUT_PATH_SUFFIX,
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
from starrynight.utils.globbing import flatten_all, flatten_dict, get_files_by
from starrynight.utils.misc import resolve_path_loaddata

###############################
## Load data generation
###############################


def get_filename_header(
    cycle: int, ch: str, use_legacy: bool = False, legacy_channel_map: dict = {}
) -> str:
    if not use_legacy:
        return f"FileName_Orig_Cycle_{int(cycle)}_{ch}"
    else:
        return f"FileName_Cycle{int(cycle):02d}_Orig{legacy_channel_map[ch]}"


def get_pathname_header(
    cycle: int, ch: str, use_legacy: bool = False, legacy_channel_map: dict = {}
) -> str:
    if not use_legacy:
        return f"PathName_Orig_Cycle_{int(cycle)}_{ch}"
    else:
        return f"PathName_Cycle{int(cycle):02d}_Orig{legacy_channel_map[ch]}"


def get_frame_header(
    cycle: int, ch: str, use_legacy: bool = False, legacy_channel_map: dict = {}
) -> str:
    if not use_legacy:
        return f"Frame_Orig_Cycle_{int(cycle)}_{ch}"
    else:
        return f"Frame_Cycle{int(cycle):02d}_Orig{legacy_channel_map[ch]}"


def get_illum_pathname_header(
    cycle: int, ch: str, use_legacy: bool = False, legacy_channel_map: dict = {}
) -> str:
    if not use_legacy:
        return f"PathName_Illum_{int(cycle)}_{ch}"
    else:
        return f"PathName_Cycle{int(cycle):02d}_Illum{legacy_channel_map[ch]}"


def get_illum_filename_header(
    cycle: int, ch: str, use_legacy: bool = False, legacy_channel_map: dict = {}
) -> str:
    if not use_legacy:
        return f"FileName_Illum_{int(cycle)}_{ch}"
    else:
        return f"FileName_Cycle{int(cycle):02d}_Illum{legacy_channel_map[ch]}"


def write_loaddata_illum_apply(
    images_df: pl.LazyFrame,
    plate_cycles_list: list[str],
    plate_channel_list: list[str],
    illum_by_cycle_channel_dict: dict,
    metadata_to_index_dict: dict[str, PCPIndex],
    nuclei_channel: str,
    path_mask: str,
    f: TextIOWrapper,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
) -> None:
    loaddata_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    legacy_channel_map = {}

    if use_legacy:
        # Load experiment config
        exp_config = json.loads(exp_config_path.read_text())

        # setup legacy_channel_map
        legacy_channel_map = gen_legacy_channel_map(
            plate_channel_list, exp_config
        )

        # replace the ch in illum map
        for ch in plate_channel_list:
            for cycle in plate_cycles_list:
                old_val = illum_by_cycle_channel_dict[cycle][ch]
                illum_by_cycle_channel_dict[cycle][ch] = AnyPath(
                    old_val.resolve()
                    .__str__()
                    .replace(ch, legacy_channel_map[ch])
                )
    # Setup metadata headers
    metadata_heads = [
        f"Metadata_{col}"
        for col in ["Batch", "Plate", "Site", "Well", "Well_Value"]
    ]

    filename_heads = [
        get_filename_header(cycle, ch, use_legacy, legacy_channel_map)
        for ch in plate_channel_list
        for cycle in plate_cycles_list
    ]
    pathname_heads = [
        get_pathname_header(cycle, ch, use_legacy, legacy_channel_map)
        for ch in plate_channel_list
        for cycle in plate_cycles_list
    ]

    # We need frame heads because image channels are combined in a single image
    frame_heads = [
        get_frame_header(cycle, ch, use_legacy, legacy_channel_map)
        for ch in plate_channel_list
        for cycle in plate_cycles_list
    ]

    # Add Frame_Cycle##_Illum* columns
    # For non-legacy mode, use channel directly; for legacy mode, use mapped channel
    illum_frame_heads = [
        f"Frame_Cycle{int(cycle):02d}_Illum{legacy_channel_map.get(ch, ch) if use_legacy else ch}"
        for ch in plate_channel_list
        for cycle in plate_cycles_list
    ]

    # Add illum apply specific columns
    illum_pathname_heads = [
        get_illum_pathname_header(cycle, ch, use_legacy, legacy_channel_map)
        for ch in plate_channel_list
        for cycle in plate_cycles_list
    ]
    # Assuming that paths already resolve with the path mask applied
    illum_filename_heads = [
        get_illum_filename_header(cycle, ch, use_legacy, legacy_channel_map)
        for ch in plate_channel_list
        for cycle in plate_cycles_list
    ]

    loaddata_writer.writerow(
        [
            *metadata_heads,
            *filename_heads,
            *pathname_heads,
            *frame_heads,
            *illum_filename_heads,
            *illum_pathname_heads,
            *illum_frame_heads,
        ]
    )

    wells_sites = (
        images_df.collect()
        .group_by("well_id")
        .agg(pl.col("site_id").unique())
        .to_dicts()
    )
    for well_sites in wells_sites:
        well_id = well_sites["well_id"]
        for site_id in well_sites["site_id"]:
            sample_index = metadata_to_index_dict[f"1_{well_id}_{int(site_id)}"]

            # Construct file and pathnames with the metadata to index map
            filenames = [
                AnyPath(
                    metadata_to_index_dict[
                        f"{int(cycle)}_{well_id}_{int(site_id)}"
                    ].key
                ).name
                for _ in plate_channel_list
                for cycle in plate_cycles_list
            ]
            pathnames = [
                AnyPath(
                    resolve_path_loaddata(
                        AnyPath(path_mask), AnyPath(sample_index.key)
                    )
                ).parent
                for _ in range(len(pathname_heads))
            ]

            # map frame index with image channels
            assert sample_index.channel_dict is not None
            frame_index = [
                sample_index.channel_dict.index(ch)
                for ch in plate_channel_list
                for _ in plate_cycles_list
            ]

            # setup illums
            illum_pathname_values = [
                illum_by_cycle_channel_dict[cycle][ch]
                .parent.resolve()
                .__str__()
                for ch in plate_channel_list
                for cycle in plate_cycles_list
            ]
            illum_filename_values = [
                illum_by_cycle_channel_dict[cycle][ch].name.__str__()
                for ch in plate_channel_list
                for cycle in plate_cycles_list
            ]

            # Setup illum frame values (always 0 for illum files)
            illum_frame_values = ["0" for _ in illum_frame_heads]

            # Extract well value from well_id by stripping 'Well' prefix if present
            well_value = well_id[4:] if well_id.startswith("Well") else well_id

            # make sure frame heads are matched with their order in the filenames
            loaddata_writer.writerow(
                [
                    # Metadata heads
                    sample_index.batch_id,
                    sample_index.plate_id,
                    site_id,
                    well_id,
                    # Well_Value is always needed
                    well_value,
                    # Filename heads
                    *filenames,
                    # Pathname heads
                    *pathnames,
                    # Frame heads
                    *[str(i) for i in frame_index],
                    # illum filenames
                    *illum_filename_values,
                    # illum pathnames
                    *illum_pathname_values,
                    # illum frames
                    *illum_frame_values,
                ]
            )


def gen_illum_apply_sbs_load_data(
    index_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_mask: str | None,
    nuclei_channel: str,
    illum_path: Path | CloudPath | None = None,
    use_legacy: bool = False,
    exp_config_path: Path | CloudPath | None = None,
    uow_hierarchy: list[str] = None,
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
    illum_path : Path | CloudPath
        Path | CloudPath to generated illums directory.
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
            SBS_ILLUM_CALC_OUT_PATH_SUFFIX
        )

    # Load index
    df = pl.scan_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    images_df = filter_images(df, True)

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

        # Setup cycles list
        plate_cycles_list = get_cycles_from_df(level_df)

        # find illum files for this level
        illum_by_cycle_channel_dict = {
            cycle: {
                ch: illum_path.joinpath(
                    # INFO: This is not optimal, output form previous step is calculated per plate
                    # INFO: So, level[:2] is used and not just levels
                    f"{'-'.join(level[:2] + [str(cycle)])}/{level[1]}_Cycle{int(cycle)}_Illum{ch}.npy"
                )
                for ch in plate_channel_list
            }
            for cycle in plate_cycles_list
        }

        # gen metadata to index key dict
        metadata_to_index_dict = {}
        for image in level_df.collect().iter_rows(named=True):
            image = PCPIndex(**image)
            metadata_to_index_dict[
                f"{int(image.cycle_id)}_{image.well_id}_{int(image.site_id)}"
            ] = image

        # Construct filename for the loaddata csv
        level_out_path = out_path.joinpath(
            f"{'^'.join(level)}#illum_apply_sbs.csv"
        )

        with level_out_path.open("w") as f:
            write_loaddata_illum_apply(
                level_df,
                plate_cycles_list,
                plate_channel_list,
                illum_by_cycle_channel_dict,
                metadata_to_index_dict,
                nuclei_channel,
                path_mask,
                f,
                use_legacy,
                exp_config_path,
            )
    return out_path


###################################
## CellProfiler pipeline generation
###################################


def generate_illum_apply_sbs_pipeline(  # noqa: C901
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
    # correct_illum_calculate -> save(corrected)
    for cycle in cycle_list:
        correct_illum_apply = CorrectIlluminationApply()
        module_counter += 1
        correct_illum_apply.module_num = module_counter

        for ch in range(
            len(channel_list) - 1
        ):  # One image is already added by default
            correct_illum_apply.add_image()

        for i, ch in enumerate(channel_list):
            # image_name
            correct_illum_apply.images[i].settings[
                0
            ].value = f"Orig_Cycle_{cycle}_{ch}"
            # corrected_image_name
            correct_illum_apply.images[i].settings[
                1
            ].value = f"Corr_Cycle_{cycle}_{ch}"
            # illum correct function image name
            correct_illum_apply.images[i].settings[
                2
            ].value = f"Illum_{cycle}_{ch}"
            # how illum function is applied
            correct_illum_apply.images[i].settings[3] = DOS_DIVIDE
        pipeline.add_module(correct_illum_apply)

        for ch in channel_list:
            save_image = SaveImages()
            module_counter += 1
            save_image.module_num = module_counter
            save_image.save_image_or_figure.value = IF_IMAGE
            save_image.image_name.value = f"Corr_Cycle_{cycle}_{ch}"
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
            # save_image.stack_axis.value = AXIS_T
            # save_image.tiff_compress.value = ""

            save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_{cycle}_Well_\\g<Well>_Site_\\g<Site>_Corr{ch}"
            pipeline.add_module(save_image)

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
        align.first_output_image.value = (
            f"Aligned_Corr_Cycle_1_{nuclei_channel}"
        )
        align.second_input_image.value = f"Corr_Cycle_{cycle}_{nuclei_channel}"
        align.second_output_image.value = (
            f"Aligned_Corr_Cycle_{cycle}_{nuclei_channel}"
        )

        for i, ch in enumerate(align_channel_list):
            align.add_image()
            # input_image_name
            align.additional_images[i].settings[
                1
            ].value = f"Corr_Cycle_{cycle}_{ch}"
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
    measure_colocal_sbs.images_list.value = ", ".join(
        [
            f"Aligned_Corr_Cycle_{cycle}_{ch}"
            for ch in channel_list
            for cycle in cycle_list
        ]
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

    images_to_flag = [
        f"Aligned_Corr_Cycle_{cycle}_{nuclei_channel}" for cycle in cycle_list
    ]
    # skip checking cycle 1 nuclei
    images_to_flag.remove(f"Aligned_Corr_Cycle_1_{nuclei_channel}")
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
        flag_unaligned.flags[i].measurement_settings[
            0
        ].source_choice.value = S_IMAGE
        flag_unaligned.flags[i].measurement_settings[0].object_name.value = None
        flag_unaligned.flags[i].measurement_settings[
            0
        ].measurement.value = f"Correlation_Correlation_Aligned_Corr_Cycle_1_{nuclei_channel}_{flag_image}"
        flag_unaligned.flags[i].measurement_settings[
            0
        ].wants_minimum.value = True
        flag_unaligned.flags[i].measurement_settings[
            0
        ].minimum_value.value = 0.9
        flag_unaligned.flags[i].measurement_settings[
            0
        ].wants_maximum.value = False
    pipeline.add_module(flag_unaligned)

    # Save image (combined overlay)
    for cycle in cycle_list:
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
            save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_{cycle}_Well_\\g<Well>_Site_\\g<Site>_Aligned{ch}"
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


def gen_illum_apply_sbs_cppipe(
    load_data_path: Path | CloudPath,
    out_dir: Path | CloudPath,
    workspace_path: Path | CloudPath,
    nuclei_channel: str,
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
    use_legacy : bool
        Use legacy illumination apply pipeline.

    """
    # Default run dir should already be present, otherwise CP raises an error
    out_dir.mkdir(exist_ok=True, parents=True)

    filename = "illum_apply_sbs.cppipe"

    # Write old cppipe and return early if use_old is true
    if use_legacy:
        ref_cppipe = get_templates_path() / "cppipe/ref_6_BC_Apply_Illum.cppipe"

        out_dir.joinpath(filename).write_text(ref_cppipe.read_text())
        return

    # get one of the load data file for generating cppipe
    sample_loaddata_file = next(load_data_path.rglob("*.csv"))

    with CellProfilerContext(out_dir=workspace_path) as cpipe:
        cpipe = generate_illum_apply_sbs_pipeline(
            cpipe, sample_loaddata_file, nuclei_channel
        )
        with out_dir.joinpath(filename).open("w") as f:
            cpipe.dump(f)
        filename = "illum_apply_painting.json"
        with out_dir.joinpath(filename).open("w") as f:
            dumpit(cpipe, f, version=6)


# ------------------------------------------------------
# Run QC checks
# ------------------------------------------------------


def gen_illum_apply_qc(
    workspace_path: Path | CloudPath,
):
    pass


def run_illum_apply_qc():
    pass
