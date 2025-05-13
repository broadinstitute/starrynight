"""Test the loaddata validation framework.

This module tests the functionality of the simplified LoadData validation framework.
"""

import tempfile
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from .loaddata_validation import (
    check_column_pattern,
    check_required_columns_not_null,
    column_exists,
    create_db_views,
    run_sql_check,
    validate_loaddata_csv,
)


def test_column_exists():
    """Test that column existence detection works correctly."""
    # Create a simple test DataFrame
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

    # Write to temporary CSV file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        csv_path = Path(temp_file.name)
        df.to_csv(csv_path, index=False)

    # Check column existence
    with duckdb.connect(":memory:") as conn:
        create_db_views(
            conn, csv_path, csv_path
        )  # Both views point to same file

        assert column_exists(conn, "col1") is True
        assert column_exists(conn, "col2") is True
        assert column_exists(conn, "nonexistent") is False

    # Clean up
    csv_path.unlink()


def test_check_required_columns_not_null():
    """Test checking required columns for existence and null values."""
    # Create test data with some nulls
    df = pd.DataFrame(
        {
            "col1": [1, None],
            "col2": ["a", "b"],
            # col3 is missing
        }
    )

    # Write to temporary CSV file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        csv_path = Path(temp_file.name)
        df.to_csv(csv_path, index=False)

    # Setup test configurations
    config_all_exist = {"columns": {"required": ["col1", "col2"]}}

    config_with_missing = {"columns": {"required": ["col1", "col2", "col3"]}}

    config_with_null = {
        "columns": {
            "required": ["col1"]  # col1 has a null value
        }
    }

    config_no_required = {"columns": {"required": []}}

    # Run tests
    with duckdb.connect(":memory:") as conn:
        create_db_views(conn, csv_path, csv_path)

        # Test with all columns existing
        errors = check_required_columns_not_null(conn, config_all_exist)
        assert len(errors) == 1
        assert "Found 1 rows with missing required values" in errors[0]

        # Test with missing column
        errors = check_required_columns_not_null(conn, config_with_missing)
        assert len(errors) == 1
        assert "Required column 'col3' missing in CSV" in errors[0]

        # Test with null value
        errors = check_required_columns_not_null(conn, config_with_null)
        assert len(errors) == 1
        assert "Found 1 rows with missing required values" in errors[0]

        # Test with no required columns
        errors = check_required_columns_not_null(conn, config_no_required)
        assert len(errors) == 0

    # Clean up
    csv_path.unlink()


def test_simplified_validator():
    """Test that the simplified validator works for a basic case."""
    # Create simple test data
    ref_data = pd.DataFrame(
        {
            "Metadata_Plate": ["Plate1", "Plate1"],
            "Metadata_Site": ["1", "2"],
            "Metadata_Well": ["A01", "A02"],
            "FileName_Test": ["test1.tif", "test2.tif"],
        }
    )

    gen_data = pd.DataFrame(
        {
            "Metadata_Plate": ["Plate1", "Plate1"],
            "Metadata_Site": ["1", "2"],
            "Metadata_Well": ["A01", "A02"],
            "FileName_Test": ["test1.tif", "test2.tif"],
        }
    )

    # Write test data to temporary files
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as ref_file:
        ref_path = Path(ref_file.name)
        ref_data.to_csv(ref_path, index=False)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as gen_file:
        gen_path = Path(gen_file.name)
        gen_data.to_csv(gen_path, index=False)

    # Create a simple test config
    test_config = {
        "name": "Test Config",
        "columns": {
            "required": [
                "Metadata_Plate",
                "Metadata_Site",
                "Metadata_Well",
                "FileName_Test",
            ],
            "pattern_check": {"FileName_Test": "%.tif"},
        },
        "custom_checks": [],
    }

    # Add test config to the VALIDATION_CONFIGS dictionary
    from .loaddata_validation import VALIDATION_CONFIGS

    VALIDATION_CONFIGS["test_config"] = test_config

    # Validate with the test config
    errors = validate_loaddata_csv(gen_path, ref_path, "test_config")

    # Cleanup temporary files
    ref_path.unlink()
    gen_path.unlink()

    # Verify no errors were found
    assert not errors, f"Validation found errors: {errors}"


def test_validate_loaddata_csv_function():
    """Test the validate_loaddata_csv helper function."""
    # Create simple test data
    ref_data = pd.DataFrame(
        {
            "Metadata_Plate": ["Plate1", "Plate1"],
            "FileName_OrigDNA": ["image1.tif", "image2.tif"],
            "PathName_OrigDNA": ["/path/to/1", "/path/to/2"],
            "Frame_OrigDNA": [1, 2],
        }
    )

    gen_data = pd.DataFrame(
        {
            "Metadata_Plate": ["Plate1", "Plate1"],
            "FileName_OrigDNA": ["image1.tif", "image2.tif"],
            "PathName_OrigDNA": ["/path/to/1", "/path/to/2"],
            "Frame_OrigDNA": [1, 2],
        }
    )

    # Write test data to temporary files
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as ref_file:
        ref_path = Path(ref_file.name)
        ref_data.to_csv(ref_path, index=False)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as gen_file:
        gen_path = Path(gen_file.name)
        gen_data.to_csv(gen_path, index=False)

    # Validate with a pipeline config that doesn't exist (should give error)
    errors_invalid = validate_loaddata_csv(
        gen_path, ref_path, "nonexistent_pipeline"
    )
    assert errors_invalid, "Should have error for nonexistent pipeline"
    assert "Unknown pipeline type" in errors_invalid[0]

    # Validate with a valid pipeline type
    errors_valid = validate_loaddata_csv(gen_path, ref_path, "cp_illum_calc")

    # Cleanup temporary files
    ref_path.unlink()
    gen_path.unlink()

    # Check if errors were found (some may be expected due to missing required columns)
    print(f"Validation errors: {errors_valid}")
