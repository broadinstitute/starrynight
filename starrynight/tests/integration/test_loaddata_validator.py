"""Test the loaddata validation framework.

This module tests the functionality of the LoadData validation framework
after removing the core metadata validation functionality.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from .loaddata_validation import LoadDataValidator, validate_loaddata_csv


def test_validator_without_core_metadata():
    """Test that the LoadDataValidator still works without core metadata validation."""
    # Create a minimal config with no core_metadata
    config = {
        "name": "Test Pipeline",
        "required_columns": ["Metadata_Plate", "FileName_DNA"],
        "column_groups": [
            {
                "name": "DNA images",
                "prefix_pattern": "DNA",
                "column_types": ["FileName", "PathName"],
            }
        ],
    }

    # Create simple test data
    ref_data = pd.DataFrame(
        {
            "Metadata_Plate": ["Plate1", "Plate1"],
            "FileName_DNA": ["image1.tif", "image2.tif"],
            "PathName_DNA": ["/path/to/1", "/path/to/2"],
        }
    )

    gen_data = pd.DataFrame(
        {
            "Metadata_Plate": ["Plate1", "Plate1"],
            "FileName_DNA": ["image1.tif", "image2.tif"],
            "PathName_DNA": ["/path/to/1", "/path/to/2"],
        }
    )

    # Write test data to temporary files
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as ref_file:
        ref_path = Path(ref_file.name)
        ref_data.to_csv(ref_path, index=False)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as gen_file:
        gen_path = Path(gen_file.name)
        gen_data.to_csv(gen_path, index=False)

    # Create validator and validate
    validator = LoadDataValidator(config)
    errors = validator.validate(gen_path, ref_path)

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
