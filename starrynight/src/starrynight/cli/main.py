"""Starrynight console."""

from pathlib import Path

import click
from cloudpathlib import AnyPath, CloudPath

from starrynight.index import gen_pcp_index
from starrynight.inventory import create_inventory
from starrynight.modules.illum_calc.cppipe import write_illum_calculate_pipeline
from starrynight.modules.illum_calc.load_data import gen_illum_calc_load_data
from starrynight.parsers.common import ParserType, get_parser
from starrynight.parsers.transformer_vincent import VincentAstToIR


@click.command(name="gen")
@click.option("-d", "--dataset", required=True)
@click.option("-o", "--out", required=True)
@click.option("-p", "--prefix", type=click.STRING, default=None)
def gen_inv(dataset: str, out: str, prefix: str | None) -> None:
    """Generate inventory files.

    Parameters
    ----------
    dataset : str
        Dataset path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    prefix : str
        Prefix to add to inventory files.

    """
    if prefix is None:
        prefix = AnyPath(dataset).parent.resolve()  # pyright: ignore
    create_inventory(AnyPath(dataset), AnyPath(out), prefix)  # pyright: ignore


@click.group()
def inventory() -> None:
    """Inventory commands."""
    pass


inventory.add_command(gen_inv)


@click.command(name="gen")
@click.option("-d", "--dataset", default=None)
@click.option("-i", "--inv", default=None)
@click.option("-o", "--out", required=True)
@click.option("-p", "--prefix", type=click.STRING, default=None)
def gen_index(
    dataset: str | None,
    inv: str | Path | CloudPath | None,
    out: str,
    prefix: str | None,
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
    prefix : str
        Prefix to add to inventory files.

    """
    if inv is None:
        assert dataset is not None
        if prefix is None:
            prefix = AnyPath(dataset).parent.resolve()  # pyright: ignore
        create_inventory(AnyPath(dataset), AnyPath(out), prefix)  # pyright: ignore
        inv = AnyPath(out).joinpath("inventory.parquet")
    path_parser = get_parser(ParserType.OPS_VINCENT)
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


@click.command(name="loaddata")
@click.option("-i", "--index", default=None)
@click.option("-o", "--out", required=True)
def gen_illum_loaddata(
    index: str | Path | CloudPath | None,
    out: str,
) -> None:
    """Generate loaddata file.

    Parameters
    ----------
    index : str | None
        Index path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.

    """
    gen_illum_calc_load_data(AnyPath(index), AnyPath(out), None)


@click.command(name="cppipe")
@click.option("-l", "--loaddata", default=None)
@click.option("-o", "--out", required=True)
@click.option("-r", "--run", required=True)
def gen_illum_cppipe(
    loaddata: str | Path | CloudPath | None,
    out: str,
    run: str,
) -> None:
    """Generate cppipe file.

    Parameters
    ----------
    loaddata : str | None
        Loaddata path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    run : str
        Run path. Can be local or a cloud path.

    """
    write_illum_calculate_pipeline(AnyPath(loaddata), AnyPath(out), AnyPath(run))


@click.group()
def illum() -> None:
    """Illum commands."""
    pass


illum.add_command(gen_illum_loaddata)
illum.add_command(gen_illum_cppipe)


@click.group
def main() -> None:
    """Starrynight CLI."""
    pass


main.add_command(inventory)
main.add_command(index)
main.add_command(illum)
