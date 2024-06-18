"""Starrynight console."""

from pathlib import Path

import click

from starrynight.inventory import create_inventory_local
from starrynight.index import gen_pcp_index


@click.command(name="local")
@click.option("-d", "--dataset", required=True)
@click.option("-o", "--out", required=True)
@click.option("-p", "--prefix", type=click.STRING)
def inv_local(dataset: str, out: str, prefix: str) -> None:
    if prefix is None:
        prefix = str(Path(dataset).resolve())
    create_inventory_local(Path(dataset), Path(out), prefix)


@click.group()
def inventory() -> None:
    pass


inventory.add_command(inv_local)


@click.command(name="local")
@click.option("-d", "--dataset", required=True)
@click.option("-o", "--out", required=True)
@click.option("-p", "--prefix", type=click.STRING)
def index_local(dataset: str, out: str, prefix: str) -> None:
    if prefix is None:
        prefix = str(Path(dataset).resolve())
    create_inventory_local(Path(dataset), Path(out), prefix)
    gen_pcp_index(Path(out).joinpath("inventory.parquet"), Path(out))


@click.group()
def index() -> None:
    pass


index.add_command(index_local)


@click.group
def main() -> None:
    pass


main.add_command(inventory)
main.add_command(index)
