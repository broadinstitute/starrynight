"""Generate index cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.index import gen_pcp_index
from starrynight.parsers.common import ParserType, get_parser
from starrynight.parsers.transformer_vincent import VincentAstToIR


@click.command(name="gen")
@click.option("-i", "--inv", required=True)
@click.option("-o", "--out", required=True)
@click.option("-p", "--parser", default=None)
def gen_index(
    inv: str,
    out: str,
    parser: str | None,
) -> None:
    """Generate index files.

    Parameters
    ----------
    dataset : str
        Dataset path. Can be local or a cloud path.
    inv : str | None
        Inventory path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    parser : str
        Custom parser to parse the file paths.

    """
    if parser is not None:
        parser = AnyPath(parser)
    path_parser = get_parser(ParserType.OPS_VINCENT, parser)
    gen_pcp_index(
        AnyPath(inv),
        AnyPath(out),
        path_parser,
        VincentAstToIR,
    )


@click.group()
def index() -> None:
    """Index commands."""
    pass


index.add_command(gen_index)
