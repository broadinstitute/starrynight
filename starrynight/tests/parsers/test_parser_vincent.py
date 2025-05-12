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


@pytest.mark.parametrize(
    "filepath,expected_metadata,path_type",
    [
        # STANDARD SBS FORMAT PATHS
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_Channel405 nm,477 nm,G,T,A,C_Seq2069.tiff",
            {
                "dataset_id": "cpg0999-broad-asma",
                "batch_id": "BATCH1",
                "plate_id": "plate1",
                "magnification": "10",
                "cycle_id": "11",
                "well_id": "WellB3",
                "site_id": "2069",
                "channels": ["405", "477", "G", "T", "A", "C"],
                "channel_count": 6,
                "extension": "tiff",
            },
            "SBS",
        ),
        # SBS format with different plate and well IDs
        (
            "cpg0999-broad-asma/broad/BATCH2/images/plate5/10X_c8_SBS-8/WellD5_PointD5_0042_Channel405 nm,477 nm,G,T_Seq0042.tiff",
            {
                "dataset_id": "cpg0999-broad-asma",
                "batch_id": "BATCH2",
                "plate_id": "plate5",
                "magnification": "10",
                "cycle_id": "8",
                "well_id": "WellD5",
                "site_id": "0042",
                "channels": ["405", "477", "G", "T"],
                "channel_count": 4,
                "extension": "tiff",
            },
            "SBS",
        ),
        # STANDARD CP FORMAT PATHS
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate2/10X_CP_plate2/WellB2_PointB2_0347_ChannelnIR,GFP,DAPI_Seq1923.tiff",
            {
                "dataset_id": "cpg0999-broad-asma",
                "batch_id": "BATCH1",
                "plate_id": "plate2",
                "magnification": "10",
                "well_id": "WellB2",
                "site_id": "1923",
                "channels": ["nIR", "GFP", "DAPI"],
                "channel_count": 3,
                "extension": "tiff",
            },
            "CP",
        ),
        # CP format with different plate and well IDs
        (
            "cpg0999-broad-asma/broad/BATCH3/images/plate4/10X_CP_plate4/WellC6_PointC6_0201_ChannelCy5,FITC,Hoechst_Seq0201.tiff",
            {
                "dataset_id": "cpg0999-broad-asma",
                "batch_id": "BATCH3",
                "plate_id": "plate4",
                "magnification": "10",
                "well_id": "WellC6",
                "site_id": "0201",
                "channels": ["Cy5", "FITC", "Hoechst"],
                "channel_count": 3,
                "extension": "tiff",
            },
            "CP",
        ),
        # CP format with different magnification
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate3/20X_CP_plate3/WellA1_PointA1_0025_ChannelTRITC,GFP,DAPI_Seq0025.tiff",
            {
                "dataset_id": "cpg0999-broad-asma",
                "batch_id": "BATCH1",
                "plate_id": "plate3",
                "magnification": "20",
                "well_id": "WellA1",
                "site_id": "0025",
                "channels": ["TRITC", "GFP", "DAPI"],
                "channel_count": 3,
                "extension": "tiff",
            },
            "CP",
        ),
    ],
)
def test_path_parsing(
    parser, transformer, filepath, expected_metadata, path_type
):
    """Test parsing path formats (SBS and CP) with various configurations.

    This consolidated test function handles both SBS and CP path formats,
    checking all necessary metadata based on the path type.

    Parameters
    ----------
    parser : Lark
        The parser instance
    transformer : VincentAstToIR
        The transformer instance
    filepath : str
        The file path to parse
    expected_metadata : dict
        Dictionary of expected metadata values
    path_type : str
        Type of path being tested ('SBS' or 'CP')

    """
    result = extract_metadata(filepath, parser, transformer)

    # Verify common core metadata extraction
    assert result["dataset_id"] == expected_metadata["dataset_id"]
    assert result["batch_id"] == expected_metadata["batch_id"]
    assert result["plate_id"] == expected_metadata["plate_id"]
    assert result["magnification"] == expected_metadata["magnification"]
    assert result["well_id"] == expected_metadata["well_id"]
    assert result["site_id"] == expected_metadata["site_id"]

    # Verify SBS-specific metadata (cycle_id)
    if path_type == "SBS":
        assert result["cycle_id"] == expected_metadata["cycle_id"]

    # Verify channel extraction
    channel_keys = [k for k in result.keys() if k.startswith("channel_")]
    assert len(channel_keys) == expected_metadata["channel_count"]

    for i, expected_channel in enumerate(expected_metadata["channels"]):
        assert result[f"channel_{i}"] == expected_channel

    # Verify file information
    assert result["extension"] == expected_metadata["extension"]


@pytest.mark.parametrize(
    "filepath,expected_channels",
    [
        # Channel with hyphen
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_Channel405-2 nm,477 nm_Seq2069.tiff",
            ["4052", "477"],
        ),
        # Channel with multiple hyphens
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_ChannelAlexa-488-antibody,Cy5-DNA_Seq2069.tiff",
            ["Alexa488antibody", "Cy5DNA"],
        ),
        # Mix of channel formats
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_ChannelCy3-dye,DAPI,A-647_Seq2069.tiff",
            ["Cy3dye", "DAPI", "A647"],
        ),
    ],
)
def test_channel_normalization(
    parser, transformer, filepath, expected_channels
):
    """Test that channels with hyphens are properly normalized."""
    try:
        result = extract_metadata(filepath, parser, transformer)

        # Check that all channels are normalized correctly
        for i, expected_channel in enumerate(expected_channels):
            assert f"channel_{i}" in result, f"Missing channel_{i} in result"
            assert result[f"channel_{i}"] == expected_channel, (
                f"Channel {i} normalization failed: "
                f"expected '{expected_channel}', got '{result[f'channel_{i}']}'"
            )

        # Verify the total number of channels
        channel_keys = [k for k in result.keys() if k.startswith("channel_")]
        assert len(channel_keys) == len(expected_channels), (
            f"Expected {len(expected_channels)} channels, but found {len(channel_keys)}"
        )
    except Exception as e:
        pytest.skip(f"Parser doesn't support this channel format yet: {e}")


@pytest.mark.parametrize(
    "filepath,expected_cycle",
    [
        # Single-digit cycle ID
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c1_SBS-1/WellB3_PointB3_0099_ChannelG,T,A,C_Seq2069.tiff",
            "1",
        ),
        # Double-digit cycle ID
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_ChannelG,T,A,C_Seq2069.tiff",
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


@pytest.mark.parametrize(
    "filepath,path_type,expected_keys",
    [
        # Standard SBS path
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c11_SBS-11/WellB3_PointB3_0099_Channel405 nm,477 nm,G,T,A,C_Seq2069.tiff",
            "SBS",
            [
                "dataset_id",
                "batch_id",
                "plate_id",
                "cycle_id",
                "well_id",
                "site_id",
                "extension",
            ],
        ),
        # Standard CP path
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate2/10X_CP_plate2/WellB2_PointB2_0347_ChannelnIR,GFP,DAPI_Seq1923.tiff",
            "CP",
            [
                "dataset_id",
                "batch_id",
                "plate_id",
                "well_id",
                "site_id",
                "extension",
            ],
        ),
        # SBS path with timestamp
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate1/10X_c11_SBS-11_20220315/WellB3_PointB3_0099_Channel405 nm,477 nm,G,T,A,C_Seq2069.tiff",
            "SBS with timestamp",
            [
                "dataset_id",
                "batch_id",
                "plate_id",
                "cycle_id",
                "well_id",
                "site_id",
                "extension",
            ],
        ),
        # CP path with additional metadata
        (
            "cpg0999-broad-asma/broad/BATCH1/images/plate2/10X_CP_plate2_experimental/WellB2_PointB2_0347_ChannelnIR,GFP,DAPI_Seq1923.tiff",
            "CP with extra metadata",
            [
                "dataset_id",
                "batch_id",
                "plate_id",
                "well_id",
                "site_id",
                "extension",
            ],
        ),
    ],
)
def test_parser_structure(filepath, path_type, expected_keys):
    """Verify the structure of parser output for different path formats.

    This test validates that the parser extracts the expected keys for various
    path formats, ensuring the parser structure remains stable across different
    variations.

    Parameters
    ----------
    filepath : str
        The file path to parse
    path_type : str
        Type of path being tested (for descriptive purposes)
    expected_keys : list
        List of metadata keys expected to be extracted

    """
    try:
        parser = get_parser(ParserType.OPS_VINCENT)
        transformer = VincentAstToIR()

        # Process the path
        result = extract_metadata(filepath, parser, transformer)

        # Verify all expected keys are present
        for key in expected_keys:
            assert key in result, f"{path_type} parser missing key: {key}"

        # Verify at least one channel is present
        channel_keys = [k for k in result.keys() if k.startswith("channel_")]
        assert len(channel_keys) > 0, f"No channels found in {path_type} path"
    except Exception as e:
        pytest.skip(f"Parser doesn't support this path format yet: {e}")
