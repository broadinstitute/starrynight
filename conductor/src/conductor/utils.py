"""Utilities."""

from pathlib import Path


def get_scratch_path() -> Path:
    """Get scratch folder path.

    Returns
    -------
    Path
        Path to scratch folder.

    """
    return Path(__file__).resolve().parents[3].joinpath("scratch")
