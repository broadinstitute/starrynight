"""Starrynight modules registry."""

from pydantic import BaseModel


class Job(BaseModel):
    name: str
    callable: str
    spec: str


JOB_REGISTRY = {""}


class ModuleSpec(BaseModel):
    name: str
    container_image: str
    inputs: list
    outputs: list


MODULE_REGISTRY = {}
