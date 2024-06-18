"""Common parser modules."""

from abc import abstractmethod

from lark import Transformer


class BaseTransformer(Transformer):
    @abstractmethod
    def __init__(self, visit_tokens: bool = True) -> None:
        super().__init__(visit_tokens)
        self.channel_dict: dict[str, list[str]] = {"channel_dict": []}
