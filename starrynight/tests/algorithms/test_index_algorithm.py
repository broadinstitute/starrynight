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

    def transform(self, ast) -> dict:
        """Return a simplified mock transformation result.

        Args:
            ast: The abstract syntax tree to transform

        Returns:
            Dictionary with mock transformation data

        """
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
def mock_file_inventory() -> FileInventory:
    """Create a mock file inventory for testing.

    Returns:
        A FileInventory object with test data.

    """
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
def mock_parser() -> MagicMock:
    """Create a mock Lark parser.

    Returns:
        A MagicMock object that simulates a Lark parser.

    """
    mock = MagicMock(spec=Lark)
    mock.parse.return_value = "mock_ast"
    return mock


class TestPCPIndex:
    """Tests for the PCPIndex model.

    This test class verifies the behavior of the PCPIndex model, which is used
    to represent indexed image files in the PCP (plate-cycle-position) format.
    """

    def test_basic_properties(self):
        """Test PCPIndex model creation and basic properties.

        Verifies that a PCPIndex instance correctly initializes with provided
        values and computes derived properties.
        """
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

    @pytest.mark.parametrize(
        "extension,expected",
        [
            ("tiff", True),
            ("tif", True),
            ("png", True),
            ("txt", False),
            ("csv", False),
        ],
    )
    def test_extension_validation(self, extension: str, expected: bool):
        """Test extension-based validation in PCPIndex.

        Args:
            extension: File extension to test
            expected: Whether it should be classified as an image

        """
        index = PCPIndex(key=f"path/to/file.{extension}", extension=extension)
        assert index.is_image is expected, (
            f"Extension '{extension}' should {'be' if expected else 'not be'} classified as an image"
        )

    @pytest.mark.parametrize(
        "key,extension,expected",
        [("path/to/dir", None, True), ("path/to/file", "tiff", False)],
    )
    def test_dir_validation(self, key: str, extension: str, expected: bool):
        """Test directory validation in PCPIndex.

        Args:
            key: File path to test
            extension: File extension (None for directories)
            expected: Whether it should be classified as a directory

        """
        index = (
            PCPIndex(key=key, extension=extension)
            if extension
            else PCPIndex(key=key)
        )
        assert index.is_dir is expected, (
            f"Path '{key}' should {'be' if expected else 'not be'} classified as a directory"
        )


def test_ast_to_pcp_index(mock_file_inventory, mock_parser):
    """Test ast_to_pcp_index function with mocks.

    Verifies that the function correctly converts a file inventory and AST
    into a PCPIndex object with proper properties.

    Args:
        mock_file_inventory: Fixture providing test inventory data
        mock_parser: Fixture providing a mock Lark parser

    """
    # Call the function with mocks
    result = ast_to_pcp_index(mock_file_inventory, mock_parser, MockTransformer)

    # Verify parser was called correctly
    mock_parser.parse.assert_called_once_with(mock_file_inventory.key)

    # Verify basic result properties
    assert isinstance(result, PCPIndex), "Result should be a PCPIndex instance"
    assert result.key == mock_file_inventory.key, (
        "Key should match the inventory key"
    )
    assert result.dataset_id == "test_dataset", (
        "Dataset ID should be correctly transferred"
    )
    assert result.batch_id == "test_batch", (
        "Batch ID should be correctly transferred"
    )
    assert result.extension == "tiff", (
        "Extension should be correctly transferred"
    )


@patch("starrynight.algorithms.index.pl.read_parquet")
@patch("starrynight.algorithms.index.write_pq")
@patch("starrynight.algorithms.index.tqdm")
def test_gen_pcp_index(
    mock_tqdm, mock_write_pq, mock_read_parquet, mock_parser
):
    """Test gen_pcp_index function.

    Verifies that index generation correctly processes inventory data,
    creates PCPIndex objects, and writes results to the output path.

    Args:
        mock_tqdm: Mock for progress bar
        mock_write_pq: Mock for parquet writing function
        mock_read_parquet: Mock for parquet reading function
        mock_parser: Mock for the path parser

    """
    # Create simplified mock data
    mock_df = pl.DataFrame(
        {"key": ["test.tiff"], "filename": ["test"], "extension": [".tiff"]}
    )
    mock_read_parquet.return_value = mock_df
    # Configure tqdm to iterate through data without progress bar in tests
    mock_tqdm.return_value = mock_df.iter_slices()

    # Run the function
    gen_pcp_index(
        inv_path=Path("/test/inventory.parquet"),
        out_path=Path("/test/output"),
        path_parser=mock_parser,
        ast_tansformer=MockTransformer,
    )

    # Verify core interactions
    # Verify core interactions occurred
    mock_read_parquet.assert_called_once(), "Should read inventory from parquet"
    mock_write_pq.assert_called_once(), "Should write index to parquet"

    # Verify output path is constructed correctly
    args, _ = mock_write_pq.call_args
    assert str(args[2]).endswith("/test/output/index.parquet"), (
        "Output file should be named 'index.parquet' in specified directory"
    )


@patch("starrynight.algorithms.index.ast_to_pcp_index")
@patch("starrynight.algorithms.index.pl.read_parquet")
def test_gen_pcp_index_error_handling(
    mock_read_parquet, mock_ast_to_pcp_index, mock_parser
):
    """Test error handling in gen_pcp_index function.

    Verifies that the function properly handles parsing errors for individual
    files without failing the entire process. Checks that appropriate error
    messages are logged when parsing fails.

    Args:
        mock_read_parquet: Mock for parquet reading function
        mock_ast_to_pcp_index: Mock for index conversion function
        mock_parser: Mock for the path parser

    """
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
    def side_effect(inv: FileInventory, *args: tuple[object, ...]) -> PCPIndex:
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
    assert mock_print.call_count > 0, (
        "Error message should be printed for parsing failures"
    )
    call_args = mock_print.call_args_list[0][0][0]
    assert "Unable to parse" in call_args, (
        "Error message should indicate parsing failure"
    )
    assert "Test error" in call_args, (
        "Original error message should be included"
    )
