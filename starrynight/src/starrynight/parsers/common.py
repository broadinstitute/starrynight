"""Common parser modules."""

import json
import logging
from abc import abstractmethod
from enum import Enum
from pathlib import Path

from cloudpathlib.cloudpath import CloudPathT
from lark import Lark, Transformer

logging.basicConfig(level=logging.INFO)


class ParserType(Enum):
    """Parser types.

    Attributes
    ----------
    OPS_VINCENT : vincent ops parser.

    """

    OPS_VINCENT = "ops_vincent"


parser_path_map = {
    ParserType.OPS_VINCENT: Path(__file__).parent / "path_parser_vincent.lark",
}


def get_parser(
    parser_type: ParserType, parser_path: Path | CloudPathT | None = None
) -> Lark:
    """Get parser.

    Parameters
    ----------
    parser_type : ParserType
        Parser type.
    parser_path : ParserType
        Path to a custom parser.

    Returns
    -------
    Lark
        Parser instance.

    """
    if parser_path is None:
        parser_path = parser_path_map[parser_type]

    return Lark.open(
        parser_path.resolve().__str__(),
        parser="lalr",
        # strict=True,
        # debug=True,
    )


class BaseTransformer(Transformer):
    """Base Lark transformer.

    Attributes
    ----------
    visit_tokens : bool
        Is token already visited.
    channel_dict : dict
        Dictionary to store channel information.
    channel_mapping : dict
        Dictionary mapping raw channel names to functional names.
    raw_channel_mapping : dict
        Dictionary mapping functional names back to raw channel names.

    """

    @abstractmethod
    def __init__(
        self, visit_tokens: bool = True, channel_map_path: Path | None = None
    ) -> None:
        """Initialize base Lark transformer.

        Parameters
        ----------
        visit_tokens : bool
            Is token already visited.
        channel_map_path : Optional[Path]
            Path to a channel mapping configuration file.

        """
        super().__init__(visit_tokens)
        self.channel_dict: dict[str, list[str]] = {"channel_dict": []}
        self.channel_mapping: dict[str, str] = {}  # raw channel -> functional name
        self.raw_channel_mapping: dict[str, str] = {}  # functional name -> raw channel

        # Load channel mapping from config file if provided
        if channel_map_path is not None and channel_map_path.exists():
            with open(channel_map_path) as f:
                mapping_config = json.load(f)
                self.channel_mapping = mapping_config.get("channel_mapping", {})
