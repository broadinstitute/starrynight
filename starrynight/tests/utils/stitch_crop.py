import time
from pathlib import Path

from ij import IJ
from loci.plugins import LociExporter
from loci.plugins.out import Exporter

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
            except Exception as e:
                print(f"Error saving file: {e}")
                attemptcount += 1
        print("failed 5 times at saving")


top_outfolder_path = Path(top_outfolder)
if not top_outfolder_path.exists():
    top_outfolder_path.mkdir()

# Define and create the parent folders where the images will be output
outfolder = top_outfolder_path / f"{step_to_stitch}_stitched"
tile_outdir = top_outfolder_path / f"{step_to_stitch}_cropped"
downsample_outdir = top_outfolder_path / f"{step_to_stitch}_stitched_10X"

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
if not tile_subdir.exists():
    tile_subdir.mkdir()
if not downsample_subdir.exists():
    downsample_subdir.mkdir()
if not out_subdir.exists():
    out_subdir.mkdir()

subdir = Path(input_file_location) / subdir

# bypassed awsdownload == 'True' for test
a = list(subdir.iterdir())
for x in a:
    if x.is_dir():
        b = list(x.iterdir())
        for c in b:
            c.rename(subdir / c.name)

if subdir.is_dir():
    welllist = []
    presuflist = []
    permprefix = None
    permsuffix = None

    # Get all well directories
    well_dirs = [d for d in subdir.iterdir() if d.is_dir()]

    for well_dir in well_dirs:
        # Extract well name from directory name (e.g., 'Plate1-WellA1' -> 'WellA1')
        well = well_dir.name.split("-")[1]
        if well not in welllist:
            welllist.append(well)

        # Process all files in this well directory
        for eachfile in well_dir.iterdir():
            filename = eachfile.name
            if ".tif" in filename and "Overlay" not in filename:
                # Files follow pattern: Plate_Plate1_Well_WellA1_Site_0_CorrDNA.tiff
                try:
                    # Use the same parsing logic as before but adapted to the new format
                    prefix_before_well, suffix_with_well = filename.split(
                        "_Well_"
                    )
                    well_with_site, suffix = suffix_with_well.split("_Site_")
                    site_num, channel_suffix = suffix.split("_", 1)

                    if (prefix_before_well, channel_suffix) not in presuflist:
                        presuflist.append((prefix_before_well, channel_suffix))

                    if channame in channel_suffix:
                        if permprefix is None:
                            permprefix = prefix_before_well
                            permsuffix = channel_suffix
                except Exception as e:
                    print(f"Error parsing filename {filename}: {e}")
    for eachpresuf in presuflist:
        if eachpresuf[1][-4:] != ".tif":
            if eachpresuf[1][-5:] != ".tiff":
                presuflist.remove(eachpresuf)
    presuflist.sort()
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
            # Find the correct well directory
            well_dir = None
            for d in well_dirs:
                if d.name.split("-")[1] == eachwell:
                    well_dir = d
                    break

            if well_dir is None:
                print(f"Could not find directory for well {eachwell}")
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
                thissuffixnicename = thissuffix.split(".")[0]
                if thissuffixnicename[0] == "_":
                    thissuffixnicename = thissuffixnicename[1:]
                tile_subdir_persuf = tile_subdir / thissuffixnicename
                if not tile_subdir_persuf.exists():
                    tile_subdir_persuf.mkdir()
                # Pattern: Plate_Plate1_Well_WellA1_Site_0_CorrDNA.tiff
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
                    str(out_subdir / fileoutname),
                    plugin,
                    compress=compress,
                )

                IJ.run("Close All")
                im = IJ.open(str(out_subdir / fileoutname))
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
                            str(
                                tile_subdir_persuf
                                / f"{thissuffixnicename}_Site_{each_tile_num}.tiff"
                            ),
                            plugin,
                            compress=compress,
                        )

                IJ.run("Close All")
                im = IJ.open(str(out_subdir / fileoutname))
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
                    str(downsample_subdir / fileoutname),
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
# Commented out since we're working with individual well directories
# and TileConfiguration.txt might be in different locations
# for eachlogfile in ["TileConfiguration.txt"]:
#     (subdir / eachlogfile).rename(out_subdir / eachlogfile)
print("done")
