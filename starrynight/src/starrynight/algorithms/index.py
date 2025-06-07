"""Inventory -> [path parser] -> Index."""

from pathlib import Path
from typing import Annotated

import polars as pl
from cloudpathlib import CloudPath
from lark import Lark
from pydantic import BaseModel, BeforeValidator, Field
from tqdm import tqdm

from starrynight.algorithms.inventory import FileInventory
from starrynight.parsers.common import BaseTransformer
from starrynight.utils.misc import write_pq

IMG_FORMATS = ["tiff", "tif", "ndff", "jpeg", "png"]


class PCPIndex(BaseModel):
    """Pooled CellPainting Index.

    Attributes
    ----------
    key : File location.
    prefix : Default prefix for the file. Can be a Local or CloudPath
    dataset_id : Dataset ID.
    batch_id : File batch ID.
    plate_id : File plate ID.
    cycle_id : File cycle ID.
    magnification : File magnification. If image file.
    well_id : File well ID.
    site_id : File site ID.
    channel_dict : File channel dictionary. If image file.
    filename : File name.
    extension : File extension.
    is_sbs_image : Is this file an SBS image?
    is_image : Is this file an image?
    is_dir : Is this file a directory?

    """

    key: str
    prefix: str | None = None
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
            and bool(info.data["cycle_id"] is not None)
        ),
    ] = Field(validation_alias="extension", default=False)
    is_image: Annotated[bool, BeforeValidator(lambda v: v in IMG_FORMATS)] = (
        Field(validation_alias="extension", default=False)
    )
    # WARN: This validation only runs when extension key is passed to the Model.
    # So set default to True, as directories won't have extension in their parse tree
    is_dir: Annotated[bool, BeforeValidator(lambda v: not bool(v))] = Field(
        validation_alias="extension", default=True
    )


def ast_to_pcp_index(
    parsed_inv: FileInventory,
    path_parser: Lark,
    ast_transformer: type[BaseTransformer],
) -> PCPIndex:
    """Create PCPIndex from AST.

    Parameters
    ----------
    parsed_inv : FileInventory
        Parsed inventory.
    path_parser : Lark
        Path parser.
    ast_transformer : type[BaseTransformer]
        AST transformer.

    Returns
    -------
    PCPIndex
        PCPIndex instance.

    """
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
        assert (
            parsed_inv.extension.replace(".", "") == pcp_index_dict["extension"]
        )

    return PCPIndex(
        **pcp_index_dict,
        filename=parsed_inv.filename,
        key=parsed_inv.key,
        prefix=parsed_inv.prefix,
        channel_dict=transformer.channel_dict["channel_dict"],
    )


def gen_pcp_index(
    inv_path: Path | CloudPath,
    out_path: Path | CloudPath,
    path_parser: Lark,
    ast_tansformer: type[BaseTransformer],
) -> None:
    """Create PCPIndex from inventory.

    Parameters
    ----------
    inv_path : Path | CloudPath
        Path to inventory. Can be local or a cloud path.
    out_path : Path | CloudPath
        Path to save generated index. Can be local or a cloud path.
    path_parser : Lark
        Path parser.
    ast_tansformer : type[BaseTransformer]
        AST transformer.

    """
    df = pl.read_parquet(inv_path.resolve().__str__())
    parsed_index = {key: [] for key in PCPIndex.model_fields.keys()}
    for batch in tqdm(
        df.iter_slices(), total=len(df) // 10000, desc="Generating Index"
    ):
        row_dicts = batch.to_dicts()
        for row in row_dicts:
            try:
                pdict = ast_to_pcp_index(
                    FileInventory(**row), path_parser, ast_tansformer
                ).model_dump()
                for k, v in pdict.items():
                    parsed_index[k].append(v)

            except Exception as e:
                print(f"Unable to parse: {row} because of {e}")
    write_pq(parsed_index, PCPIndex, out_path.joinpath("index.parquet"))
