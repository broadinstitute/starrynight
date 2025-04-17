"""Utilities for cellprofiler."""

import logging
from inspect import Traceback
from pathlib import Path
from typing import Self

import cellprofiler_core.preferences
import cellprofiler_core.utilities.java
from cellprofiler_core.pipeline import Event, Pipeline, RunException
from cellprofiler_core.preferences import LOGGER
from cloudpathlib import CloudPath


class CellProfilerContext:
    """Context manager for setting up a CellProfiler environment.

    Parameters
    ----------
    out_dir : Path | CloudPath
        Output directory where data will be written.
    loaddata_path : Path | CloudPath, optional
        Path to the data file. If None, no data file is loaded.
    plugin_dir : Path | CloudPath, optional
        Directory containing plugins. If None, no plugins are loaded.
    require_jvm : bool, optional
        Whether a Java Virtual Machine (JVM) is required.

    Returns
    -------
    Pipeline
        The CellProfiler pipeline object.

    """

    def __init__(
        self: Self,
        out_dir: Path | CloudPath,
        loaddata_path: Path | CloudPath | None = None,
        plugin_dir: Path | CloudPath | None = None,
        require_jvm: bool = False,
    ) -> None:
        """Initialize the context.

        Creates the output directory and sets up logging.
        """
        out_dir.mkdir(exist_ok=True, parents=True)
        self.out_dir = out_dir.resolve().__str__()
        self.loaddata_path = loaddata_path
        self.plugin_dir = plugin_dir
        self.require_jvm = require_jvm

        LOGGER.setLevel(logging.CRITICAL)

    @staticmethod
    def handle_error_event(_, event: Event) -> None:
        if isinstance(event, RunException):
            raise event.error

    def __enter__(self: Self) -> Pipeline:
        """Enter the context.

        Sets up CellProfiler preferences and starts a JVM if required.
        Returns the pipeline object.
        """
        cellprofiler_core.preferences.set_headless()
        cellprofiler_core.preferences.set_default_output_directory(self.out_dir)
        cellprofiler_core.reader.fill_readers(check_config=False)  # pyright: ignore[reportAttributeAccessIssue]
        cellprofiler_core.reader.filter_active_readers(["bioformats_reader"])  # pyright: ignore[reportAttributeAccessIssue]

        if self.loaddata_path:
            cellprofiler_core.preferences.set_data_file(
                self.loaddata_path.resolve().__str__()
            )
        if self.require_jvm:
            cellprofiler_core.utilities.java.start_java()
        if self.plugin_dir is not None:
            cellprofiler_core.preferences.set_plugin_directory(
                self.plugin_dir.resolve().__str__()
            )
        self.pipeline = Pipeline()
        self.pipeline.add_listener(self.handle_error_event)
        return self.pipeline

    def __exit__(
        self: Self, _exc_type: type, _exc_val: Exception, _exc_tb: Traceback
    ) -> None:
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
        if self.require_jvm:
            cellprofiler_core.utilities.java.stop_java()
