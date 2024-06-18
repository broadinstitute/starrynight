"""Inventory module.

Provides functions to create inventory files.
"""

from glob import glob
from pathlib import Path
from typing import Type

from cpgdata.pipe import get_field_type
from cpgdata.parser import py_to_pa
import pyarrow as pa
from pyarrow import parquet as pq
from pydantic import BaseModel
from tqdm import tqdm


class FileInventory(BaseModel):
    key: str
    filename: str
    extension: str
    local_prefix: str | None = None
    s3_prefix: str | None = None


def gen_pq_schema(pydantic_model: Type[BaseModel]) -> pa.Schema:
    """Generate parquet schema from pydantic type.

    Parameters
    ----------
    pydantic_model : Type[MeasuredPrefix]
        Pydantic model type.

    Returns
    -------
    pa.Schema
        Parquet schema.
    """
    constructed_model = pydantic_model.model_construct()
    model_fields = constructed_model.model_fields
    schema = [
        pa.field(key, py_to_pa[get_field_type(val)])
        for key, val in model_fields.items()
    ]
    return pa.schema(schema)


def write_pq(col_dict: dict, dict_type: Type[BaseModel], out_path: Path) -> None:
    pq_schema = gen_pq_schema(dict_type)
    with pq.ParquetWriter(out_path, pq_schema) as pq_witer:
        pq_witer.write_table(pa.Table.from_pydict(col_dict, schema=pq_schema))


def create_inventory_local(
    dataset_dir: Path,
    out_dir: Path,
    local_prefix: str | None = None,
    s3_prefix: str | None = None,
) -> None:
    files = [Path(file) for file in glob("*/**", root_dir=dataset_dir, recursive=True)]
    col_dict = {key: [] for key in FileInventory.model_construct().model_fields.keys()}
    for file in tqdm(files, desc="Writing inventory: "):
        parsed_local_file = FileInventory(
            key=str(file),
            filename=file.stem,
            extension=file.suffix,
            local_prefix=local_prefix,
            s3_prefix=s3_prefix,
        )
        for key, value in parsed_local_file.model_dump().items():
            col_dict[key].append(value)
    write_pq(col_dict, FileInventory, out_dir.joinpath("inventory.parquet"))
