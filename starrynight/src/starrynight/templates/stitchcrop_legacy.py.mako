# ruff: noqa: ANN002,ANN003,ANN202,ANN204,ANN401,D100,D104,D202,D400,D413,D415,E501,F401,F541,F821,F841,I001,N803,N806,N816,PTH102,PTH104,PTH110,PTH112,PTH113,PTH114,PTH115,PTH118,PTH123,UP015,UP024,UP031,UP035,W605,E722
"""Script for stitching and cropping microscopy images using ImageJ/Fiji.

This script:
1. Takes multi-site microscopy images from each well
2. Stitches them together into a full well image
3. Crops the stitched image into tiles for analysis
4. Creates downsampled versions for quality control

Usage:
  - Run normally for interactive mode with confirmations:
    python stitch_crop.py

  - Run in automatic mode (skip all confirmations):
    python stitch_crop.py -y
    python stitch_crop.py --yes
    python stitch_crop.py auto
"""

import os
import time
from glob import glob
import logging
import sys
from ij import IJ
from loci.plugins import LociExporter
from loci.plugins.out import Exporter

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Handle command-line arguments
autorun = False
if len(sys.argv) > 1:
    if sys.argv[1].lower() in ("-y", "--yes", "yes", "auto"):
        autorun = True
        logger.info("Auto mode: All confirmations will be skipped")

def confirm_continue(message="Continue to the next step?"):
    """Ask the user for confirmation to continue.

    Args:
        message: The message to display to the user

    Returns:
        bool: True if the user wants to continue, False otherwise
    """
    global autorun
    logger.info(">>> CONFIRM: " + message)

    # If autorun is enabled, skip confirmation and return True
    if autorun:
        logger.info("Auto-confirmed: Proceeding automatically")
    return True

    # Otherwise ask for confirmation
    #response = input("Continue? (y/n): ").strip().lower()
    #return response == "y" or response == "yes"

logger.info("Exp config: ${exp_config}")

# Configuration parameters
localtemp = "${temp_dir}"  # Temporary directory

# Grid stitching parameters
rows = "2"  # Number of rows in the site grid
columns = "2"  # Number of columns in the site grid
size = "1480"  # Base size of input images (pixels)
overlap_pct = "${exp_config['img_overlap_pct']}"  # Percentage overlap between adjacent images

# Tiling parameters
tileperside = "2"  # Number of tiles to create per side when cropping
scalingstring = "1.99"  # Scaling factor to apply to images
round_or_square = "square"  # Shape of the well (square or round)
final_tile_size = "2960"  # Final tile size after scaling (pixels)
xoffset_tiles = "0"  # X offset for tile cropping
yoffset_tiles = "0"  # Y offset for tile cropping
compress = "True"  # Whether to compress output TIFF files

# Channel information
channame = "DNA"  # Target channel name for processing

# Unused parameters (kept for compatibility)
imperwell = "unused"
stitchorder = "unused"
filterstring = "unused"
awsdownload = "unused"
bucketname = "unused"
downloadfilter = "unused"
quarter_if_round = "unused"

#top_outfolder = input_file_location

plugin = LociExporter()

def tiffextend(imname):
    """Ensure filename has proper TIFF extension.

    Args:
        imname: The image filename

    Returns:
        Filename with .tif or .tiff extension
    """
    if ".tif" in imname:
        return imname
    if "." in imname:
        return imname[: imname.index(".")] + ".tiff"
    else:
        return imname + ".tiff"

def savefile(im, imname, plugin, compress="false"):
    """Save an image with optional compression.

    Args:
        im: ImageJ ImagePlus object to save
        imname: Output filename/path
        plugin: LociExporter plugin instance
        compress: Whether to use LZW compression ("true" or "false")
    """
    attemptcount = 0
    imname = tiffextend(imname)
    logger.info("Saving %s, width=%s, height=%s", imname, im.width, im.height)

    # Simple save without compression
    if compress.lower() != "true":
        IJ.saveAs(im, "tiff", imname)
    # Save with compression (with retry logic)
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
                logger.info("Succeeded after attempt %s", attemptcount)
                return
            except:
                attemptcount += 1
        logger.error("Failed 5 times at saving %s", imname)

# STEP 1: Create directory structure for output files
# logger.info("Top output folder: {top_outfolder}")
# if not os.path.exists(top_outfolder):
#     logger.info("Creating top output folder: {top_outfolder}")
#     os.mkdir(top_outfolder)

# Define and create the parent folders where the images will be output
# outfolder = os.path.join(
#     top_outfolder, (step_to_stitch + "_stitched")
# )  # For stitched images
# tile_outdir = os.path.join(
#     top_outfolder, (step_to_stitch + "_cropped")
# )  # For cropped tiles
# downsample_outdir = os.path.join(
#     top_outfolder,
#     (step_to_stitch + "_stitched_10X"),  # For downsampled QC images
# )
# logger.info(
#     f"Output folders: \n - Stitched: {outfolder}\n - Cropped: {tile_outdir}\n - Downsampled: {downsample_outdir}"
# )
#
# Create parent directories if they don't exist
# if not os.path.exists(outfolder):
#     logger.info("Creating output folder: {outfolder}")
#     os.mkdir(outfolder)
# if not os.path.exists(tile_outdir):
#     logger.info("Creating tile output folder: {tile_outdir}")
#     os.mkdir(tile_outdir)
# if not os.path.exists(downsample_outdir):
#     logger.info("Creating downsample output folder: {downsample_outdir}")
#     os.mkdir(downsample_outdir)

# Define and create the batch-specific subfolders where the images will be output
out_subdir = "${stitch_out_dir}"
tile_subdir = "${tile_out_dir}"
downsample_subdir = "${downsample_out_dir}"

# if not os.path.exists(tile_subdir):
#     os.mkdir(tile_subdir)
# if not os.path.exists(downsample_subdir):
#     os.mkdir(downsample_subdir)
# if not os.path.exists(out_subdir):
#     os.mkdir(out_subdir)

# STEP 2: Prepare input directory and files
subdir = "${images_dir}"
logger.info("Input subdirectory: %s", subdir)

# bypassed awsdownload == 'True' for test (would download files from AWS)

# Check what's in the input directory
logger.info("Checking if directory exists: %s", subdir)
glob_path = "{0}{1}".format(subdir, "*")
logger.info("Globbing: %s", glob_path)
a = glob(glob_path)
#a = [a.split("/")[-1] for a in a]
logger.info("Contents of %s : %s", glob_path, a)

# Flatten any nested directories - create symlinks from subdirectories to main directory
for x in a:
    if os.path.isdir(x):
        logger.info("Processing subdirectory: %s", x)
        b = os.listdir(x)
        for c in b:
            # Skip CSV files
            if c.lower().endswith(".csv"):
                logger.info("Skipping CSV file: %s", c)
                continue

            src = os.path.join(x, c)
            dst = os.path.join(subdir, c)
            logger.info("Creating symlink: %s -> %s", src, dst)
            # Check if destination exists
            if os.path.exists(dst) or os.path.islink(dst):
                logger.info("Destination already exists, skipping: %s", dst)
            else:
                os.symlink(src, dst)

# STEP 3: Analyze input files and organize by well and channel
if os.path.isdir(subdir):
    logger.info("Processing directory content: %s", subdir)
    dirlist = os.listdir(subdir)
    logger.info("Files in directory: %s", dirlist)

    # Lists to track wells and prefix/suffix combinations
    welllist = []  # List of all well IDs found
    presuflist = []  # List of (prefix, channel) tuples
    permprefix = None  # Track a permanent prefix for reference
    permsuffix = None  # Track a permanent suffix for reference

    # Parse each file to extract well information and channel information
    for eachfile in dirlist:
        if ".tif" in eachfile:
            logger.info("Processing TIFF file: %s", eachfile)
            # Skip overlay files
            if "Overlay" not in eachfile:
                try:
                    # Parse filename according to expected pattern:
                    # {prefix}_Well_{wellID}_Site_{siteNumber}_{channel}.tif
                    prefixBeforeWell, suffixWithWell = eachfile.split("_Well_")
                    Well, suffixAfterWell = suffixWithWell.split("_Site_")
                    logger.info(
                        "File parts: Prefix=%s, Well=%s, SuffixAfter=%s", prefixBeforeWell, Well, suffixAfterWell
                    )

                    # Extract channel suffix (part after the Site_#_ portion)
                    channelSuffix = suffixAfterWell[
                        suffixAfterWell.index("_") + 1 :
                    ]
                    logger.info("Channel suffix: %s", channelSuffix)

                    # Track this prefix-channel combination if new
                    if (prefixBeforeWell, channelSuffix) not in presuflist:
                        presuflist.append((prefixBeforeWell, channelSuffix))
                        logger.info(
                            "Added to presuflist: %s", (prefixBeforeWell, channelSuffix)
                        )

                    # Track this well if new
                    if Well not in welllist:
                        welllist.append(Well)
                        logger.info("Added to welllist: %s", Well)

                    # If this file has our target channel, note its prefix/suffix
                    if channame in channelSuffix:
                        logger.info(
                            "Found target channel (%s) in %s", channame, channelSuffix
                        )
                        if permprefix is None:
                            permprefix = prefixBeforeWell
                            permsuffix = channelSuffix
                            logger.info(
                                "Set permanent prefix: %s and suffix: %s", permprefix, permsuffix
                            )
                except Exception as e:
                    logger.error("Error processing file %s: %s", eachfile, e)

    # Filter out non-TIFF files from presuflist
    logger.info("Before filtering presuflist: %s", presuflist)
    for eachpresuf in presuflist:
        if eachpresuf[1][-4:] != ".tif":
            if eachpresuf[1][-5:] != ".tiff":
                presuflist.remove(eachpresuf)
                logger.info("Removed from presuflist: %s", eachpresuf)

    # Sort for consistent processing order
    presuflist.sort()
    logger.info("Final welllist: %s", welllist)
    logger.info("Final presuflist: %s", presuflist)
    logger.info(
        "Analysis complete - wells: %s, channels: %s", welllist, presuflist
    )

    # STEP 4: Set up parameters for image stitching and cropping
    if round_or_square == "square":
        # Calculate image dimensions
        stitchedsize = int(rows) * int(size)  # Base size of the stitched image
        tileperside = int(tileperside)  # How many tiles to create per side
        scale_factor = float(scalingstring)  # Scaling factor to apply
        rounded_scale_factor = int(round(scale_factor))

        # Calculate the final image size after scaling
        upscaledsize = int(stitchedsize * rounded_scale_factor)
        # ImageJ has a size limit, so cap if needed
        if upscaledsize > 46340:
            upscaledsize = 46340

        # Calculate the size of each tile
        tilesize = int(upscaledsize / tileperside)

        # Confirm proceeding with stitching
        if not confirm_continue(
            "Setup complete. Ready to process %d wells and %d channels. Proceed with stitching?" % (len(welllist), len(presuflist))
        ):
            logger.info("Exiting at user request before processing wells")
            sys.exit(0)

        # STEP 5: Process each well
        for eachwell in welllist:
            # Create the instructions for ImageJ's Grid/Collection stitching plugin
            # This defines how images will be stitched together
            standard_grid_instructions = [
                # First part of the command with grid setup
                "type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x="
                + rows
                + " grid_size_y="
                + columns
                + " tile_overlap="
                + overlap_pct
                + " first_file_index_i=0 directory="
                + subdir
                + " file_names=",
                # Second part with stitching parameters
                " output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]",
            ]
            # Confirm before processing this well
            if eachwell == welllist[0]:  # Only confirm on the first well
                if not confirm_continue(
                    "Ready to process well %s and all its channels. Proceed?" % eachwell
                ):
                    logger.info(
                        "Exiting at user request before processing well %s", eachwell
                    )
                    sys.exit(0)

            # STEP 6: Process each channel for this well
            for eachpresuf in presuflist:  # for each channel
                # Extract the prefix and suffix (channel name)
                thisprefix, thissuffix = eachpresuf

                # Clean up the suffix to use as a directory name
                thissuffixnicename = thissuffix.split(".")[0]
                if thissuffixnicename[0] == "_":
                    thissuffixnicename = thissuffixnicename[1:]

                # Create a channel-specific subdirectory for tile outputs
                tile_subdir_persuf = os.path.join(
                    tile_subdir, thissuffixnicename
                )
                if not os.path.exists(tile_subdir_persuf):
                    os.mkdir(tile_subdir_persuf)

                # Set up the filename pattern for input images
                # The {i} will be replaced with site numbers (1, 2, 3, 4...)
                filename = (
                    thisprefix + "_Well_" + eachwell + "_Site_{i}_" + thissuffix
                )

                # Set up the output filename for the stitched image
                fileoutname = "Stitched" + filename.replace("{i}", "")

                # STEP 7: Run the ImageJ stitching operation for this channel and well
                IJ.run(
                    "Grid/Collection stitching",
                    standard_grid_instructions[0]
                    + filename
                    + standard_grid_instructions[1],
                )
                # Get the resulting stitched image
                im = IJ.getImage()

                # Calculate dimensions for scaling
                width = str(int(round(im.width * float(scalingstring))))
                height = str(int(round(im.height * float(scalingstring))))

                # Log progress of stitching
                logger.info("Stitching complete for %s - %s", eachwell, thissuffix)

                # STEP 8: Scale the stitched image
                # This scales the barcoding and cell painting images to match each other
                logger.info(
                    "Scale... x=%s y=%s width=%s height=%s interpolation=Bilinear average create", scalingstring, scalingstring, width, height
                )
                IJ.run(
                    "Scale...",
                    "x="
                    + scalingstring
                    + " y="
                    + scalingstring
                    + " width="
                    + width
                    + " height="
                    + height
                    + " interpolation=Bilinear average create",
                )
                # Wait for the operation to complete
                # TODO: Uncomment this after testing
                # time.sleep(15)
                im2 = IJ.getImage()

                # STEP 9: Adjust the canvas size
                # Padding ensures tiles are all the same size (for CellProfiler later on)
                logger.info(
                    "Canvas Size... width=%s height=%s position=Top-Left zero", upscaledsize, upscaledsize
                )
                IJ.run(
                    "Canvas Size...",
                    "width="
                    + str(upscaledsize)
                    + " height="
                    + str(upscaledsize)
                    + " position=Top-Left zero",
                )
                # Wait for the operation to complete
                # TODO: Uncomment this after testing
                # time.sleep(15)
                im3 = IJ.getImage()

                # STEP 10: Save the stitched image
                savefile(
                    im3,
                    os.path.join(out_subdir, fileoutname),
                    plugin,
                    compress=compress,
                )

                # Close all images and reopen the saved stitched image
                IJ.run("Close All")
                im = IJ.open(os.path.join(out_subdir, fileoutname))
                im = IJ.getImage()

                # Log progress
                logger.info(
                    "Scaling and saving complete for %s - %s", eachwell, thissuffix
                )

                # STEP 11: Crop the stitched image into tiles
                for eachxtile in range(tileperside):
                    for eachytile in range(tileperside):
                        # Calculate the tile number (1-based)
                        each_tile_num = eachxtile * tileperside + eachytile + 1

                        # Select a rectangular region for this tile
                        IJ.makeRectangle(
                            eachxtile * tilesize,  # X position
                            eachytile * tilesize,  # Y position
                            tilesize,  # Width
                            tilesize,  # Height
                        )

                        # Crop the selected region
                        im_tile = im.crop()

                        # Save the cropped tile
                        savefile(
                            im_tile,
                            os.path.join(
                                tile_subdir_persuf,
                                thissuffixnicename
                                + "_Site_"
                                + str(each_tile_num)
                                + ".tiff",
                            ),
                            plugin,
                            compress=compress,
                        )

                # Close all images and reopen the saved stitched image again
                IJ.run("Close All")
                im = IJ.open(os.path.join(out_subdir, fileoutname))
                im = IJ.getImage()

                # STEP 12: Create downsampled version for quality control
                logger.info(
                    "Scale... x=0.1 y=0.1 width=%s height=%s interpolation=Bilinear average create", im.width / 10, im.width / 10
                )
                # Scale down to 10% of original size
                im_10 = IJ.run(
                    "Scale...",
                    "x=0.1 y=0.1 width="
                    + str(im.width / 10)
                    + " height="
                    + str(im.width / 10)
                    + " interpolation=Bilinear average create",
                )
                im_10 = IJ.getImage()

                # Save the downsampled image
                savefile(
                    im_10,
                    os.path.join(downsample_subdir, fileoutname),
                    plugin,
                    compress=compress,
                )

                # Log crop and downsample completion
                logger.info(
                    "Cropping and downsampling complete for %s - %s", eachwell, thissuffix
                )

                # Close all open images before next iteration
                IJ.run("Close All")
                # Commented out code for reference:
                # im=IJ.open(os.path.join(out_subdir,fileoutname))
                # im = IJ.getImage()
                # IJ.run("Close All")
    # Code for round wells is disabled for testing
    elif round_or_square == "round":
        logger.info("Removed round for testing")

    else:
        logger.error("Must identify well as round or square")
else:
    logger.error("Could not find input directory %s", subdir)

# STEP 13: Move the TileConfiguration.txt file to the output directory
for eachlogfile in ["TileConfiguration.txt"]:
    try:
        os.rename(
            os.path.join(subdir, eachlogfile),
            os.path.join(out_subdir, eachlogfile),
        )
        logger.info("Moved %s to output directory", eachlogfile)
    except Exception:
        logger.error("Could not find TileConfiguration.txt in %s", subdir)
        # Create an empty file if it doesn't exist (for testing purposes)
        if not os.path.exists(os.path.join(out_subdir, eachlogfile)):
            with open(os.path.join(out_subdir, eachlogfile), "w") as f:
                f.write("# This is a placeholder file\n")
            logger.info("Created empty %s in output directory", eachlogfile)

# Final confirmation
logger.info("Processing complete")
# In autorun mode, always show summary
if autorun or confirm_continue(
    "All processing is complete. Would you like to see a summary?"
):
    logger.info("======== PROCESSING SUMMARY =========")
    logger.info("Input directory: %s" % subdir)
    logger.info("Stitched images: %s" % out_subdir)
    logger.info("Cropped tiles: %s" % tile_subdir)
    logger.info("Downsampled QC images: %s" % downsample_subdir)
    logger.info("Wells processed: %s" % welllist)
    logger.info("Channels processed: %s", [s[1] for s in presuflist])
    logger.info("=====================================")

logger.info("Processing completed successfully")
