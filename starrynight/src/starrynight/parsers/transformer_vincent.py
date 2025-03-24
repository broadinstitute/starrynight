"""Project vincent path parser."""

# ruff: noqa: ANN001, D102, N802

from pathlib import Path

from starrynight.parsers.common import BaseTransformer


class VincentAstToIR(BaseTransformer):
    """Transformer for converting Vincent AST to IR.

    This class takes a parsed AST from Vincent and converts it into an
    intermediate representation (IR) that can be used by the rest of the
    pipeline.
    """

    def __init__(self, channel_map_path: Path = None) -> None:
        """Initialize the transformer.

        Initializes the channel dictionary, which is used to keep track of
        channels as they are encountered in the input data.

        Parameters
        ----------
        channel_map_path : Path, optional
            Path to a channel mapping configuration file. If not provided,
            will attempt to use the default config path.

        """
        # If no config path is provided, use the default location
        if channel_map_path is None:
            # Try to locate the default config file
            default_config_path = (
                Path(__file__).parent.parent / "configs" / "channel_mapping.json"
            )
            if default_config_path.exists():
                channel_map_path = default_config_path

        super().__init__(visit_tokens=True, channel_map_path=channel_map_path)

        # If no config was loaded, set up some basic defaults
        if not self.channel_mapping:
            self.channel_mapping = {
                # Common DNA stains
                "DAPI": "DNA",
                "Hoechst": "DNA",
                "405 nm": "DNA",
                # Common cell membrane/cytoskeleton stains
                "Phalloidin": "Cell",
                "PhalloAF750": "Cell",
                "CellMask": "Cell",
                # Other common stains with functional names
                "ZO1": "Junction",
                "ZO1-AF488": "Junction",
                "GFP": "GFP",
                "nIR": "nIR",
                # SBS channels
                "A": "SBS_A",
                "C": "SBS_C",
                "G": "SBS_G",
                "T": "SBS_T",
            }

        self.channel_dict: dict[str, list[str]] = {"channel_dict": []}

        # Reverse mapping to store the raw channel name for each functional name
        self.raw_channel_mapping = {}

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

    def plate_well_site_id(self, items) -> dict:
        out_dict = {}
        for item in items:
            out_dict.update(item)
        return out_dict

    def channel(self, items) -> dict:
        channel_len = len(self.channel_dict["channel_dict"])
        # important for cellprofiler ("-" in channel name is not allowed)
        raw_channel = items[0].replace("-", "")

        # Map the raw channel name to a functional name if it exists in the mapping
        functional_name = self.channel_mapping.get(raw_channel, raw_channel)

        # Store the raw channel name for each functional name for reference
        self.raw_channel_mapping[functional_name] = raw_channel

        # Add the functional name to the channel_dict
        self.channel_dict["channel_dict"].append(functional_name)

        # Return the channel with both the raw and functional names
        return {
            f"channel_{channel_len}": functional_name,
            f"raw_channel_{channel_len}": raw_channel,
        }

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
