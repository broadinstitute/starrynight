"""Misc utilities."""

from pathlib import Path


def get_scratch_path() -> Path:
    return Path(__file__).parents[4].joinpath("scratch")
