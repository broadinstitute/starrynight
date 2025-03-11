"""Alignment commands."""

import csv
from io import TextIOWrapper
from pathlib import Path

import polars as pl

# from cellprofiler.modules.exporttospreadsheet import (
#     DELIMITER_COMMA,
#     GP_NAME_METADATA,
#     NANS_AS_NANS,
#     ExportToSpreadsheet,
# )
# from cellprofiler.modules.flagimage import FlagImage
# from cellprofiler.modules.measurecolocalization import MeasureColocalization
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

###############################
## Load data generation
###############################


def resolve_path(path_mask: Path | CloudPath, filepath: Path | CloudPath) -> str:
    try:
        rel_path = filepath.relative_to(path_mask)
        return path_mask.joinpath(rel_path).resolve().__str__()
    except ValueError:
        return f"{path_mask.resolve().rstrip('/')}/{filepath.resolve().lstrip('/')}/"


def write_loaddata(
    images_df: pl.DataFrame,
    plate_channel_list: list[str],
    corr_images_path: Path | CloudPath,
    nuclei_channel: str,
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
    cycle1_nuclei_filename_head = "FileName_CorrCycle1Nuclei"
    cycle1_nuclei_pathname_head = "PathName_CorrCycle1Nuclei"
    loaddata_writer.writerow(
        [
            *metadata_heads,
            *filename_heads,
            *pathname_heads,
            cycle1_nuclei_filename_head,
            cycle1_nuclei_pathname_head,
        ]
    )
    for index in images_df.to_dicts():
        index = PCPIndex(**index)
        filenames = [
            f"{index.batch_id}_{index.plate_id}_{int(index.cycle_id)}_Well_{index.well_id}_Site_{int(index.site_id)}_Corr{col}.tiff"
            for col in plate_channel_list
        ]
        cycle1_nuclei_filename = f"{index.batch_id}_{index.plate_id}_1_Well_{index.well_id}_Site_{int(index.site_id)}_Corr{nuclei_channel}.tiff"
        pathnames = [
            resolve_path(AnyPath(path_mask), corr_images_path)
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
                # cycle 1 filename
                cycle1_nuclei_filename,
                # cycle 1 pathname
                pathnames[0],
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
        f"align_{batch}_{plate}_{int(cycle):02}.csv"
    ).open("w") as f:
        write_loaddata(
            df_batch_plate_cycle,
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
    images_df = df.filter(
        pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True)
    ).sample(fraction=0.1)

    images_hierarchy_dict = gen_image_hierarchy(images_df)

    # Query default path prefix
    default_path_prefix = images_df.select("prefix").unique().to_series().to_list()[0]

    # Setup path mask (required for resolving pathnames during the execution)
    if path_mask is None:
        path_mask = default_path_prefix

    # Setup chunking and write loaddata for each batch/plate
    for batch in images_hierarchy_dict.keys():
        for plate in images_hierarchy_dict[batch].keys():
            # Write loaddata assuming image nesting with cycles
            plate_cycles_list = get_cycles_by_batch_plate(images_df, batch, plate)
            # remove the first cycle (not required for alignment)
            plate_cycles_list.remove("1")
            for cycle in plate_cycles_list:
                write_loaddata_csv_by_batch_plate_cycle(
                    images_df,
                    out_path,
                    corr_images_path,
                    nuclei_channel,
                    path_mask,
                    batch,
                    plate,
                    cycle,
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
    channel_list = [
        col.split("_")[1].replace("Corr", "")
        for col in load_data_df.columns
        if col.startswith("FileName")
    ]
    # remove the extra channel only needed for alignment
    channel_list.remove("Cycle1Nuclei")

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
    load_data.metadata_fields.value = "Batch,Plate,Cycle"
    load_data.rescale.value = True
    pipeline.add_module(load_data)

    # INFO: Create and configure required modules
    # Align(to cycle 0 nuclei channel) -> MeasureColocalization -> FlagImage
    # -> save(aligned images) -> ExportToSpreadsheet

    align = Align()
    module_counter += 1
    align.module_num = module_counter
    align.alignment_method.value = M_CROSS_CORRELATION
    align.crop_mode.value = C_SAME_SIZE

    # make a copy of channel list and remove nuclei_channel
    align_channel_list = channel_list.copy()
    align_channel_list.remove(nuclei_channel)
    align.first_input_image.value = "CorrCycle1Nuclei"
    align.first_output_image.value = "AlignedCorrCycle1Nuclei"
    align.second_input_image.value = f"Corr{nuclei_channel}"
    align.second_output_image.value = f"Aligned{nuclei_channel}"

    for i, ch in enumerate(align_channel_list):
        align.add_image()
        # input_image_name
        align.additional_images[i].settings[1].value = f"Corr{ch}"
        # output_image_name
        align.additional_images[i].settings[2].value = f"Aligned{ch}"
        # align_choice
        align.additional_images[i].settings[3].value = A_SIMILARLY
    pipeline.add_module(align)

    # Save image (combined overlay)
    for ch in channel_list:
        save_image = SaveImages()
        module_counter += 1
        save_image.module_num = module_counter
        save_image.save_image_or_figure.value = IF_IMAGE
        save_image.image_name.value = f"Aligned{ch}"
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
        save_image.single_file_name.value = f"\\g<Batch>_\\g<Plate>_\\g<Cycle>_Well_\\g<Well>_Site_\\g<Site>_Aligned{ch}"
        pipeline.add_module(save_image)

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
