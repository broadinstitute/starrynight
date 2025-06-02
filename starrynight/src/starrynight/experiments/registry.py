"""Starrynight experiments registry."""
# pyright: reportAssignmentType=false

from starrynight.experiments.common import Experiment
from starrynight.experiments.pcp_generic import PCPGeneric

EXPERIMENT_REGISTRY: dict[str, Experiment] = {
    "Pooled CellPainting [Generic]": PCPGeneric,
    "Pooled CellPainting [Stitchcrop]": PCPGeneric,
}
