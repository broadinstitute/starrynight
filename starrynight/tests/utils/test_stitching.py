"""Test stitching module."""

from pathlib import Path
from typing import Any

import polars as pl
import scyjava as sj
from cloudpathlib import AnyPath, CloudPath

from starrynight.utils.pyimagej import ImagejContext


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
        "256": [
            6,
            10,
            12,
            14,
            16,
            16,
            18,
            18,
            18,
            18,
            18,
            18,
            16,
            16,
            14,
            12,
            10,
            6,
        ],
        "88": [6, 8, 10, 10, 10, 10, 10, 10, 8, 6],
        "52": [4, 6, 8, 8, 8, 8, 6, 4],
    }
    return im_per_well_dict[str(im_per_well)]


def save_image_fiji(
    ij, image: object, out_path: Path, compress: bool = False
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
    img_shape = ij.io().open(image_files[0].resolve().__str__()).shape
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


if __name__ == "__main__":
    with ImagejContext() as ij:
        image_files = [
            Path(f"../fixtures/stitch_images/{i}.tif") for i in range(1, 11)
        ]
        stitch_images_fiji(
            ij,
            image_files,
            Path("../fixtures/stitch_images/").joinpath("tile_config.txt"),
            Path(),
            tile_overlap_pct=50,
        )
        output = ij.py.active_imageplus()
        print("Image id")
        print(output.getID())
        save_image_fiji(ij, output, Path().joinpath("custom.tif"))
