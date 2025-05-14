# ruff: noqa: ANN002,ANN003,ANN202,ANN204,ANN401,D100,D104,D202,D400,D413,D415,E501,F401,F541,F821,F841,I001,N803,N806,N816,PTH102,PTH104,PTH110,PTH112,PTH113,PTH118,PTH123,UP015,UP024,UP031,UP035,W605,E722

import os
import time
import logging
from ij import IJ
from loci.plugins import LociExporter
from loci.plugins.out import Exporter

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

input_file_location = "../../scratch/fix_s1_pcpip_output/Source1/Batch1"
step_to_stitch = "images_corrected"
subdir = "images_corrected/painting"
out_subdir_tag = "Plate_Well"
rows = "2"
columns = "2"
imperwell = "unused"
stitchorder = "unused"
channame = "DNA"
size = "1480"
overlap_pct = "10"
tileperside = "2"
filterstring = "unused"
scalingstring = "1.99"
awsdownload = "unused"
bucketname = "unused"
localtemp = "../../scratch/FIJI_temp"
downloadfilter = "unused"
round_or_square = "square"
quarter_if_round = "unused"
final_tile_size = "2960"
xoffset_tiles = "0"
yoffset_tiles = "0"
compress = "True"

top_outfolder = input_file_location

plugin = LociExporter()


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
    print("Saving ", imname, im.width, im.height)
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
                print("Succeeded after attempt ", attemptcount)
                return
            except:
                attemptcount += 1
        print("failed 5 times at saving")


logger.info(f"Top output folder: {top_outfolder}")
if not os.path.exists(top_outfolder):
    logger.info(f"Creating top output folder: {top_outfolder}")
    os.mkdir(top_outfolder)

# Define and create the parent folders where the images will be output
outfolder = os.path.join(top_outfolder, (step_to_stitch + "_stitched"))
tile_outdir = os.path.join(top_outfolder, (step_to_stitch + "_cropped"))
downsample_outdir = os.path.join(
    top_outfolder, (step_to_stitch + "_stitched_10X")
)
logger.info(
    f"Output folders: \n - Stitched: {outfolder}\n - Cropped: {tile_outdir}\n - Downsampled: {downsample_outdir}"
)

if not os.path.exists(outfolder):
    logger.info(f"Creating output folder: {outfolder}")
    os.mkdir(outfolder)
if not os.path.exists(tile_outdir):
    logger.info(f"Creating tile output folder: {tile_outdir}")
    os.mkdir(tile_outdir)
if not os.path.exists(downsample_outdir):
    logger.info(f"Creating downsample output folder: {downsample_outdir}")
    os.mkdir(downsample_outdir)

# Define and create the batch-specific subfolders where the images will be output
out_subdir = os.path.join(outfolder, out_subdir_tag)
tile_subdir = os.path.join(tile_outdir, out_subdir_tag)
downsample_subdir = os.path.join(downsample_outdir, out_subdir_tag)
if not os.path.exists(tile_subdir):
    os.mkdir(tile_subdir)
if not os.path.exists(downsample_subdir):
    os.mkdir(downsample_subdir)
if not os.path.exists(out_subdir):
    os.mkdir(out_subdir)

subdir = os.path.join(input_file_location, subdir)
logger.info(f"Input subdirectory: {subdir}")

# bypassed awsdownload == 'True' for test

logger.info(f"Checking if directory exists: {subdir}")
a = os.listdir(subdir)
logger.info(f"Contents of {subdir}: {a}")

for x in a:
    if os.path.isdir(os.path.join(subdir, x)):
        logger.info(f"Processing subdirectory: {x}")
        b = os.listdir(os.path.join(subdir, x))
        for c in b:
            src = os.path.join(subdir, x, c)
            dst = os.path.join(subdir, c)
            logger.info(f"Moving file: {src} -> {dst}")
            os.rename(os.path.join(subdir, x, c), os.path.join(subdir, c))

if os.path.isdir(subdir):
    logger.info(f"Processing directory content: {subdir}")
    dirlist = os.listdir(subdir)
    logger.info(f"Files in directory: {dirlist}")
    welllist = []
    presuflist = []
    permprefix = None
    permsuffix = None
    for eachfile in dirlist:
        if ".tif" in eachfile:
            logger.info(f"Processing TIFF file: {eachfile}")
            # removed filterstring for test
            if "Overlay" not in eachfile:
                try:
                    prefixBeforeWell, suffixWithWell = eachfile.split("_Well_")
                    Well, suffixAfterWell = suffixWithWell.split("_Site_")
                    logger.info(
                        f"File parts: Prefix={prefixBeforeWell}, Well={Well}, SuffixAfter={suffixAfterWell}"
                    )
                    channelSuffix = suffixAfterWell[
                        suffixAfterWell.index("_") + 1 :
                    ]
                    logger.info(f"Channel suffix: {channelSuffix}")
                    if (prefixBeforeWell, channelSuffix) not in presuflist:
                        presuflist.append((prefixBeforeWell, channelSuffix))
                        logger.info(
                            f"Added to presuflist: {(prefixBeforeWell, channelSuffix)}"
                        )
                    if Well not in welllist:
                        welllist.append(Well)
                        logger.info(f"Added to welllist: {Well}")
                    if channame in channelSuffix:
                        logger.info(
                            f"Found target channel ({channame}) in {channelSuffix}"
                        )
                        if permprefix is None:
                            permprefix = prefixBeforeWell
                            permsuffix = channelSuffix
                            logger.info(
                                f"Set permanent prefix: {permprefix} and suffix: {permsuffix}"
                            )
                except Exception as e:
                    logger.error(f"Error processing file {eachfile}: {e}")

    logger.info(f"Before filtering presuflist: {presuflist}")
    for eachpresuf in presuflist:
        if eachpresuf[1][-4:] != ".tif":
            if eachpresuf[1][-5:] != ".tiff":
                presuflist.remove(eachpresuf)
                logger.info(f"Removed from presuflist: {eachpresuf}")
    presuflist.sort()
    logger.info(f"Final welllist: {welllist}")
    logger.info(f"Final presuflist: {presuflist}")
    print(welllist, presuflist)

    if round_or_square == "square":
        stitchedsize = int(rows) * int(size)
        tileperside = int(tileperside)
        scale_factor = float(scalingstring)
        rounded_scale_factor = int(round(scale_factor))
        upscaledsize = int(stitchedsize * rounded_scale_factor)
        if upscaledsize > 46340:
            upscaledsize = 46340
        tilesize = int(upscaledsize / tileperside)

        for eachwell in welllist:
            # simplified for test
            standard_grid_instructions = [
                "type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x="
                + rows
                + " grid_size_y="
                + columns
                + " tile_overlap="
                + overlap_pct
                + " first_file_index_i=0 directory="
                + subdir
                + " file_names=",
                " output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]",
            ]
            for eachpresuf in presuflist:  # for each channel
                thisprefix, thissuffix = eachpresuf
                thissuffixnicename = thissuffix.split(".")[0]
                if thissuffixnicename[0] == "_":
                    thissuffixnicename = thissuffixnicename[1:]
                tile_subdir_persuf = os.path.join(
                    tile_subdir, thissuffixnicename
                )
                if not os.path.exists(tile_subdir_persuf):
                    os.mkdir(tile_subdir_persuf)
                filename = (
                    thisprefix + "_Well_" + eachwell + "_Site_{i}_" + thissuffix
                )
                fileoutname = "Stitched" + filename.replace("{i}", "")

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
                print(
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
                time.sleep(15)
                im2 = IJ.getImage()
                # padding to ensure tiles are all the same size (for CellProfiler later on)
                print(
                    "Canvas Size...",
                    "width="
                    + str(upscaledsize)
                    + " height="
                    + str(upscaledsize)
                    + " position=Top-Left zero",
                )
                IJ.run(
                    "Canvas Size...",
                    "width="
                    + str(upscaledsize)
                    + " height="
                    + str(upscaledsize)
                    + " position=Top-Left zero",
                )
                time.sleep(15)
                im3 = IJ.getImage()
                savefile(
                    im3,
                    os.path.join(out_subdir, fileoutname),
                    plugin,
                    compress=compress,
                )

                IJ.run("Close All")
                im = IJ.open(os.path.join(out_subdir, fileoutname))
                im = IJ.getImage()

                for eachxtile in range(tileperside):
                    for eachytile in range(tileperside):
                        each_tile_num = eachxtile * tileperside + eachytile + 1
                        IJ.makeRectangle(
                            eachxtile * tilesize,
                            eachytile * tilesize,
                            tilesize,
                            tilesize,
                        )
                        im_tile = im.crop()
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

                IJ.run("Close All")
                im = IJ.open(os.path.join(out_subdir, fileoutname))
                im = IJ.getImage()

                # scaling to make a downsampled image for QC
                print(
                    "Scale...",
                    "x=0.1 y=0.1 width="
                    + str(im.width / 10)
                    + " height="
                    + str(im.width / 10)
                    + " interpolation=Bilinear average create",
                )
                im_10 = IJ.run(
                    "Scale...",
                    "x=0.1 y=0.1 width="
                    + str(im.width / 10)
                    + " height="
                    + str(im.width / 10)
                    + " interpolation=Bilinear average create",
                )
                im_10 = IJ.getImage()
                savefile(
                    im_10,
                    os.path.join(downsample_subdir, fileoutname),
                    plugin,
                    compress=compress,
                )
                IJ.run("Close All")
                # im=IJ.open(os.path.join(out_subdir,fileoutname))
                # im = IJ.getImage()
                # IJ.run("Close All")
    # removed round for test
    elif round_or_square == "round":
        print("Removed round for testing")

    else:
        print("Must identify well as round or square")
else:
    print("Could not find input directory ", subdir)
for eachlogfile in ["TileConfiguration.txt"]:
    os.rename(
        os.path.join(subdir, eachlogfile), os.path.join(out_subdir, eachlogfile)
    )
print("done")
