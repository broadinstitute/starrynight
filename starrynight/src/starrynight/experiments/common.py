"""Common experiment schemas."""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from cloudpathlib.cloudpath import CloudPath
from pydantic import BaseModel


class Experiment(BaseModel, ABC):
    """Experiment configuration."""

    dataset_id: str
    index_path: Path | CloudPath
    inventory_path: Path | CloudPath | None = None
    data_production_contact: str | None = None
    data_processing_contact: str | None = None

    # users should not access it directly
    init_config_: BaseModel | None = None

    @staticmethod
    @abstractmethod
    def get_init_config() -> BaseModel:
        pass

    @staticmethod
    @abstractmethod
    def from_index(
        index_path: Path | CloudPath, init_config: dict
    ) -> "Experiment":
        """Create experiment schema from index."""
        pass


class DummyExperiment(Experiment):
    """DummyExperiment to bootstrap pipeline configuration."""

    @staticmethod
    def from_index(index_path: Path) -> "DummyExperiment":
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
