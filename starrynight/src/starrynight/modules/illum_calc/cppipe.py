"""Illumination Calculate."""

from pathlib import Path

import polars as pl
from cellprofiler.modules.correctilluminationcalculate import (
    EA_ALL_ACROSS,
    FI_MANUALLY,
    IC_REGULAR,
    SM_MEDIAN_FILTER,
    CorrectIlluminationCalculate,
)
from cellprofiler.modules.resize import C_MANUAL, I_BILINEAR, R_BY_FACTOR, Resize
from cellprofiler.modules.saveimages import (
    AXIS_T,
    FF_NPY,
    FN_SINGLE_NAME,
    IF_IMAGE,
    WS_LAST_CYCLE,
    SaveImages,
)
from cellprofiler_core.constants.modules.load_data import (
    ABSOLUTE_FOLDER_NAME,
    DEFAULT_OUTPUT_FOLDER_NAME,
    NO_FOLDER_NAME,
)
from cellprofiler_core.modules.loaddata import LoadData
from cellprofiler_core.pipeline import Pipeline
from centrosome.bg_compensate import MODE_AUTO
from cloudpathlib import CloudPath

# from starrynight.experiment import PCPGeneric
from starrynight.utils.cellprofiler import CellProfilerContext


def generate_illum_calculate_pipeline(
    pipeline: Pipeline,
    load_data_path: Path | CloudPath,
) -> Pipeline:
    load_data_df = pl.read_csv(load_data_path.resolve().__str__())
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
    load_data.metadata_fields.value = "Plate"
    load_data.rescale.value = True
    pipeline.add_module(load_data)

    # INFO: Create and configure required resize(downsample) -> correct_illum_calculate -> resize(upsample)
    # -> save(upsample) modules -> create batch
    for col in [
        col.split("_")[1] for col in load_data_df.columns if col.startswith("FileName_")
    ]:
        resize_down = Resize()
        module_counter += 1
        resize_down.module_num = module_counter
        resize_down.x_name.value = f"{col}"
        resize_down.y_name.value = f"Downsampled{col}"
        resize_down.size_method.value = R_BY_FACTOR
        resize_down.resizing_factor_x.value = 0.25
        resize_down.resizing_factor_y.value = 0.25
        # resize_down.resizing_factor_z.value = ""
        resize_down.specific_width.value = 100
        resize_down.specific_height.value = 100
        # resize_down.specific_planes.value = ""
        resize_down.interpolation.value = I_BILINEAR
        resize_down.use_manual_or_image.value = C_MANUAL
        resize_down.specific_image.value = None
        resize_down.additional_image_count.value = "0"
        pipeline.add_module(resize_down)

        correct_illum_calculate = CorrectIlluminationCalculate()
        module_counter += 1
        correct_illum_calculate.module_num = module_counter
        correct_illum_calculate.image_name.value = f"Downsampled{col}"
        correct_illum_calculate.illumination_image_name.value = f"Illum{col}"
        correct_illum_calculate.intensity_choice.value = IC_REGULAR
        correct_illum_calculate.dilate_objects.value = False
        correct_illum_calculate.object_dilation_radius.value = 1
        correct_illum_calculate.block_size.value = 60
        correct_illum_calculate.rescale_option.value = "Yes"
        correct_illum_calculate.each_or_all.value = EA_ALL_ACROSS
        correct_illum_calculate.smoothing_method.value = SM_MEDIAN_FILTER
        correct_illum_calculate.automatic_object_width.value = FI_MANUALLY
        correct_illum_calculate.object_width.value = 10
        correct_illum_calculate.size_of_smoothing_filter.value = 20
        correct_illum_calculate.save_average_image.value = False
        correct_illum_calculate.average_image_name.value = "IllumBlueAvg"
        correct_illum_calculate.save_dilated_image.value = False
        correct_illum_calculate.dilated_image_name.value = "IllumBlueDilated"
        correct_illum_calculate.automatic_splines.value = True
        correct_illum_calculate.spline_bg_mode.value = MODE_AUTO
        correct_illum_calculate.spline_points.value = 5
        correct_illum_calculate.spline_threshold.value = 2
        correct_illum_calculate.spline_rescale.value = 2
        correct_illum_calculate.spline_maximum_iterations.value = 40
        correct_illum_calculate.spline_convergence.value = 0.001
        pipeline.add_module(correct_illum_calculate)

        resize_up = Resize()
        module_counter += 1
        resize_up.module_num = module_counter
        resize_up.x_name.value = f"Illum{col}"
        resize_up.y_name.value = f"UpsampledIllum{col}"
        resize_up.size_method.value = R_BY_FACTOR
        resize_up.resizing_factor_x.value = 4
        resize_up.resizing_factor_y.value = 4
        # resize_up.resizing_factor_z.value = ""
        resize_up.specific_width.value = 100
        resize_up.specific_height.value = 100
        # resize_up.specific_planes.value = ""
        resize_up.interpolation.value = I_BILINEAR
        resize_up.use_manual_or_image.value = C_MANUAL
        resize_up.specific_image.value = None
        resize_up.additional_image_count.value = "0"
        pipeline.add_module(resize_up)

        save_image = SaveImages()
        module_counter += 1
        save_image.module_num = module_counter
        save_image.save_image_or_figure.value = IF_IMAGE
        save_image.image_name.value = f"UpsampledIllum{col}"
        save_image.file_name_method.value = FN_SINGLE_NAME
        # save_image.file_image_name.value = ""
        save_image.single_file_name.value = f"\\g<Plate>_Illum{col}"
        save_image.number_of_digits.value = 4
        save_image.wants_file_name_suffix.value = False
        save_image.file_name_suffix.value = ""
        save_image.file_format.value = FF_NPY
        save_image.pathname.value = f"{DEFAULT_OUTPUT_FOLDER_NAME}|"
        # save_image.bit_depth.value = ""
        save_image.overwrite.value = False
        save_image.when_to_save.value = WS_LAST_CYCLE
        save_image.update_file_names.value = False
        save_image.create_subdirectories.value = False
        # save_image.root_dir.value = ""
        save_image.stack_axis.value = AXIS_T
        # save_image.tiff_compress.value = ""
        pipeline.add_module(save_image)

    # create_batch_files = CreateBatchFiles()
    # module_counter += 1
    # create_batch_files.module_num = module_counter
    # create_batch_files.wants_default_output_directory.value = True
    # # create_batch_files.custom_output_directory.value = ""
    # create_batch_files.remote_host_is_windows.value = False
    # create_batch_files.batch_mode.value = False
    # create_batch_files.distributed_mode.value = False
    # # create_batch_files.default_image_directory.value = ""
    # create_batch_files.revision.value = 0
    # create_batch_files.from_old_matlab.value = False
    # pipeline.add_module(create_batch_files)

    return pipeline


def write_illum_calculate_pipeline(
    load_data_path: Path | CloudPath,
    write_path: Path | CloudPath,
    run_path: Path | CloudPath,
) -> None:
    """Write out illumination calculate pipeline to file.

    Parameters
    ----------
    load_data_path : Path | CloudPath
        Path | CloudPath to load data csv.
    write_path : Path | CloudPath
        Path | CloudPath to write pipeline to.
    run_path : Path | CloudPath
        Path | CloudPath to run directory.

    """
    # Default run dir should already be present, otherwise CP raises an error
    write_path.mkdir(exist_ok=True, parents=True)
    with CellProfilerContext(out_dir=run_path) as cpipe:
        cpipe = generate_illum_calculate_pipeline(cpipe, load_data_path)
        with write_path.joinpath("illum_calc.cppipe").open("w") as f:
            cpipe.dump(f)
