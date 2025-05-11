"""Test the index algorithm module."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import polars as pl
import pytest
from lark import Lark

from starrynight.algorithms.index import (
    IMG_FORMATS,
    PCPIndex,
    ast_to_pcp_index,
    gen_pcp_index,
)
from starrynight.algorithms.inventory import FileInventory
from starrynight.parsers.common import BaseTransformer


class MockTransformer(BaseTransformer):
    """Mock transformer for testing."""

    def __init__(self) -> None:
        """Initialize the mock transformer."""
        super().__init__()
        self.channel_dict = {"channel_dict": ["channel1", "channel2"]}

    def transform(self, ast):
        """Return a mock transformation result."""
        return {
            "start": [
                {"dataset_id": "test_dataset"},
                {"batch_id": "test_batch"},
                {"plate_id": "test_plate"},
                {"cycle_id": "1"},
                {"magnification": "10"},
                {"well_id": "A1"},
                {"site_id": "1"},
                # NOTE: Removed filename from here since it's passed separately in ast_to_pcp_index
                {"extension": "tiff"},
            ]
        }


@pytest.fixture
def mock_file_inventory():
    """Create a mock file inventory for testing."""
    return FileInventory(
        key="path/to/test_file.tiff",
        filename="test_file",
        extension=".tiff",
        prefix="path/to",
        is_symlink=False,
        mtime=1234567890,
        size=1000,
    )


@pytest.fixture
def mock_parser():
    """Create a mock Lark parser."""
    mock = MagicMock(spec=Lark)
    mock.parse.return_value = "mock_ast"
    return mock


def test_pcp_index_model():
    """Test PCPIndex model properties and validation."""
    # Test basic model creation
    index = PCPIndex(
        key="path/to/test_file.tiff",
        prefix="path/to",
        dataset_id="test_dataset",
        batch_id="test_batch",
        plate_id="test_plate",
        cycle_id="1",
        magnification="10X",
        well_id="A1",
        site_id="1",
        channel_dict=["channel1", "channel2"],
        filename="test_file",
        extension="tiff",
    )

    # Verify model properties
    assert index.key == "path/to/test_file.tiff"
    assert index.dataset_id == "test_dataset"
    assert index.batch_id == "test_batch"
    assert index.plate_id == "test_plate"
    assert index.cycle_id == "1"
    assert index.well_id == "A1"
    assert index.site_id == "1"
    assert index.filename == "test_file"
    assert index.extension == "tiff"
    assert index.channel_dict == ["channel1", "channel2"]

    # Verify computed properties
    assert index.is_image is True
    assert (
        index.is_sbs_image is True
    )  # True because extension is in IMG_FORMATS and cycle_id is not None
    assert index.is_dir is False  # False because extension is not None


def test_pcp_index_validation():
    """Test validation logic in PCPIndex model."""
    # Test is_image validation
    for ext in IMG_FORMATS:
        index = PCPIndex(key="path/to/file", extension=ext)
        assert index.is_image is True

    # Non-image file should have is_image=False
    index = PCPIndex(key="path/to/file", extension="txt")
    assert index.is_image is False

    # Test is_sbs_image validation (requires both image extension and cycle_id)
    index = PCPIndex(key="path/to/file", extension="tiff", cycle_id="1")
    assert index.is_sbs_image is True

    index = PCPIndex(key="path/to/file", extension="tiff", cycle_id=None)
    assert index.is_sbs_image is False

    # Test is_dir validation
    index = PCPIndex(key="path/to/dir")  # No extension
    assert index.is_dir is True

    index = PCPIndex(key="path/to/file", extension="tiff")
    assert index.is_dir is False


def test_ast_to_pcp_index(mock_file_inventory, mock_parser):
    """Test ast_to_pcp_index function."""
    result = ast_to_pcp_index(mock_file_inventory, mock_parser, MockTransformer)

    # Verify parser and transformer were called correctly
    mock_parser.parse.assert_called_once_with(mock_file_inventory.key)

    # Verify result properties
    assert isinstance(result, PCPIndex)
    assert result.key == mock_file_inventory.key
    assert result.prefix == mock_file_inventory.prefix
    assert result.filename == mock_file_inventory.filename
    assert result.dataset_id == "test_dataset"
    assert result.batch_id == "test_batch"
    assert result.plate_id == "test_plate"
    assert result.cycle_id == "1"
    assert result.well_id == "A1"
    assert result.site_id == "1"
    assert result.extension == "tiff"
    assert result.channel_dict == ["channel1", "channel2"]


@patch("starrynight.algorithms.index.pl.read_parquet")
@patch("starrynight.algorithms.index.write_pq")
@patch("starrynight.algorithms.index.tqdm")
@patch("starrynight.algorithms.index.ast_to_pcp_index")
def test_gen_pcp_index(
    mock_ast_to_pcp_index,
    mock_tqdm,
    mock_write_pq,
    mock_read_parquet,
    mock_parser,
):
    """Test gen_pcp_index function."""
    # Create mock data for testing
    mock_df = pl.DataFrame(
        {
            "key": ["path/to/test_file.tiff"],
            "filename": ["test_file"],
            "extension": [".tiff"],
            "prefix": ["path/to"],
            "is_symlink": [False],
            "mtime": [1234567890],
            "size": [1000],
        }
    )
    mock_read_parquet.return_value = mock_df

    # Mock tqdm to return the dataframe iterator directly
    mock_tqdm.return_value = mock_df.iter_slices()

    # Create a return value for ast_to_pcp_index
    mock_result = PCPIndex(
        key="path/to/test_file.tiff",
        prefix="path/to",
        filename="test_file",
        extension="tiff",
        dataset_id="test_dataset",
        batch_id="test_batch",
    )
    mock_ast_to_pcp_index.return_value = mock_result

    # Run the function
    gen_pcp_index(
        inv_path=Path("/test/inventory.parquet"),
        out_path=Path("/test/output"),
        path_parser=mock_parser,
        ast_tansformer=MockTransformer,
    )

    # Verify read_parquet was called with correct args
    mock_read_parquet.assert_called_once()

    # Verify write_pq was called with correct args
    mock_write_pq.assert_called_once()

    # Assert that ast_to_pcp_index was called with the correct arguments
    # The first argument should be a FileInventory object with the mock data
    mock_ast_to_pcp_index.assert_called()

    # Verify that write_pq was called with the PCPIndex type and correct path
    args, kwargs = mock_write_pq.call_args
    assert args[1] == PCPIndex
    assert str(args[2]).endswith("/test/output/index.parquet")


@patch("starrynight.algorithms.index.ast_to_pcp_index")
@patch("starrynight.algorithms.index.pl.read_parquet")
@patch("starrynight.algorithms.index.write_pq")
@patch("starrynight.algorithms.index.tqdm")
def test_gen_pcp_index_error_handling(
    mock_tqdm,
    mock_write_pq,
    mock_read_parquet,
    mock_ast_to_pcp_index,
    mock_parser,
):
    """Test error handling in gen_pcp_index function."""
    # Create mock data with multiple records
    mock_df = pl.DataFrame(
        {
            "key": ["path/to/good_file.tiff", "path/to/bad_file.tiff"],
            "filename": ["good_file", "bad_file"],
            "extension": [".tiff", ".tiff"],
            "prefix": ["path/to", "path/to"],
            "is_symlink": [False, False],
            "mtime": [1234567890, 1234567891],
            "size": [1000, 1001],
        }
    )
    mock_read_parquet.return_value = mock_df

    # Mock tqdm to return the dataframe iterator directly
    mock_tqdm.return_value = mock_df.iter_slices()

    # Make ast_to_pcp_index succeed for first record and fail for second
    def side_effect(inv, parser, transformer) -> PCPIndex:
        if inv.filename == "good_file":
            # Create dummy data structure similar to what gen_pcp_index expects
            parsed_data = {
                k: [] for k in PCPIndex.model_construct().model_fields.keys()
            }

            # Add one record of good data
            for key in parsed_data:
                if key == "key":
                    parsed_data[key].append(inv.key)
                elif key == "filename":
                    parsed_data[key].append(inv.filename)
                elif key == "extension":
                    parsed_data[key].append(inv.extension.replace(".", ""))
                elif key == "dataset_id":
                    parsed_data[key].append("test_dataset")
                else:
                    parsed_data[key].append(None)

            # When this function is called, simulate return, but set mock_write_pq for test
            mock_write_pq.reset_mock()  # Reset previous call count

            # Create a real PCPIndex object for return
            return PCPIndex(
                key=inv.key,
                prefix=inv.prefix,
                filename=inv.filename,
                extension="tiff",
                dataset_id="test_dataset",
            )
        else:
            raise ValueError("Test error")

    mock_ast_to_pcp_index.side_effect = side_effect

    # Run the function with print mocked to verify error message
    with patch("builtins.print") as mock_print:
        gen_pcp_index(
            inv_path=Path("/test/inventory.parquet"),
            out_path=Path("/test/output"),
            path_parser=mock_parser,
            ast_tansformer=MockTransformer,
        )

    # Verify error handling for bad record
    assert mock_print.call_count > 0
    call_args = mock_print.call_args_list[0][0][0]
    assert "Unable to parse" in call_args
    assert "Test error" in call_args
