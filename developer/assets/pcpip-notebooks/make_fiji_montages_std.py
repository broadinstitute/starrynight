from ij import IJ
import os

topdir = r"C:\\Users\\Administrator\\Desktop\\assaydev"
ncols = "10"  # 24 if 384, 12 if 96 well
nrows = "6"  # 16 if 384, 8 if 96 well
scale = "0.75"
border = "1"
batchlist = os.listdir(topdir)

platelist = []

for eachbatch in batchlist:
    batchfolder = os.path.join(topdir, eachbatch)
    if os.path.isdir(batchfolder):
        folderlist = os.listdir(batchfolder)
        for eachfolder in folderlist:
            if "-" in eachfolder:
                plate = eachfolder.rsplit("-", 1)[0]
                platelist.append(plate)
                if not os.path.exists(os.path.join(batchfolder, plate)):
                    os.mkdir(os.path.join(batchfolder, plate))
                for eachfile in os.listdir(os.path.join(batchfolder, eachfolder)):
                    if ".png" in eachfile:
                        try:
                            os.rename(
                                os.path.join(batchfolder, eachfolder, eachfile),
                                os.path.join(batchfolder, plate, eachfile),
                            )
                        except:  # noqa: E722
                            pass

for eachbatch in batchlist:
    batchfolder = os.path.join(topdir, eachbatch)
    folderlist = os.listdir(batchfolder)
    for eachfolder in folderlist:
        if eachfolder in platelist:  # only use plate folders
            if os.path.isdir(os.path.join(batchfolder, eachfolder)):
                thisfolder = os.path.join(batchfolder, eachfolder)
                sampleimage = os.listdir(thisfolder)[0]
                IJ.run(
                    "Image Sequence...",
                    "open=" + os.path.join(thisfolder, sampleimage) + " sort",
                )
                IJ.run(
                    "Make Montage...",
                    "columns="
                    + ncols
                    + " rows="
                    + nrows
                    + " scale="
                    + scale
                    + " border="
                    + border,
                )
                im = IJ.getImage()
                IJ.saveAs("Tiff", os.path.join(batchfolder, eachfolder + ".tif"))
                IJ.run("Close All")
