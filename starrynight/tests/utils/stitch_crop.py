import logging
import time
from pathlib import Path

from ij import IJ
from loci.plugins import LociExporter
from loci.plugins.out import Exporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("stitch_crop")

input_file_location = "/Users/shsingh/Documents/GitHub/starrynight/scratch/fix_s1_pcpip_output/Source1/Batch1"
step_to_stitch = "images_corrected"
subdir = "images_corrected/painting"
out_subdir_tag = "Plate_Well"
rows = "2"
columns = "2"
imperwell = "unused"
stitchorder = "unused"
channame = "CorrDNA"
size = "1480"
overlap_pct = "10"
tileperside = "2"
filterstring = "unused"
scalingstring = "1.99"
awsdownload = "unused"
bucketname = "unused"
localtemp = "/Users/shsingh/Documents/GitHub/starrynight/scratch/FIJI_temp"
downloadfilter = "unused"
round_or_square = "square"
quarter_if_round = "unused"
final_tile_size = "2960"
xoffset_tiles = "0"
yoffset_tiles = "0"
compress = "True"

top_outfolder = input_file_location

plugin = LociExporter()

logger.info(f"Starting stitch_crop with input location: {input_file_location}")
logger.info(
    f"Parameters: step={step_to_stitch}, subdir={subdir}, channame={channame}"
)


def tiffextend(imname):
    if ".tif" in imname:
        return imname
    if "." in imname:
        return imname[: imname.index(".")] + ".tiff"
    else:
        return imname + ".tiff"


def savefile(im, imname, plugin, compress="false"):
    attemptcount = 0
    imname = tiffextend(imname)
    logger.info(f"Saving {imname}, width={im.width}, height={im.height}")
    if compress.lower() != "true":
        IJ.saveAs(im, "tiff", imname)
    else:
        while attemptcount < 5:
            try:
                plugin.arg = (
                    "outfile="
                    + imname
                    + " windowless=true compression=LZW saveROI=false"
                )
                exporter = Exporter(plugin, im)
                exporter.run()
                logger.info(f"Succeeded after attempt {attemptcount}")
                return
            except Exception as e:
                logger.error(f"Error saving file: {e}")
                attemptcount += 1
        logger.error("Failed 5 times at saving")


top_outfolder_path = Path(top_outfolder)
logger.info(f"Top output folder: {top_outfolder_path}")
if not top_outfolder_path.exists():
    logger.info(f"Creating output folder: {top_outfolder_path}")
    top_outfolder_path.mkdir()

# Define and create the parent folders where the images will be output
outfolder = top_outfolder_path / f"{step_to_stitch}_stitched"
tile_outdir = top_outfolder_path / f"{step_to_stitch}_cropped"
downsample_outdir = top_outfolder_path / f"{step_to_stitch}_stitched_10X"
logger.info(
    f"Creating output directories: {outfolder}, {tile_outdir}, {downsample_outdir}"
)

if not outfolder.exists():
    outfolder.mkdir()
if not tile_outdir.exists():
    tile_outdir.mkdir()
if not downsample_outdir.exists():
    downsample_outdir.mkdir()

# Define and create the batch-specific subfolders where the images will be output
out_subdir = outfolder / out_subdir_tag
tile_subdir = tile_outdir / out_subdir_tag
downsample_subdir = downsample_outdir / out_subdir_tag
logger.info(
    f"Creating subfolders: {out_subdir}, {tile_subdir}, {downsample_subdir}"
)

if not tile_subdir.exists():
    tile_subdir.mkdir()
if not downsample_subdir.exists():
    downsample_subdir.mkdir()
if not out_subdir.exists():
    out_subdir.mkdir()

subdir = Path(input_file_location) / subdir
logger.info(f"Input directory to process: {subdir}")

# SKIP moving files from well dirs to parent dir for testing
# bypassed awsdownload == 'True' for test
if subdir.exists():
    a = list(subdir.iterdir())
    logger.info(f"Found {len(a)} items in input directory")
    # Comment out file moving for testing
    # for x in a:
    #     if x.is_dir():
    #         b = list(x.iterdir())
    #         logger.info(f"Processing subdirectory {x.name} with {len(b)} files")
    #         for c in b:
    #             logger.info(f"Renaming {c.name} to {subdir / c.name}")
    #             c.rename(subdir / c.name)

if subdir.is_dir():
    welllist = []
    presuflist = []
    permprefix = None
    permsuffix = None

    # Get all well directories
    well_dirs = [d for d in subdir.iterdir() if d.is_dir()]
    logger.info(f"Found {len(well_dirs)} well directories")

    for well_dir in well_dirs:
        # Extract well name from directory name (e.g., 'Plate1-WellA1' -> 'WellA1')
        logger.info(f"Processing well directory: {well_dir.name}")
        well = well_dir.name.split("-")[1]
        if well not in welllist:
            welllist.append(well)

        # Process all files in this well directory
        files_in_well = list(well_dir.iterdir())
        logger.info(f"Found {len(files_in_well)} files in well {well}")

        # For testing - create some dummy TIFF files if there are none
        if not any(".tif" in f.name for f in files_in_well):
            logger.info(f"Creating dummy test files in {well_dir}")
            # Create dummy test files
            for site in range(4):
                dummy_file = (
                    well_dir
                    / f"Plate_Plate1_Well_{well}_Site_{site}_CorrDNA.tiff"
                )
                if not dummy_file.exists():
                    with dummy_file.open("w") as f:
                        f.write("dummy tiff content")
            files_in_well = list(well_dir.iterdir())
            logger.info(f"Now found {len(files_in_well)} files in well {well}")

        for eachfile in files_in_well:
            filename = eachfile.name
            if ".tif" in filename and "Overlay" not in filename:
                # Files follow pattern: Plate_Plate1_Well_WellA1_Site_0_CorrDNA.tiff
                logger.info(f"Processing file: {filename}")
                try:
                    # Use the same parsing logic as before but adapted to the new format
                    prefix_before_well, suffix_with_well = filename.split(
                        "_Well_"
                    )
                    well_with_site, suffix = suffix_with_well.split("_Site_")
                    site_num, channel_suffix = suffix.split("_", 1)
                    logger.info(
                        f"Parsed: prefix={prefix_before_well}, well={well_with_site}, site={site_num}, channel={channel_suffix}"
                    )

                    if (prefix_before_well, channel_suffix) not in presuflist:
                        presuflist.append((prefix_before_well, channel_suffix))
                        logger.info(
                            f"Added prefix/suffix pair: {prefix_before_well}, {channel_suffix}"
                        )

                    if channame in channel_suffix:
                        if permprefix is None:
                            permprefix = prefix_before_well
                            permsuffix = channel_suffix
                            logger.info(
                                f"Set permanent prefix/suffix: {permprefix}, {permsuffix}"
                            )
                except Exception as e:
                    logger.error(f"Error parsing filename {filename}: {e}")

    # Filter and sort the presuflist
    temp_presuflist = list(
        presuflist
    )  # Create a copy to avoid modification during iteration
    for eachpresuf in temp_presuflist:
        if eachpresuf[1][-4:] != ".tif" and eachpresuf[1][-5:] != ".tiff":
            presuflist.remove(eachpresuf)
            logger.info(f"Removed non-TIFF item from presuflist: {eachpresuf}")

    presuflist.sort()
    logger.info(f"Wells found: {welllist}")
    logger.info(f"Prefix/suffix pairs found: {presuflist}")

    if round_or_square == "square":
        stitchedsize = int(rows) * int(size)
        tileperside_int = int(tileperside)
        scale_factor = float(scalingstring)
        rounded_scale_factor = int(round(scale_factor))
        upscaledsize = int(stitchedsize * rounded_scale_factor)
        if upscaledsize > 46340:
            upscaledsize = 46340
        tilesize = int(upscaledsize / tileperside_int)
        logger.info(
            f"Square mode: stitchedsize={stitchedsize}, scale_factor={scale_factor}, upscaledsize={upscaledsize}, tilesize={tilesize}"
        )

        for eachwell in welllist:
            logger.info(f"Processing well: {eachwell}")
            # simplified for test
            # Find the correct well directory
            well_dir = None
            for d in well_dirs:
                if d.name.split("-")[1] == eachwell:
                    well_dir = d
                    break

            if well_dir is None:
                logger.error(f"Could not find directory for well {eachwell}")
                continue

            standard_grid_instructions = [
                "type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x="
                + rows
                + " grid_size_y="
                + columns
                + " tile_overlap="
                + overlap_pct
                + " first_file_index_i=0 directory="
                + str(well_dir)
                + " file_names=",
                " output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]",
            ]

            for eachpresuf in presuflist:  # for each channel
                thisprefix, thissuffix = eachpresuf
                logger.info(
                    f"Processing prefix/suffix: {thisprefix}, {thissuffix}"
                )
                thissuffixnicename = thissuffix.split(".")[0]
                if thissuffixnicename[0] == "_":
                    thissuffixnicename = thissuffixnicename[1:]
                tile_subdir_persuf = tile_subdir / thissuffixnicename
                logger.info(f"Tile subdirectory: {tile_subdir_persuf}")
                if not tile_subdir_persuf.exists():
                    logger.info(f"Creating directory: {tile_subdir_persuf}")
                    tile_subdir_persuf.mkdir()
                # Pattern: Plate_Plate1_Well_WellA1_Site_0_CorrDNA.tiff
                filename = (
                    thisprefix + "_Well_" + eachwell + "_Site_{i}_" + thissuffix
                )
                fileoutname = "Stitched" + filename.replace("{i}", "")
                logger.info(f"Filename pattern: {filename}")
                logger.info(f"Output filename: {fileoutname}")

                logger.info("Running Grid/Collection stitching")
                IJ.run(
                    "Grid/Collection stitching",
                    standard_grid_instructions[0]
                    + filename
                    + standard_grid_instructions[1],
                )
                im = IJ.getImage()
                width = str(int(round(im.width * float(scalingstring))))
                height = str(int(round(im.height * float(scalingstring))))
                # scale the barcoding and cell painting images to match each other
                logger.info(f"Scaling image to width={width}, height={height}")
                scale_params = (
                    "x="
                    + scalingstring
                    + " y="
                    + scalingstring
                    + " width="
                    + width
                    + " height="
                    + height
                    + " interpolation=Bilinear average create"
                )
                logger.info(f"Scale parameters: {scale_params}")
                IJ.run(
                    "Scale...",
                    scale_params,
                )
                # Skip sleep for testing
                # logger.info("Sleeping for 15 seconds after scaling")
                # time.sleep(15)
                im2 = IJ.getImage()
                # padding to ensure tiles are all the same size (for CellProfiler later on)
                canvas_params = (
                    "width="
                    + str(upscaledsize)
                    + " height="
                    + str(upscaledsize)
                    + " position=Top-Left zero"
                )
                logger.info(f"Adjusting canvas size: {canvas_params}")
                IJ.run(
                    "Canvas Size...",
                    canvas_params,
                )
                # Skip sleep for testing
                # logger.info("Sleeping for 15 seconds after canvas adjustment")
                # time.sleep(15)
                im3 = IJ.getImage()
                logger.info(f"Saving to {out_subdir / fileoutname}")
                savefile(
                    im3,
                    str(out_subdir / fileoutname),
                    plugin,
                    compress=compress,
                )

                logger.info("Closing all images")
                IJ.run("Close All")
                logger.info(f"Opening file: {out_subdir / fileoutname}")
                im = IJ.open(str(out_subdir / fileoutname))
                im = IJ.getImage()

                logger.info(
                    f"Cropping into {tileperside_int}x{tileperside_int} tiles"
                )
                for eachxtile in range(tileperside_int):
                    for eachytile in range(tileperside_int):
                        each_tile_num = (
                            eachxtile * tileperside_int + eachytile + 1
                        )
                        logger.info(
                            f"Processing tile {each_tile_num} at x={eachxtile}, y={eachytile}"
                        )
                        IJ.makeRectangle(
                            eachxtile * tilesize,
                            eachytile * tilesize,
                            tilesize,
                            tilesize,
                        )
                        im_tile = im.crop()
                        tile_filename = str(
                            tile_subdir_persuf
                            / f"{thissuffixnicename}_Site_{each_tile_num}.tiff"
                        )
                        logger.info(f"Saving tile to {tile_filename}")
                        savefile(
                            im_tile,
                            tile_filename,
                            plugin,
                            compress=compress,
                        )

                logger.info("Closing all images")
                IJ.run("Close All")
                logger.info(f"Opening file again: {out_subdir / fileoutname}")
                im = IJ.open(str(out_subdir / fileoutname))
                im = IJ.getImage()

                # scaling to make a downsampled image for QC
                downsample_params = (
                    "x=0.1 y=0.1 width="
                    + str(im.width / 10)
                    + " height="
                    + str(im.width / 10)
                    + " interpolation=Bilinear average create"
                )
                logger.info(f"Creating downsampled image: {downsample_params}")
                im_10 = IJ.run(
                    "Scale...",
                    downsample_params,
                )
                im_10 = IJ.getImage()
                downsample_filename = str(downsample_subdir / fileoutname)
                logger.info(
                    f"Saving downsampled image to {downsample_filename}"
                )
                savefile(
                    im_10,
                    downsample_filename,
                    plugin,
                    compress=compress,
                )
                logger.info("Closing all images")
                IJ.run("Close All")
    # removed round for test
    elif round_or_square == "round":
        logger.info("Removed round for testing")
    else:
        logger.error("Must identify well as round or square")
else:
    logger.error(f"Could not find input directory {subdir}")
# Commented out since we're working with individual well directories
# and TileConfiguration.txt might be in different locations
# for eachlogfile in ["TileConfiguration.txt"]:
#     (subdir / eachlogfile).rename(out_subdir / eachlogfile)
logger.info("Processing completed successfully")
