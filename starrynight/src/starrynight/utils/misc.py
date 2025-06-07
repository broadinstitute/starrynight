"""Misc utilities."""

from pathlib import Path

import pyarrow as pa
from cloudpathlib import CloudPath
from pyarrow import parquet as pq
from pydantic import BaseModel

from starrynight.utils.py_to_pa import get_pyarrow_schema


def anywidgets_path() -> Path:
    """Get path to anywidgets directory.

    Returns
    -------
    Path
        Path to anywidgets directory.

    """
    return Path(__file__).parents[4].joinpath("canvas/anywidgets/_build")


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
    # HACK: Temporary fix for issue #131 - path duplication bug
    # 
    # ORIGINAL DESIGN INTENT:
    # This function was designed to support portable workflows where:
    # - Index files contain only relative paths (relative to dataset root)
    # - path_mask provides the absolute base path for the current machine/container
    # - This allows the same index to be used across different machines where
    #   data is mounted at different locations (e.g., local vs container environments)
    #
    # THE BUG:
    # The original implementation had path overlap issues where both path_mask
    # and filepath contained overlapping directory components, leading to 
    # duplication like: /path/to/scratch/scratch/data/file.txt
    #
    # CURRENT HACK:
    # We now ignore path_mask entirely and just resolve filepath to absolute.
    # This breaks the portability feature but fixes the immediate duplication bug.
    #
    # FUTURE PLAN:
    # The developer intends to properly fix this later by:
    # 1. Ensuring index generation creates truly relative paths
    # 2. Fixing path_mask derivation logic  
    # 3. Implementing proper overlap detection in path resolution
    # 4. Restoring the original portability design
    #
    # For now, this hack allows the pipeline to work with user-provided paths.
    
    # Just ignore path_mask and return filepath as absolute
    return f"{filepath.resolve()}/"


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
