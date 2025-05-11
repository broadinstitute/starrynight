"""Test Generate index module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cloudpathlib import CloudPath

from starrynight.modules.gen_index import (
    GenIndexModule,
    create_pipe_gen_index,
    create_work_unit_gen_index,
)
from starrynight.modules.schema import Container as SpecContainer
from starrynight.modules.schema import (
    ExecFunction,
    TypeAlgorithmFromCitation,
    TypeCitations,
    TypeEnum,
    TypeInput,
    TypeOutput,
)


@pytest.fixture
def mock_spec():
    """Create a mock specification for testing."""
    return SpecContainer(
        inputs=[
            TypeInput(
                name="inventory_path",
                type=TypeEnum.files,
                description="Path to the inventory.",
                optional=False,
                path="/test/path/inventory.parquet",
            ),
            TypeInput(
                name="parser_path",
                type=TypeEnum.file,
                description="Path to a custom parser grammar file.",
                optional=True,
                path=None,
            ),
        ],
        outputs=[
            TypeOutput(
                name="project_index",
                type=TypeEnum.file,
                description="Generated Index",
                optional=False,
                path="/test/path/output/index.parquet",
            ),
        ],
        parameters=[],
        display_only=[],
        results=[],
        exec_function=ExecFunction(
            name="",
            script="",
            module="",
            cli_command="",
        ),
        docker_image=None,
        algorithm_folder_name=None,
        citations=TypeCitations(
            algorithm=[
                TypeAlgorithmFromCitation(
                    name="Test algorithm",
                    description="Test description",
                )
            ]
        ),
    )


def test_create_work_unit_gen_index():
    """Test creation of work units for Generate Index step."""
    # Test with a simple output directory
    out_dir = Path("/test/output")
    work_units = create_work_unit_gen_index(out_dir)

    # Verify structure of work units
    assert len(work_units) == 1
    assert "inventory" in work_units[0].inputs
    assert "index" in work_units[0].outputs

    # Verify paths are correctly constructed
    assert work_units[0].inputs["inventory"][0].endswith("inventory.parquet")
    assert work_units[0].outputs["index"][0].endswith("index.parquet")


def test_create_pipe_gen_index(mock_spec):
    """Test creation of pipeline for Generate Index step."""
    # Create pipeline with mock spec
    uid = "test_gen_index"
    pipe = create_pipe_gen_index(uid, mock_spec)

    # Verify pipeline structure
    assert pipe is not None
    assert len(pipe.node_list) == 1

    # Verify container configuration
    container = pipe.node_list[0]
    assert container.name == uid
    assert "inventory" in container.input_paths
    assert "index" in container.output_paths

    # Verify command includes expected options
    assert "starrynight" in container.config.cmd
    assert "index" in container.config.cmd
    assert "gen" in container.config.cmd
    assert "-i" in container.config.cmd
    assert "-o" in container.config.cmd


def test_gen_index_module_uid():
    """Test UID generation for GenIndexModule."""
    assert GenIndexModule.uid() == "generate_index"


def test_gen_index_module_spec():
    """Test default spec generation for GenIndexModule."""
    spec = GenIndexModule._spec()

    # Verify spec structure
    assert len(spec.inputs) == 2
    assert len(spec.outputs) == 2
    assert spec.inputs[0].name == "inventory_path"
    assert spec.inputs[1].name == "parser_path"
    assert spec.outputs[0].name == "project_index"
    assert spec.outputs[1].name == "index_notebook"


@patch("starrynight.modules.gen_index.create_pipe_gen_index")
@patch("starrynight.modules.gen_index.create_work_unit_gen_index")
@patch(
    "starrynight.modules.gen_index.GenIndexModule.__init__", return_value=None
)
def test_from_config(mock_init, mock_create_work, mock_create_pipe, mock_spec):
    """Test module creation from config."""
    # Mock the pipeline and work unit creation
    mock_pipe = MagicMock()
    mock_create_pipe.return_value = mock_pipe
    mock_create_work.return_value = [{"mock": "work_unit"}]

    # Create a minimal data config
    class MockDataConfig:
        def __init__(self) -> None:
            self.workspace_path = Path("/test/workspace")
            self.storage_path = Path("/test/storage")

    # Test module creation
    GenIndexModule.from_config(MockDataConfig(), spec=mock_spec)

    # Verify create_pipe_gen_index was called with correct args
    mock_create_pipe.assert_called_once_with(
        uid=GenIndexModule.uid(),
        spec=mock_spec,
    )

    # Verify create_work_unit_gen_index was called
    mock_create_work.assert_called_once()

    # Verify module was initialized correctly
    mock_init.assert_called_once()
    _, kwargs = mock_init.call_args
    assert kwargs["spec"] == mock_spec
    assert kwargs["pipe"] == mock_pipe
    assert kwargs["uow"] == [{"mock": "work_unit"}]
