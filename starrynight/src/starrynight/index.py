"""Inventory -> [path parser] -> Index."""

from pathlib import Path
from typing import Annotated

import polars as pl
from lark import Lark
from pydantic import BaseModel, Field, BeforeValidator
from tqdm import tqdm


from starrynight.inventory import FileInventory
from starrynight.parsers.common import BaseTransformer
from starrynight.validate import write_pq
from starrynight.parsers.transformer_vincent import VincentAstToIR


IMG_FORMATS = ["tiff", "tif", "ndff", "jpeg", "png"]


class PCPIndex(BaseModel):
    key: str
    local_prefix: str | None = None
    s3_prefix: str | None = None
    dataset_id: str | None = None
    batch_id: str | None = None
    plate_id: str | None = None
    cycle_id: str | None = None
    magnification: str | None = None
    well_id: str | None = None
    site_id: str | None = None
    channel_dict: list[str] | None = None
    filename: str | None = None
    extension: str | None = None
    is_sbs_image: Annotated[
        bool,
        BeforeValidator(
            lambda v, info: v in IMG_FORMATS
            and bool((info.data["cycle_id"] is not None))
        ),
    ] = Field(validation_alias="extension", default=False)
    is_image: Annotated[bool, BeforeValidator(lambda v: v in IMG_FORMATS)] = Field(
        validation_alias="extension", default=False
    )
    # WARN: This validation only runs when extension key is passed to the Model.
    # So set default to True, as directories won't have extension in their parse tree
    is_dir: Annotated[bool, BeforeValidator(lambda v: not bool(v))] = Field(
        validation_alias="extension", default=True
    )


def ast_to_pcp_index(
    parsed_inv: FileInventory, path_parser: Lark, ast_transformer: type[BaseTransformer]
) -> PCPIndex:
    ast = path_parser.parse(parsed_inv.key)
    transformer = ast_transformer()
    ir = transformer.transform(ast)
    pcp_index_dict = {
        k: v
        for item in ir["start"]
        for k, v in (item.items() if isinstance(item, dict) else {})
    }
    # Check if parser is correctly parsing filename and extensions
    if pcp_index_dict.get("filename", False):
        assert parsed_inv.filename == pcp_index_dict["filename"]
    if pcp_index_dict.get("extension", False):
        assert parsed_inv.extension == pcp_index_dict["extension"]

    return PCPIndex(
        **pcp_index_dict,
        filename=parsed_inv.filename,
        key=parsed_inv.key,
        channel_dict=transformer.channel_dict["channel_dict"],
    )


def gen_pcp_index(
    inv_path: Path,
    out_path: Path,
    path_parser: Lark,
    ast_tansformer: type[BaseTransformer],
) -> None:
    df = pl.read_parquet(inv_path)
    parsed_index = {key: [] for key in PCPIndex.model_construct().model_fields.keys()}
    for batch in tqdm(df.iter_slices()):
        row_dicts = batch.to_dicts()
        for row in row_dicts:
            try:
                pdict = ast_to_pcp_index(
                    FileInventory(**row), path_parser, ast_tansformer
                ).model_dump()
                for k, v in pdict.items():
                    parsed_index[k].append(v)

            except Exception as e:
                raise e
    write_pq(parsed_index, PCPIndex, out_path)


if __name__ == "__main__":
    path_parser = Lark.open("path_parser.lark", rel_to=__file__, parser="lalr")
    gen_pcp_index(
        Path(__file__).parents[1].joinpath("inventory.parquet"),
        Path(__file__).parent.joinpath("asma_index.parquet"),
        path_parser,
        VincentAstToIR,
    )
