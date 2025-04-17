"""File globbing utils."""

from enum import Enum
from pathlib import Path

from cloudpathlib import CloudPath


class HierarchyType(Enum):
    """Hierarchy type enum."""

    BATCH = "batch"
    PLATE = "plate"
    WELL = "well"
    SITE = "site"
    CYCLE = "cycle"


def get_files_by(
    hierarchy_list: list[str], root_dir: Path | CloudPath, file_glob: str
) -> dict:
    """Recursively retrieves files from directories in a hierarchical structure.

    The function explores the directories in `root_dir` according to the provided
    `hierarchy_list` and returns a dictionary that maps each directory name to a
    list of file paths matching the given `file_glob` pattern. If there are multiple
    levels in `hierarchy_list`, the function recursively calls itself to navigate
    deeper into the directory hierarchy.

    Parameters
    ----------
    hierarchy_list : list of HierarchyType
        A list of hierarchical levels to traverse. Each level corresponds to
        a directory in the structure that will be explored. If there is more than
        one level, the function will recurse into subdirectories.

    root_dir : Path | CloudPath
        The root directory in which to start searching for files. It is expected
        to be a `Path` object that points to the base folder.

    file_glob : str
        A glob pattern used to match filenames in each directory. Only files that
        match this pattern will be included in the result.

    Returns
    -------
    dict
        A dictionary where the keys are directory names (strings) and the values
        are lists of `Path` objects representing files that match the `file_glob`
        pattern within each directory. If there are multiple hierarchical levels,
        the value for each directory will be a nested dictionary corresponding to
        the next level of hierarchy.

    Notes
    -----
    The function first checks if the `hierarchy_list` has a length of 1, in which
    case it directly searches for files in the directories at the first level of
    the hierarchy. If `hierarchy_list` has more than one element, the function
    recursively descends into subdirectories and collects matching files at each
    level.

    Example
    -------
    >>> from pathlib import Path
    >>> hierarchy_list = ['level1', 'level2']
    >>> root_dir = Path('/path/to/root')
    >>> file_glob = '*.txt'
    >>> get_files_by(hierarchy_list, root_dir, file_glob)
    {'dir1': {'subdir1': [PosixPath('/path/to/root/dir1/subdir1/file1.txt')]}}

    """
    term_dirs = [dir.stem for dir in root_dir.glob("*") if dir.is_dir()]
    hierarchy_dict = {}
    if len(hierarchy_list) == 1:
        for dir in term_dirs:
            files = [
                file
                for file in root_dir.joinpath(dir).glob(file_glob)
                if not file.is_dir()
            ]
            hierarchy_dict[dir] = files
    else:
        for dir in term_dirs:
            hierarchy_dict[dir] = get_files_by(
                hierarchy_list[1:], root_dir.joinpath(dir), file_glob
            )
    return hierarchy_dict


def flatten_dict(
    nested_dict: dict, path: list[str] = []
) -> list[tuple[list[str], list]]:
    """Flattens a nested dictionary into a list of tuples.

    Each tuple contains a list of directory names (nested levels) and the associated
    value at the deepest level of the nested structure.
    The function recursively navigates the dictionary, collecting directory
    names as it goes and adding the corresponding values at the deepest level.

    Parameters
    ----------
    nested_dict : dict
        The dictionary to flatten. It can be arbitrarily nested and contain lists
        of files as values at the deepest levels.

    path : list of str, optional
        The list that keeps track of the directory names as we traverse deeper. It's
        used internally during recursion and doesn't need to be passed by the user.

    Returns
    -------
    list of tuple
        A list of tuples where each tuple contains:
        - A list of directory names (path to the final directory),
        - A list of files at the deepest directory level.

    Notes
    -----
    This function is recursive and will process all levels of nested dictionaries.

    Example
    -------
    >>> nested_dict = {
    >>>     'dir1': {
    >>>         'subdir1': ['file1.txt', 'file2.txt'],
    >>>         'subdir2': ['file3.txt']
    >>>     },
    >>>     'dir2': ['file4.txt']
    >>> }
    >>> flatten_dict(nested_dict)
    [
        (['dir1', 'subdir1'], ['file1.txt', 'file2.txt']),
        (['dir1', 'subdir2'], ['file3.txt']),
        (['dir2'], ['file4.txt'])
    ]

    """
    flattened = []

    if isinstance(nested_dict, dict):
        for key, value in nested_dict.items():
            # Recursively call flatten_dict for nested dictionaries
            flattened.extend(flatten_dict(value, path + [key]))
    else:
        # If the current value is a list (final directory files), append it
        flattened.append((path, nested_dict))

    return flattened
