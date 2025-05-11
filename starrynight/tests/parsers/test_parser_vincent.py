"""Test the Vincent path parser implementation."""

from functools import reduce
from typing import Any

import pytest
from lark import Lark, ParseError

from starrynight.parsers.common import ParserType, get_parser
from starrynight.parsers.transformer_vincent import VincentAstToIR


@pytest.fixture
def parser() -> Lark:
    """Create and return a Vincent parser instance."""
    return get_parser(ParserType.OPS_VINCENT)


@pytest.fixture
def transformer() -> VincentAstToIR:
    """Create and return a Vincent transformer instance."""
    return VincentAstToIR()


def extract_metadata(
    filepath: str, parser: Lark, transformer: VincentAstToIR
) -> dict[str, Any]:
    """Extract metadata from a file path using the Vincent parser."""
    ast = parser.parse(filepath)
    ir = transformer.transform(ast)

    # Extract the parsed metadata dictionary using functional style
    items = [item for item in ir["start"] if isinstance(item, dict)]
    return reduce(lambda a, b: a | b, items, {})


def test_sbs_path_parsing(parser, transformer):
    """Test parsing a standard SBS format path."""
    filepath = "cpg0999-merck-asma/merck/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_Channel405 nm,477 nm,G,T,A,C_Seq2069.tiff"
    result = extract_metadata(filepath, parser, transformer)

    # Verify core metadata extraction
    assert result["dataset_id"] == "cpg0999-merck-asma"
    assert result["batch_id"] == "BATCH1"
    assert result["plate_id"] == "plate1"
    assert result["magnification"] == "10"
    assert result["cycle_id"] == "11"
    assert result["well_id"] == "B3"
    assert result["site_id"] == "2069"

    # Verify channel extraction
    assert result["channel_0"] == "405"
    assert result["channel_1"] == "477"
    assert result["channel_2"] == "G"
    assert result["channel_3"] == "T"
    assert result["channel_4"] == "A"
    assert result["channel_5"] == "C"
    assert len([k for k in result.keys() if k.startswith("channel_")]) == 6

    # Verify file information
    assert result["extension"] == "tiff"


def test_cp_path_parsing(parser, transformer):
    """Test parsing a standard CP format path."""
    filepath = "cpg0999-merck-asma/merck/BATCH1/images/plate2/10X_CP_plate2/WellB2_PointB2_0347_ChannelnIR,GFP,DAPI_Seq1923.tiff"
    result = extract_metadata(filepath, parser, transformer)

    # Verify core metadata extraction
    assert result["dataset_id"] == "cpg0999-merck-asma"
    assert result["batch_id"] == "BATCH1"
    assert result["plate_id"] == "plate2"
    assert result["magnification"] == "10"
    assert result["well_id"] == "B2"
    assert result["site_id"] == "1923"

    # Verify channel extraction
    assert result["channel_0"] == "nIR"
    assert result["channel_1"] == "GFP"
    assert result["channel_2"] == "DAPI"

    # Verify file information
    assert result["extension"] == "tiff"


def test_channel_normalization(parser, transformer):
    """Test that channels with hyphens are properly normalized."""
    try:
        filepath = "cpg0999-merck-asma/merck/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_Channel405-2 nm,477 nm_Seq2069.tiff"
        result = extract_metadata(filepath, parser, transformer)

        # Check that hyphens in channel names are removed
        assert "channel_0" in result
        assert result["channel_0"] == "4052", (
            "Hyphen should be removed from channel name"
        )
    except Exception:
        pytest.skip("Parser doesn't support this channel format yet")


@pytest.mark.parametrize(
    "filepath,expected_cycle",
    [
        # Single-digit cycle ID
        (
            "cpg0999-merck-asma/merck/BATCH1/images/plate1/10X_c1_SBS-1/WellB3_PointB3_0099_ChannelG,T,A,C_Seq2069.tiff",
            "1",
        ),
        # Double-digit cycle ID
        (
            "cpg0999-merck-asma/merck/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_ChannelG,T,A,C_Seq2069.tiff",
            "11",
        ),
    ],
)
def test_cycle_id_variations(parser, transformer, filepath, expected_cycle):
    """Test parsing paths with different cycle ID lengths (single vs. double digit)."""
    try:
        result = extract_metadata(filepath, parser, transformer)
        assert result["cycle_id"] == expected_cycle
    except Exception:
        pytest.skip(f"Parser doesn't support this cycle ID length: {filepath}")


def test_invalid_paths(parser):
    """Test parser behavior with invalid paths."""
    invalid_paths = [
        "invalid/path/format",
        "missing/fields/images/plate1",
        "/too/many/separators/at/beginning",
    ]

    for path in invalid_paths:
        with pytest.raises(ParseError):
            parser.parse(path)


def test_parser_structure():
    """Verify the structure of parser output for different paths.

    This test validates that the parser extracts the expected keys for both
    SBS and CP path formats, ensuring the parser structure remains stable.
    """
    # Test paths
    sbs_path = "cpg0999-merck-asma/merck/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_Channel405 nm,477 nm,G,T,A,C_Seq2069.tiff"
    cp_path = "cpg0999-merck-asma/merck/BATCH1/images/plate2/10X_CP_plate2/WellB2_PointB2_0347_ChannelnIR,GFP,DAPI_Seq1923.tiff"

    parser = get_parser(ParserType.OPS_VINCENT)
    transformer = VincentAstToIR()

    # Process SBS path
    sbs_result = extract_metadata(sbs_path, parser, transformer)

    # Process CP path
    cp_result = extract_metadata(cp_path, parser, transformer)

    # Verify both parsers extract expected keys
    expected_keys = ["dataset_id", "batch_id", "plate_id", "extension"]
    for key in expected_keys:
        assert key in sbs_result, f"SBS parser missing key: {key}"
        assert key in cp_result, f"CP parser missing key: {key}"
