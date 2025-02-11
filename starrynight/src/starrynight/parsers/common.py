"""Common parser modules."""

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

    """

    @abstractmethod
    def __init__(self, visit_tokens: bool = True) -> None:
        """Initialize base Lark transformer."""
        super().__init__(visit_tokens)
        self.channel_dict: dict[str, list[str]] = {"channel_dict": []}
