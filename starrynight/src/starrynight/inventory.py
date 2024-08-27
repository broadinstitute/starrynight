"""Inventory module.

Provides functions to create inventory files.
"""

from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from pydantic import BaseModel
from tqdm import tqdm

from starrynight.utils.misc import write_pq


class FileInventory(BaseModel):
    """File Inventory.

    Attributes
    ----------
    key : File location.
    filename : Filename.
    extension : File extension.
    local_prefix : Local prefix for the file.
    cloud_prefix : Cloud prefix for the file.

    """

    key: str
    filename: str
    extension: str
    local_prefix: str | None = None
    cloud_prefix: str | None = None


def create_inventory(
    dataset_dir: Path | CloudPath,
    out_dir: Path | CloudPath,
    local_prefix: str | None = None,
    cloud_prefix: str | None = None,
) -> None:
    """Create inventory files from dataset.

    Parameters
    ----------
    dataset_dir : Path | CloudPath
        Path to dataset. Can be local or a cloud path.
    out_dir : Path | CloudPath
        Path to save generated inventory. Can be local or a cloud path.
    local_prefix : str | None
        Local prefix to add to inventory files.
    cloud_prefix : str | None
        Cloud prefix to add to inventory files.

    """
    files = [AnyPath(file) for file in AnyPath(dataset_dir).glob("*/**")]
    col_dict = {key: [] for key in FileInventory.model_construct().model_fields.keys()}
    for file in tqdm(files, desc="Writing inventory: "):
        parsed_local_file = FileInventory(
            key=str(file),
            filename=file.stem,
            extension=file.suffix,
            local_prefix=local_prefix,
            cloud_prefix=cloud_prefix,
        )
        for key, value in parsed_local_file.model_dump().items():
            col_dict[key].append(value)
    write_pq(col_dict, FileInventory, out_dir.joinpath("inventory.parquet"))
