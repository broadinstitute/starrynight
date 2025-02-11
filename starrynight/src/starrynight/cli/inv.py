"""Generate inventory cli wrapper."""

import click
from cloudpathlib import AnyPath

from starrynight.algorithms.inventory import create_inventory


@click.command(name="gen")
@click.option("-d", "--dataset", required=True)
@click.option("-o", "--out", required=True)
def gen_inv(dataset: str, out: str) -> None:
    """Generate inventory files.

    Parameters
    ----------
    dataset : str
        Dataset path. Can be local or a cloud path.
    out : str
        Output path. Can be local or a cloud path.
    """
    create_inventory(AnyPath(dataset), AnyPath(out))  # pyright: ignore


@click.group()
def inventory() -> None:
    """Inventory commands."""
    pass


inventory.add_command(gen_inv)
