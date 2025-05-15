"""Tests for fixture functionality."""

import json
from pathlib import Path

import duckdb
import pytest

# Fixtures are automatically available from conftest.py

# Note on fixture relationships:
# - fix_starrynight_basic_setup: Runs CLI workflow to generate test files (slow but validates CLI)
# - fix_starrynight_pregenerated_setup: Copies pre-generated files (fast, for downstream tests)
# Both fixtures provide the same output contract but serve different testing purposes.


@pytest.mark.parametrize(
    "fix_starrynight_setup",
    [
        {"mode": "generated", "fixture": "fix_s1"},
        {"mode": "pregenerated", "fixture": "fix_s1"},
        {"mode": "generated", "fixture": "fix_s2"},
        {"mode": "pregenerated", "fixture": "fix_s2"},
    ],
    indirect=True,
)
def test_starrynight_setup_fixtures(fix_starrynight_setup, request):
    """Test all fixture modes and configurations with identical validation logic.

    This test uses explicit parameterization to run against all combinations:
    - Modes: "generated" vs "pregenerated"
    - Fixtures: "fix_s1" vs "fix_s2"

    This ensures that all fixture configurations work correctly regardless of how
    they're created (via CLI or from pre-generated files).
    """
    # The fixture is provided directly
    setup_fixture = fix_starrynight_setup

    # Get paths from fixture
    index_file = setup_fixture["index_file"]
    experiment_json_path = setup_fixture["experiment_json_path"]
    assert index_file.suffix == ".parquet", "Index file is not a parquet file"

    # Validate index.parquet file using DuckDB
    try:
        # Create a connection to an in-memory DuckDB instance
        con = duckdb.connect(database=":memory:")

        # Check that the file exists and has rows
        row_count = con.execute(
            f"SELECT COUNT(*) FROM '{index_file}'"
        ).fetchone()[0]
        assert row_count > 0, "Index parquet file is empty"

        # Get column names from the parquet file
        columns_result = con.execute(
            f"SELECT * FROM '{index_file}' LIMIT 0"
        ).description
        column_names = [col[0] for col in columns_result]

        # Check for essential columns
        essential_columns = [
            "dataset_id",
            "plate_id",
            "well_id",
            "site_id",
            "extension",
            "is_sbs_image",
            "is_image",
            "channel_dict",
        ]
        for col in essential_columns:
            assert col in column_names, (
                f"Missing essential column '{col}' in index file"
            )

    except Exception as e:
        pytest.fail(f"Failed to validate index parquet file with DuckDB: {e}")

    # Validate experiment.json file
    try:
        with experiment_json_path.open() as f:
            experiment_config = json.load(f)

        # Check for essential sections
        assert "cp_config" in experiment_config, (
            "Missing cp_config section in experiment JSON"
        )
        assert "sbs_config" in experiment_config, (
            "Missing sbs_config section in experiment JSON"
        )

    except json.JSONDecodeError:
        pytest.fail("Experiment JSON file contains invalid JSON")
    except Exception as e:
        pytest.fail(f"Failed to validate experiment JSON: {e}")

    # Verify data type coverage - check both SBS and CP images exist
    image_counts = con.execute(f"""
        SELECT
            SUM(CASE WHEN is_sbs_image THEN 1 ELSE 0 END) as sbs_count,
            SUM(CASE WHEN NOT is_sbs_image AND is_image THEN 1 ELSE 0 END) as cp_count
        FROM '{index_file}'
    """).fetchone()

    sbs_count = image_counts[0]
    cp_count = image_counts[1]

    assert sbs_count > 0, "No SBS images found in index"
    assert cp_count > 0, "No CP (non-SBS) images found in index"

    # Verify well/site structure - check for multiple wells and sites
    well_count = con.execute(f"""
        SELECT COUNT(DISTINCT well_id)
        FROM '{index_file}'
    """).fetchone()[0]

    assert well_count >= 2, f"Expected multiple wells, found {well_count}"

    # Get minimum sites per well count to verify multi-site structure
    min_sites = con.execute(f"""
        SELECT MIN(site_count)
        FROM (
            SELECT well_id, COUNT(DISTINCT site_id) as site_count
            FROM '{index_file}'
            GROUP BY well_id
        )
    """).fetchone()[0]

    assert min_sites >= 2, "Expected multiple sites per well"

    # Verify channel patterns - SBS and CP should have different channels
    if "channel_dict" in column_names:
        # This approach handles the list-type channel_dict column
        # Get sample channels from SBS and CP images
        sbs_sample = con.execute(f"""
            SELECT channel_dict
            FROM '{index_file}'
            WHERE is_sbs_image
            LIMIT 1
        """).fetchone()[0]

        cp_sample = con.execute(f"""
            SELECT channel_dict
            FROM '{index_file}'
            WHERE NOT is_sbs_image AND is_image
            LIMIT 1
        """).fetchone()[0]

        # DuckDB will return these as Python lists
        assert len(sbs_sample) > 0, "Empty SBS channel pattern"
        assert len(cp_sample) > 0, "Empty CP channel pattern"

        # Check that SBS and CP have different channel patterns
        assert set(sbs_sample) != set(cp_sample), (
            "SBS and CP should have different channel patterns"
        )

    # Verify file types - without hardcoding specific extensions
    extensions = con.execute(f"""
        SELECT DISTINCT extension
        FROM '{index_file}'
        WHERE is_image
    """).fetchall()

    image_extensions = [ext[0] for ext in extensions]
    assert len(image_extensions) > 0, "No image file extensions found"
    assert all(
        ext in ["tiff", "tif", "png", "jpg", "jpeg", "ome.tiff", "ome.tif"]
        for ext in image_extensions
    ), f"Found unexpected image extensions: {image_extensions}"

    # Verify consistent batch, dataset and plate values
    id_counts = con.execute(f"""
        SELECT
            COUNT(DISTINCT dataset_id) as dataset_count,
            COUNT(DISTINCT batch_id) as batch_count
        FROM '{index_file}'
    """).fetchone()

    assert id_counts[0] == 1, "Multiple dataset IDs found"
    assert id_counts[1] == 1, "Multiple batch IDs found"

    # Print some debug information
    # Get current parameter value for the parameterized test
    current_param = request.node.callspec.params.get("fix_starrynight_setup")
    mode = current_param.get("mode")
    fixture = current_param.get("fixture")
    print(f"Testing fixture={fixture}, mode={mode}")
    print(f"Index file location: {index_file}")
    print(f"Experiment JSON location: {experiment_json_path}")
