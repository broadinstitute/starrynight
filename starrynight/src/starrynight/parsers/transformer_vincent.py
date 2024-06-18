"""Project vincent path parser."""

from starrynight.parsers.common import BaseTransformer


class VincentAstToIR(BaseTransformer):
    def __init__(self) -> None:
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
        return {"well_id": "".join(items)}

    def site_id(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"site_id": "".join(items)}

    def channel(self, items) -> dict:
        channel_len = len(self.channel_dict["channel_dict"])
        self.channel_dict["channel_dict"].append(items[0])
        return {f"channel_{channel_len}": items[0]}

    def filename(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"filename": "".join(items)}

    def extension(self, items) -> dict:
        # assert len(set(items)) == 1
        return {"extension": "".join(items)}

    def string(self, s):
        return "".join(s)

    def stringwithdash(self, s):
        return "".join(s)

    def DIGIT(self, n):
        return "".join(n)

    def number(self, n):
        (n,) = n
        return float(n)

    sep = lambda self, _: None  # noqa
