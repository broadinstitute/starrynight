"""Stitch and crop commands."""

import csv
from io import TextIOWrapper
from pathlib import Path
from typing import Any

import imagej
import numpy as np
import polars as pl
from cloudpathlib import AnyPath, CloudPath

from starrynight.algorithms.index import PCPIndex
from starrynight.utils.dfutils import (
    gen_image_hierarchy,
    get_channels_by_batch_plate,
    get_cycles_by_batch_plate,
)
from starrynight.utils.globbing import flatten_dict, get_files_by
from starrynight.utils.misc import resolve_path_loaddata
from starrynight.utils.pyimagej import ImagejContext

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
    metadata_heads = [
        f"Metadata_{col}" for col in ["Batch", "Plate", "Site", "Well"]
    ]

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

    with batch_plate_out_path.joinpath(f"align_{batch}_{plate}.csv").open(
        "w"
    ) as f:
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
    """Generate load data for stitch and crop pipeline.

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
        corr_images_path = index_path.parents[1].joinpath(
            "illum/sbs/illum_apply"
        )

    df = pl.read_parquet(index_path.resolve().__str__())

    # Filter for relevant images
    images_df = df.filter(
        pl.col("is_sbs_image").eq(True), pl.col("is_image").eq(True)
    )

    images_hierarchy_dict = gen_image_hierarchy(images_df)

    # Query default path prefix
    default_path_prefix = (
        images_df.select("prefix").unique().to_series().to_list()[0]
    )

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
## Fiji pipeline generation
###################################


def gen_tile_config(
    file_coord_tuple_list: list[tuple[str, tuple]], out_path: Path | CloudPath
) -> None:
    tile_config = f"dim = {len(file_coord_tuple_list[0][1])}\n"
    # filename; ; (x, y) # here x, y are pixel coordinates
    for file_path, coord in file_coord_tuple_list:
        tile_config += f"{file_path}; ; {coord}\n"
    with out_path.open("w") as f:
        f.write(tile_config)


def get_row_config(im_per_well: int) -> list[int]:
    im_per_well_dict = {
        "10": [10],
        "1396": [18, 22, 26, 28, 30, 32, 34, 36, 36, 38, 38, 40, 40, 40, 40]
        + [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]
        + [38, 38, 36, 36, 34, 32, 30, 28, 26, 22, 18],
        "1364": [8, 14, 18, 22, 26, 28, 30, 32, 34, 34, 36, 36, 38, 38]
        + [40, 40, 40, 42, 42, 42, 42, 42, 42, 42, 42, 40, 40, 40, 38, 38]
        + [36, 36, 34, 34, 32, 30, 28, 26, 22, 18, 14, 8],
        "1332": [14, 18, 22, 26, 28, 30, 32, 34, 34, 36, 36, 38, 38, 40, 40, 40]
        + [40, 40, 40, 40, 40, 40, 40]
        + [40, 40, 40, 40, 38, 38, 36, 36, 34, 34, 32, 30, 28, 26, 22, 18, 14],
        "394": [3, 7, 9, 11, 11, 13, 13, 15, 15, 15, 17, 17, 17, 17, 17]
        + [17, 17, 17, 17, 17, 15, 15, 15, 13, 13, 11, 11, 9, 7, 3],
        "320": [4, 8, 12, 14, 16, 18, 18, 20, 20, 20]
        + [20, 20, 20, 20, 18, 18, 16, 14, 12, 8, 4],
        "316": [6, 10, 14, 16, 16, 18, 18, 20, 20]
        + [20, 20, 20, 20, 18, 18, 16, 16, 14, 10, 6],
        "293": [7, 11, 13, 15, 17, 17, 19, 19, 19, 19]
        + [19, 19, 19, 17, 17, 15, 13, 11, 7],
        "256": [6, 10, 12, 14, 16, 16, 18, 18, 18]
        + [18, 18, 18, 16, 16, 14, 12, 10, 6],
        "88": [6, 8, 10, 10, 10, 10, 10, 10, 8, 6],
        "52": [4, 6, 8, 8, 8, 8, 6, 4],
    }
    return im_per_well_dict[str(im_per_well)]


def save_image_fiji(
    ij, image: Any, out_path: Path, compress: bool = False
) -> None:
    plugin = "Bio-Formats Exporter"
    params = {
        # "imageid": image.getID(),
        "save": "./custom.tif",
        # "export": True,
        "compression": "Uncompressed",
    }
    print(params)
    print(type(image))
    print(image.shape)
    ij.py.run_plugin(plugin, params, imp=image)
    # image.close()


def call_grid_stitch_fiji(ij, params: dict) -> None:
    plugin = "Grid/Collection stitching"
    ij.py.run_plugin(plugin, params)


def stitch_images_fiji(
    ij,
    sorted_imgs_list: list,
    tile_config: Path | CloudPath,
    out_dir: Path | CloudPath,
    tile_overlap_pct: int = 10,
):
    # fetch row config
    row_config = get_row_config(len(sorted_imgs_list))

    # get image shape and generate approx img file coordinates
    img_shape = ij.io().open(sorted_imgs_list[0].resolve().__str__()).shape
    file_coord_tuple_list = []
    agg = 0
    for i, _ in enumerate(row_config):
        y_offset = img_shape[1] * i
        for j in range(row_config[i]):
            x_offset = (img_shape[0]) / 2 * j
            file_coord_tuple_list.append(
                (sorted_imgs_list[agg].name, (x_offset, y_offset))
            )
            agg += 1

    # Generate tile config
    gen_tile_config(file_coord_tuple_list, tile_config)

    # Setup stitching params
    params = {
        "type": "Positions from file",
        "order": "Defined by TileConfiguration",
        "directory": tile_config.parent.resolve().__str__(),
        "layout_file": tile_config.name,
        "fusion_method": "Linear Blending",
        "regression_threshold": "0.30",
        "max/avg_displacement_threshold": "2.50",
        "absolute_displacement_threshold": "3.50",
        "tile_overlap": tile_overlap_pct,
        "compute_overlap": True,
        "computation_parameters": "Save computation time (but use more RAM)",
        "image_output": "Keep output virtual",
        "output_directory": out_dir.resolve().__str__(),
        # "ignore_z_stage": True,
    }
    call_grid_stitch_fiji(ij, params)
