"""Starrynight templates."""

from pathlib import Path


def get_templates_path() -> Path:
    """Return the path to the templates."""
    return Path(__file__).parent
