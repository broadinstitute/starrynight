"""Inventory module.

Provides functions to create inventory files.
"""

import random
import string
from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from cpgdata.utils import parallel
from pydantic import BaseModel
from tqdm import tqdm

from starrynight.utils.misc import merge_pq, write_pq


class FileInventory(BaseModel):
    """File Inventory.

    Attributes
    ----------
    key : File location.
    filename : Filename.
    extension : File extension.
    prefix : prefix for the file.

    """

    key: str
    filename: str
    extension: str
    prefix: str | None = None


def randomword(length: int) -> str:
    """Generate random word.

    Parameters
    ----------
    length : int
        Length of word to generate.

    Returns
    -------
    str
        Random word.

    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def parse_prefix(
    prefix_list: list[CloudPath | Path],
    out_dir: CloudPath | Path,
    prefix: CloudPath | Path,
    job_idx: int = 0,
) -> None:
    """Parse prefix.

    Parameters
    ----------
    prefix_list : list[CloudPath | Path]
        List of prefix to parse.
    out_dir : CloudPath | Path
        Path to output dir.
    prefix : CloudPath | Path
        Prefix to use.
    job_idx : int
        Index of job.

    """
    col_dict = {key: [] for key in FileInventory.model_construct().model_fields.keys()}
    for file in tqdm(prefix_list, desc="Writing inventory: ", position=job_idx):
        if file.is_dir():
            continue
        parsed_local_file = FileInventory(
            key=file.relative_to(prefix).__str__(),  # pyright: ignore
            filename=file.name,
            extension=file.suffix,
            prefix=prefix.resolve().__str__(),
        )
        for key, value in parsed_local_file.model_dump().items():
            col_dict[key].append(value)
    write_pq(
        col_dict,
        FileInventory,
        out_dir.joinpath(f"inventory_{job_idx}_{randomword(10)}.parquet"),
    )


def create_inventory(
    dataset_dir: Path | CloudPath, out_dir: Path | CloudPath, prefix: Path | CloudPath
) -> None:
    """Create inventory files from dataset.

    Parameters
    ----------
    dataset_dir : Path | CloudPath
        Path to dataset. Can be local or a cloud path.
    out_dir : Path | CloudPath
        Path to save generated inventory. Can be local or a cloud path.
    prefix : Path | CloudPath
        prefix to add to inventory files.

    """
    files = [AnyPath(file) for file in AnyPath(dataset_dir).rglob("*")]
    inv = out_dir.joinpath("inv")
    inv.mkdir(parents=True, exist_ok=True)
    # prefix = Path("/datastore/")
    parallel(files, parse_prefix, [inv, prefix])

    out_files = [AnyPath(file) for file in AnyPath(inv).rglob("*.parquet")]
    merge_pq(out_files, out_dir.joinpath("inventory.parquet"))
