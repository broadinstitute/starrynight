"""Utilities for cellprofiler."""

import logging
from pathlib import Path

import cellprofiler_core.preferences
from cellprofiler_core.preferences import LOGGER
import cellprofiler_core.utilities.java
from cellprofiler_core.pipeline import Pipeline


class CellProfilerContext:
    def __init__(
        self, out_dir: Path, plugin_dir: Path | None = None, require_jvm: bool = False
    ) -> None:
        out_dir.mkdir(exist_ok=True, parents=True)
        self.out_dir = out_dir.resolve().__str__()
        LOGGER.setLevel(logging.CRITICAL)
        if plugin_dir is not None:
            self.plugin_dir = plugin_dir.resolve().__str__()
        else:
            self.plugin_dir = None
        self.require_jvm = require_jvm

    def __enter__(self) -> Pipeline:
        cellprofiler_core.preferences.set_headless()
        if self.require_jvm:
            cellprofiler_core.utilities.java.start_java()
        cellprofiler_core.preferences.set_default_output_directory(self.out_dir)
        if self.plugin_dir is not None:
            cellprofiler_core.preferences.set_plugin_directory(self.plugin_dir)
        self.pipeline = Pipeline()
        return self.pipeline

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.require_jvm:
            cellprofiler_core.utilities.java.stop_java()
