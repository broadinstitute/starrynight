"""Test the index algorithm functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

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
    """Simple mock transformer for testing."""

    def __init__(self) -> None:
        """Initialize the mock transformer."""
        super().__init__()
        self.channel_dict = {"channel_dict": ["channel1", "channel2"]}

    def transform(self, ast):
        """Return a simplified mock transformation result."""
        return {
            "start": [
                {"dataset_id": "test_dataset"},
                {"batch_id": "test_batch"},
                {"plate_id": "test_plate"},
                {"cycle_id": "1"},
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


class TestPCPIndex:
    """Tests for the PCPIndex model."""

    def test_basic_properties(self):
        """Test PCPIndex model creation and basic properties."""
        # Create a minimal test instance
        index = PCPIndex(
            key="path/to/test_file.tiff",
            extension="tiff",
            cycle_id="1",
        )

        # Test basic properties
        assert index.key == "path/to/test_file.tiff"
        assert index.extension == "tiff"
        assert index.cycle_id == "1"

        # Test computed properties
        assert index.is_image is True
        assert index.is_sbs_image is True
        assert index.is_dir is False

    def test_extension_validation(self):
        """Test extension-based validation in PCPIndex."""
        # Test valid image extensions
        for ext in IMG_FORMATS:
            index = PCPIndex(key="path/to/file", extension=ext)
            assert index.is_image is True

        # Test non-image extension
        index = PCPIndex(key="path/to/file", extension="txt")
        assert index.is_image is False

    def test_dir_validation(self):
        """Test directory validation in PCPIndex."""
        # Test directory (no extension)
        index = PCPIndex(key="path/to/dir")
        assert index.is_dir is True

        # Test file (has extension)
        index = PCPIndex(key="path/to/file", extension="tiff")
        assert index.is_dir is False


def test_ast_to_pcp_index(mock_file_inventory, mock_parser):
    """Test ast_to_pcp_index function with mocks."""
    # Call the function with mocks
    result = ast_to_pcp_index(mock_file_inventory, mock_parser, MockTransformer)

    # Verify parser was called correctly
    mock_parser.parse.assert_called_once_with(mock_file_inventory.key)

    # Verify basic result properties
    assert isinstance(result, PCPIndex)
    assert result.key == mock_file_inventory.key
    assert result.dataset_id == "test_dataset"
    assert result.batch_id == "test_batch"
    assert result.extension == "tiff"


@patch("starrynight.algorithms.index.pl.read_parquet")
@patch("starrynight.algorithms.index.write_pq")
@patch("starrynight.algorithms.index.tqdm")
def test_gen_pcp_index(
    mock_tqdm, mock_write_pq, mock_read_parquet, mock_parser
):
    """Test gen_pcp_index function."""
    # Create simplified mock data
    mock_df = pl.DataFrame(
        {"key": ["test.tiff"], "filename": ["test"], "extension": [".tiff"]}
    )
    mock_read_parquet.return_value = mock_df
    mock_tqdm.return_value = mock_df.iter_slices()

    # Run the function
    gen_pcp_index(
        inv_path=Path("/test/inventory.parquet"),
        out_path=Path("/test/output"),
        path_parser=mock_parser,
        ast_tansformer=MockTransformer,
    )

    # Verify core interactions
    mock_read_parquet.assert_called_once()
    mock_write_pq.assert_called_once()

    # Verify output path
    args, _ = mock_write_pq.call_args
    assert str(args[2]).endswith("/test/output/index.parquet")


@patch("starrynight.algorithms.index.ast_to_pcp_index")
@patch("starrynight.algorithms.index.pl.read_parquet")
def test_gen_pcp_index_error_handling(
    mock_read_parquet, mock_ast_to_pcp_index, mock_parser
):
    """Test error handling in gen_pcp_index function."""
    # Create mock data with good and bad records
    mock_df = pl.DataFrame(
        {
            "key": ["good.tiff", "bad.tiff"],
            "filename": ["good", "bad"],
            "extension": [".tiff", ".tiff"],
        }
    )
    mock_read_parquet.return_value = mock_df

    # Setup mock to succeed for good file and fail for bad file
    def side_effect(inv: FileInventory, *args: object) -> PCPIndex:
        if inv.filename == "good":
            return PCPIndex(key=inv.key, extension="tiff")
        else:
            raise ValueError("Test error")

    mock_ast_to_pcp_index.side_effect = side_effect

    # Run with print mocked to verify error message
    with patch("builtins.print") as mock_print:
        with patch(
            "starrynight.algorithms.index.tqdm",
            return_value=mock_df.iter_slices(),
        ):
            with patch("starrynight.algorithms.index.write_pq"):
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
