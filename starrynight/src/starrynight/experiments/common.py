"""Common experiment schemas."""

from abc import ABC, abstractstaticmethod
from enum import Enum
from pathlib import Path
from typing import Unpack

# Use a try block for backwards compatibility
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from pydantic import BaseModel


class Experiment(BaseModel, ABC):
    """Experiment configuration."""

    dataset_id: str
    data_production_contact: str | None = None
    data_processing_contact: str | None = None

    # users should not access it directly
    init_config_: BaseModel | None = None

    @abstractstaticmethod
    def from_index(index_path: Path, **kwargs: Unpack) -> Self:
        """Create experiment schema from index."""
        pass


class DummyExperiment(Experiment):
    """DummyExperiment to bootstrap pipeline configuration."""

    @staticmethod
    def from_index(index_path: Path) -> Self:
        """Configure experiment with index."""
        raise NotImplementedError


class ImageMetadataGeneric(BaseModel):
    """Generic metadata for an image."""

    name: str
    batch_id: str
    plate_id: str
    site_id: str
    img_format: str
    assay_type: str
    channel_dict: dict


class ImageFrameType(Enum):
    """Frame type for image."""

    ROUND = "round"
    SQUARE = "square"


class AcquisitionOrderType(Enum):
    """Acquisition order for image."""

    SNAKE = "snake"
    ROWS = "rows"
