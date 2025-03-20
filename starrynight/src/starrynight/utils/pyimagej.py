"""Imagej context provider."""

from inspect import Traceback
from pathlib import Path

import imagej
import jpype
import scyjava
from imagej._java import jc


class ImagejContext:
    """Context manager for setting up a Imagej environment.

    Returns
    -------
    Pipeline
        Initialized imagej object.

    """

    def __init__(
        self,
    ) -> None:
        """Initialize the context.

        Creates the output directory and sets up logging.
        """
        self.fiji_path = Path(
            "/home/ank/workspace/hub/broad/starrynight/scratch/Fiji.app"
        )
        self.plugin_path = self.fiji_path.joinpath("plugins/")

        # scyjava.config.add_options(f"-Dplugins.dir={self.plugin_path}")

    def __enter__(self):
        """Enter the context.

        Sets up CellProfiler preferences and starts a JVM if required.
        Returns the pipeline object.
        """
        self.ij = imagej.init(self.fiji_path)
        return self.ij

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: Traceback) -> None:
        """Exit the context and clean up resources.

        Parameters
        ----------
        exc_type : type
            The type of exception raised, if any.
        exc_val : Exception
            The instance of the exception raised, if any.
        exc_tb : Traceback
            The traceback object for the exception, if any.

        """
        self.ij.dispose()
        jpype.shutdownJVM()
