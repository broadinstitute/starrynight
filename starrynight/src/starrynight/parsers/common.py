"""Common parser modules."""

from abc import abstractmethod
from enum import Enum
from pathlib import Path

from lark import Lark, Transformer


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


def get_parser(parser_type: ParserType) -> Lark:
    """Get parser.

    Parameters
    ----------
    parser_type : ParserType
        Parser type.

    Returns
    -------
    Lark
        Parser instance.

    """
    return Lark.open(parser_path_map[parser_type].resolve().__str__(), parser="lalr")


class BaseTransformer(Transformer):
    """Base Lark transformer.

    Attribures
    ----------
    visit_tokens : bool
        Is token already visited.

    """

    @abstractmethod
    def __init__(self, visit_tokens: bool = True) -> None:
        """Initialize base Lark transformer."""
        super().__init__(visit_tokens)
        self.channel_dict: dict[str, list[str]] = {"channel_dict": []}
