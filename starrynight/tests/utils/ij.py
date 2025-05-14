"""Mock implementation of ImageJ/Fiji libraries for testing control flow."""

import sys
from typing import Any, Optional, Union


class ImagePlus:
    """Mock ImagePlus class to simulate ImageJ images."""

    def __init__(self, width: int = 1000, height: int = 1000) -> None:
        """Initialize image with dimensions.

        Args:
            width: Image width in pixels.
            height: Image height in pixels.

        """
        self.width = width
        self.height = height
        self.title = "MockImage"

    def crop(self) -> "ImagePlus":
        """Return a new cropped image."""
        return ImagePlus(width=500, height=500)


class IJ:
    """Mock IJ class to simulate ImageJ functions."""

    @staticmethod
    def run(command: str, options: str | None = None) -> None:
        """Mock implementation of IJ.run command.

        Args:
            command: The ImageJ command to run.
            options: Optional parameters for the command.

        """
        print(f"Mock IJ.run: {command} with options: {options}")
        return None

    # Keep camelCase method names to match ImageJ's Java API
    @staticmethod
    def getImage() -> ImagePlus:  # noqa: N802
        """Get the current image in ImageJ.

        Returns:
            A mock ImagePlus object.

        """
        print("Mock IJ.getImage called")
        return ImagePlus()

    @staticmethod
    def makeRectangle(x: int, y: int, width: int, height: int) -> None:  # noqa: N802
        """Create a rectangular selection.

        Args:
            x: X-coordinate of the selection.
            y: Y-coordinate of the selection.
            width: Width of the selection.
            height: Height of the selection.

        """
        print(f"Mock IJ.makeRectangle: {x}, {y}, {width}, {height}")
        return None

    @staticmethod
    def open(path: str) -> None:
        """Open an image file.

        Args:
            path: Path to the image file.

        """
        print(f"Mock IJ.open: {path}")
        return None

    @staticmethod
    def saveAs(image: ImagePlus, format_type: str, path: str) -> None:  # noqa: N802
        """Save an image to a file.

        Args:
            image: The image to save.
            format_type: The format to save as (tiff, etc).
            path: The file path to save to.

        """
        print(f"Mock IJ.saveAs: Saving {format_type} to {path}")
        return None


class ModuleType:
    """Module type class for creating mock modules."""

    def __init__(self, name: str) -> None:
        """Initialize a module with a name.

        Args:
            name: The name of the module.

        """
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
    """Mock implementation of the LociExporter class."""

    def __init__(self) -> None:
        """Initialize a LociExporter.

        Creates an exporter with a None arg.
        """
        self.arg = None

    def run(self) -> None:
        """Run the exporter with the current settings."""
        print(f"Mock LociExporter.run with arg: {self.arg}")


class Exporter:
    """Mock implementation of the Exporter class."""

    def __init__(self, plugin: LociExporter, image: ImagePlus) -> None:
        """Initialize an Exporter with a plugin and image.

        Args:
            plugin: The plugin to use for exporting.
            image: The image to export.

        """
        self.plugin = plugin
        self.image = image

    def run(self) -> None:
        """Run the exporter with the current settings."""
        print(f"Mock Exporter.run with plugin: {self.plugin}")


# Assign the classes to their modules
loci.plugins.LociExporter = LociExporter
loci.plugins.out.Exporter = Exporter
