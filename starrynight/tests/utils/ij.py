"""Mock implementation of ImageJ/Fiji libraries for testing control flow."""


class ImagePlus:
    """Mock ImagePlus class to simulate ImageJ images"""

    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.title = "MockImage"

    def crop(self):
        """Return a new cropped image"""
        return ImagePlus(width=500, height=500)


class IJ:
    """Mock IJ class to simulate ImageJ functions"""

    @staticmethod
    def run(command, options=None):
        print(f"Mock IJ.run: {command} with options: {options}")
        return None

    @staticmethod
    def getImage():
        print("Mock IJ.getImage called")
        return ImagePlus()

    @staticmethod
    def makeRectangle(x, y, width, height):
        print(f"Mock IJ.makeRectangle: {x}, {y}, {width}, {height}")
        return None

    @staticmethod
    def open(path):
        print(f"Mock IJ.open: {path}")
        return None

    @staticmethod
    def saveAs(image, format_type, path):
        print(f"Mock IJ.saveAs: Saving {format_type} to {path}")
        return None


# Create a loci.plugins module
import sys


class ModuleType:
    def __init__(self, name):
        self.__name__ = name


# Create the module structure
loci = ModuleType("loci")
loci.plugins = ModuleType("loci.plugins")
loci.plugins.out = ModuleType("loci.plugins.out")
sys.modules["loci"] = loci
sys.modules["loci.plugins"] = loci.plugins
sys.modules["loci.plugins.out"] = loci.plugins.out


# Define the classes
class LociExporter:
    def __init__(self):
        self.arg = None

    def run(self):
        print(f"Mock LociExporter.run with arg: {self.arg}")


class Exporter:
    def __init__(self, plugin, image):
        self.plugin = plugin
        self.image = image

    def run(self):
        print(f"Mock Exporter.run with plugin: {self.plugin}")


# Assign the classes to their modules
loci.plugins.LociExporter = LociExporter
loci.plugins.out.Exporter = Exporter
