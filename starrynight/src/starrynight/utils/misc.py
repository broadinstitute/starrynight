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


def resolve_path_loaddata(
    path_mask: Path | CloudPath, filepath: Path | CloudPath
) -> str:
    """Resolve filepaths for loaddata.

    Parameters
    ----------
    path_mask : Path | CloudPath
        Path used for masking filepath from index
    filepath : Path | CloudPath
        Path of the file in index

    """
    # print(f"Path mask: {path_mask}")
    # print(f"File path: {filepath}")
    # try:
    #     filepath.resolve().relative_to(path_mask.resolve())
    #     print(f"Relative path: {filepath.absolute().__str__()}")
    #     return filepath.resolve().__str__()
    # except ValueError:
    #     print(
    #         f"Absolute path:{path_mask.resolve().__str__().rstrip('/')}/{filepath.__str__().lstrip('/')}/"
    #     )
    if filepath.is_absolute():
        return filepath
    else:
        return f"{path_mask.resolve().__str__().rstrip('/')}/{filepath.__str__().lstrip('/')}/"


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
    with out_path.open("wb") as f:
        with pq.ParquetWriter(f, pq_schema) as pq_witer:
            pq_witer.write_table(
                pa.Table.from_pydict(col_dict, schema=pq_schema)
            )


def merge_pq(
    files_list: list[CloudPath | Path], out_file: CloudPath | Path
) -> None:
    """Merge parquet files.

    Parameters
    ----------
    files_list : list[CloudPath | Path]
        List of file paths to merge
    out_file : CloudPath | Path
        Path to merged file

    """
    schema = pq.ParquetFile(files_list[0]).schema_arrow
    with out_file.open("wb") as f:
        with pq.ParquetWriter(f, schema=schema) as writer:
            for file in files_list:
                if isinstance(file, CloudPath):
                    file = file.fspath
                writer.write_table(pq.read_table(file, schema=schema))
