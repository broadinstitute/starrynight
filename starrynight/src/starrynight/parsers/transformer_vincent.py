"""Project vincent path parser."""

# ruff: noqa: ANN001, D102, N802

from starrynight.parsers.common import BaseTransformer


class VincentAstToIR(BaseTransformer):
    """Transformer for converting Vincent AST to IR.

    This class takes a parsed AST from Vincent and converts it into an
    intermediate representation (IR) that can be used by the rest of the
    pipeline.
    """

    def __init__(self) -> None:
        """Initialize the transformer.

        Initializes the channel dictionary, which is used to keep track of
        channels as they are encountered in the input data.
        """
        super().__init__()
        self.channel_dict: dict[str, list[str]] = {"channel_dict": []}

    def start(self, items) -> dict:
        return {"start": items}

    def dataset_id(self, items) -> dict:
        assert len(set(items)) == 1
        return {"dataset_id": items[0]}

    def batch_id(self, items) -> dict:
        assert len(set(items)) == 1
        return {"batch_id": items[0]}

    def plate_id(self, items) -> dict:
        assert len(set(items)) == 1
        return {"plate_id": items[0]}

    def cycle_id(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"cycle_id": "".join(items)}

    def magnification(self, items) -> dict:
        return {"magnification": "".join(items)}

    def well_id(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"well_id": "Well" + "".join(items)}

    def site_id(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"site_id": "".join(items)}

    def plate_well_site_id(self, items) -> dict:
        out_dict = {}
        for item in items:
            out_dict.update(item)
        return out_dict

    def channel(self, items) -> dict:
        channel_len = len(self.channel_dict["channel_dict"])
        # important for cellprofiler ("-" in channel name is not allowed)
        normalized_channel = items[0].replace("-", "")
        self.channel_dict["channel_dict"].append(normalized_channel)
        return {f"channel_{channel_len}": normalized_channel}

    def filename(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"filename": "".join(items)}

    def extension(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"extension": "".join(items)}

    def string(self, s) -> str:
        return "".join(s)

    def stringwithdash(self, s) -> str:
        return "-".join(s)

    def stringwithdots(self, s) -> str:
        return s[-1]

    def stringwithdashcommaspace(self, s) -> str:
        return "-".join(s)

    def DIGIT(self, n) -> str:
        return "".join(n)

    def number(self, n) -> float:
        (n,) = n
        return float(n)

    sep = lambda self, _: None  # noqa
