"""Misc utilities."""

from pathlib import Path

import pyarrow as pa
from cloudpathlib import CloudPath
from pyarrow import parquet as pq
from pydantic import BaseModel

from starrynight.utils.py_to_pa import get_pyarrow_schema


def get_scratch_path() -> Path:
    """Get path to scratch directory.

    Returns
    -------
    Path
        Path to scratch directory.

    """
    return Path(__file__).parents[4].joinpath("scratch")


def write_pq(
    col_dict: dict, dict_type: type[BaseModel], out_path: Path | CloudPath
) -> None:
    """Write Parquet file.

    Parameters
    ----------
    col_dict : dict
        Column dictionary.
    dict_type : type[BaseModel]
        PyDantic model.
    out_path : Path | CloudPath
        Path to save Parquet file. Can be local or a cloud path.

    """
    pq_schema = get_pyarrow_schema(dict_type)
    out_path.parent.mkdir(exist_ok=True, parents=True)
    with pq.ParquetWriter(out_path, pq_schema) as pq_witer:
        pq_witer.write_table(pa.Table.from_pydict(col_dict, schema=pq_schema))
