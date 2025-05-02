"""Experiment CLI."""

import json

import click
from cloudpathlib import AnyPath

from starrynight.experiments.registry import EXPERIMENT_REGISTRY


@click.command()
@click.option("-i", "--index", required=True)
@click.option("-e", "--exp", required=True)
@click.option("-c", "--config", required=True)
@click.option("-o", "--out", required=True)
def new(index: str, exp: str, config: str, out: str) -> None:
    """Create a new experiment."""
    exp_model = EXPERIMENT_REGISTRY.get(exp, None)
    if exp_model is None:
        raise ValueError(f"Unknow experiment: {exp}")

    init_config = json.loads(AnyPath(config).read_text())
    exp_config = exp_model.from_index(AnyPath(index), init_config)
    with AnyPath(out).joinpath("experiment.json").open("w") as f:
        f.write(exp_config.model_dump_json())


@click.command()
@click.option("-e", "--exp", required=True)
@click.option("-o", "--out", required=True)
def init(exp: str, out: str) -> None:
    """Create a new experiments init config."""
    exp_model = EXPERIMENT_REGISTRY.get(exp, None)
    if exp_model is None:
        raise ValueError(f"Unknow experiment: {exp}")

    init_config = exp_model.get_init_config()
    with AnyPath(out).joinpath("experiment_init.json").open("w") as f:
        f.write(init_config.model_dump_json())


@click.group()
def exp() -> None:
    """Experiments."""
    pass


exp.add_command(init)
exp.add_command(new)
