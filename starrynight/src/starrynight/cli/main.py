"""Starrynight console."""

import click

from starrynight.cli.align import align
from starrynight.cli.analysis import analysis
from starrynight.cli.cp import invoke_cp
from starrynight.cli.exp import exp
from starrynight.cli.illum import illum
from starrynight.cli.index import index
from starrynight.cli.inv import inventory
from starrynight.cli.preprocess import preprocess
from starrynight.cli.presegcheck import presegcheck
from starrynight.cli.segcheck import segcheck
from starrynight.cli.stitchcrop import stitchcrop


@click.group
def main() -> None:
    """Starrynight CLI."""
    pass


main.add_command(inventory)
main.add_command(index)
main.add_command(illum)
main.add_command(invoke_cp)
main.add_command(presegcheck)
main.add_command(segcheck)
main.add_command(align)
main.add_command(preprocess)
main.add_command(analysis)
main.add_command(exp)
main.add_command(stitchcrop)
