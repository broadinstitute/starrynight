"""Generate Index module config."""

from starrynight.modules.schema import Container, TypeCitations

PCP_GEN_INDEX = Container(
    parameters=[],
    display_only=[],
    results=[],
    exec_function=None,
    docker_image=None,
    algorithm_folder_name=None,
    citations=TypeCitations(algorithm=[]),
)
