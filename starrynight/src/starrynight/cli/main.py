"""Starrynight console."""

import click

from starrynight.cli.cp import invoke_cp
from starrynight.cli.illum import illum
from starrynight.cli.index import index
from starrynight.cli.inv import inventory


@click.group
def main() -> None:
    """Starrynight CLI."""
    pass


main.add_command(inventory)
main.add_command(index)
main.add_command(illum)
main.add_command(invoke_cp)
