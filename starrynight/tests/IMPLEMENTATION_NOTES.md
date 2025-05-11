# StarryNight Testing Implementation Notes

This document provides detailed guidance for implementing tests for the StarryNight codebase based on the testing plan in `CLAUDE.md`. It offers concrete strategies, patterns, and examples to follow when developing tests.

## General Implementation Principles

1. **Focus on high-value tests first**: Prioritize testing complex algorithms and critical paths.
2. **Keep tests independent**: Each test should set up its own state and not depend on other tests.
3. **Follow existing patterns**: Look at existing tests like `test_index_algorithm.py` for style guidance.
4. **Use pytest features**: Leverage fixtures, parameterization, and markers effectively.
5. **Mock external dependencies**: Isolate tests from external systems and focus on the unit being tested.

## Layer-by-Layer Implementation Strategy

### Algorithm Layer

The algorithm layer forms the foundation and should be tested thoroughly. Based on the existing `test_index_algorithm.py`, we can see several patterns to follow:

#### Key Testing Strategies for Algorithm Layer:

1. **Class-based testing for models**:
   - Use pytest classes for grouping related model tests (see `TestPCPIndex`)
   - Test both basic properties and computed/derived properties
   - Test edge cases and validation logic

2. **Function-level testing with mocks**:
   - Test individual functions with appropriate mocks
   - Verify both return values and side effects
   - Mock external dependencies (files, libraries, etc.)

3. **Error handling testing**:
   - Test how functions handle invalid inputs or errors
   - Mock error conditions to verify proper handling

#### Example: Testing Pattern for Illumination Calculation

```python
"""Test the illumination calculation algorithm functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from starrynight.algorithms.illum_calc import (
    gen_illum_calc_load_data_by_batch_plate,
    gen_illum_calc_cppipe_by_batch_plate,
)

# Fixtures for common test data
@pytest.fixture
def mock_index_data():
    """Create mock index data for testing."""
    # Create mock index dataframe or data structure
    return {...}

@pytest.fixture
def mock_workspace():
    """Create mock workspace directory."""
    # Setup mock workspace
    return Path("/mock/workspace")

# Test load data generation
@patch("starrynight.algorithms.illum_calc.pl.read_parquet")
@patch("starrynight.algorithms.illum_calc.write_csv")
def test_gen_illum_calc_load_data(mock_write_csv, mock_read_parquet, mock_index_data, mock_workspace):
    """Test illumination calculation load data generation."""
    # Setup mock return values
    mock_read_parquet.return_value = mock_index_data

    # Call function under test
    gen_illum_calc_load_data_by_batch_plate(
        index_path=Path("/test/index.parquet"),
        out_path=mock_workspace,
        path_mask=None
    )

    # Verify correct calls were made
    mock_read_parquet.assert_called_once()
    assert mock_write_csv.call_count > 0

    # Verify output structure or content if needed
    # ...

# Test pipeline generation
@patch("starrynight.algorithms.illum_calc.CellProfilerContext")
def test_gen_illum_calc_cppipe(mock_cp_context, mock_workspace):
    """Test illumination calculation pipeline generation."""
    # Setup mock CellProfiler context
    context_instance = MagicMock()
    mock_cp_context.return_value.__enter__.return_value = context_instance

    # Call function under test
    gen_illum_calc_cppipe_by_batch_plate(
        load_data_path=mock_workspace / "loaddata",
        out_dir=mock_workspace / "cppipe",
        workspace_path=mock_workspace
    )

    # Verify pipeline creation
    # Verify pipeline was properly configured
    # ...
```

#### Implementation Priorities for Algorithm Layer:

1. Build on existing index tests to add more edge cases
2. Develop tests for illumination calculation algorithms
3. Develop tests for illumination application algorithms
4. Add tests for segmentation check algorithms
5. Create tests for CellProfiler pipeline generation algorithms

### CLI Layer

The CLI layer tests should focus on command registration, parameter validation, and proper invocation of underlying algorithms.

#### Key Testing Strategies for CLI Layer:

1. **Command registration tests**:
   - Verify that commands are properly registered with expected names
   - Test command grouping and hierarchy

2. **Parameter validation tests**:
   - Test required parameters are enforced
   - Test parameter type validation
   - Test parameter constraints and defaults

3. **Command execution tests**:
   - Mock underlying algorithm functions
   - Test that CLI commands call the correct algorithms with right parameters
   - Verify exit codes for success/failure scenarios

#### Example: Testing Pattern for CLI Commands

```python
"""Test the CLI command functionality."""

from unittest.mock import patch
import pytest
from click.testing import CliRunner

from starrynight.cli.illum import illum_calc_cmd, illum_apply_cmd
from starrynight.cli.main import main

@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()

def test_illum_calc_command_registration():
    """Test that illumination calculation commands are properly registered."""
    # Inspect the CLI command structure to verify registration
    assert "illum" in [cmd.name for cmd in main.commands.values()]
    assert "calc" in [cmd.name for cmd in main.get_command(None, "illum").commands.values()]

@patch("starrynight.cli.illum.gen_illum_calc_load_data_by_batch_plate")
def test_illum_calc_loaddata_command(mock_gen_loaddata, cli_runner):
    """Test illumination calculation loaddata command execution."""
    # Call the CLI command
    result = cli_runner.invoke(illum_calc_cmd, [
        "loaddata",
        "-i", "/test/index.parquet",
        "-o", "/test/output"
    ])

    # Verify command succeeded
    assert result.exit_code == 0

    # Verify underlying algorithm was called with correct parameters
    mock_gen_loaddata.assert_called_once()
    args, _ = mock_gen_loaddata.call_args
    assert str(args[0]) == "/test/index.parquet"
    assert str(args[1]) == "/test/output"
```

### Module Layer

Module tests should focus on specifications, configurations, and compute graph generation.

#### Key Testing Strategies for Module Layer:

1. **Specification tests**:
   - Verify module specifications are correctly defined
   - Test input/output configurations
   - Test parameter validation

2. **Module creation tests**:
   - Test module creation from configurations
   - Verify proper inheritance and extension points

3. **Compute graph tests**:
   - Test pipeline creation logic
   - Verify node creation and connections
   - Test containerization specifications

#### Implementation Priorities for Module Layer:

1. Create tests for base module structure
2. Implement tests for module specifications
3. Add tests for module configuration from experiments
4. Develop tests for compute graph generation

### StarryNight Pipeline Layer

Pipeline tests should verify proper composition, structure, and integration of modules.

#### Key Testing Strategies for Pipeline Layer:

1. **Composition tests**:
   - Test module combining into pipelines
   - Verify sequential and parallel execution structures

2. **Structure validation tests**:
   - Verify pipeline nodes are correctly connected
   - Test dependency resolution

3. **Integration tests**:
   - Test end-to-end pipelines with mocked executions
   - Verify data flow through pipeline stages

#### Implementation Priorities for Pipeline Layer:

1. Create basic pipeline composition tests
2. Develop tests for sequential and parallel execution patterns
3. Implement tests for module integration in pipelines
4. Add end-to-end pipeline tests

## Mocking Strategies

### CellProfiler Mocking

Effective mocking of CellProfiler is critical for testing. Based on the existing tests, the following approaches work well:

1. **Mock CellProfiler Context**:
```python
@patch("starrynight.algorithms.cp.CellProfilerContext")
def test_function_using_cp(mock_cp_context):
    # Setup context mock
    context_instance = MagicMock()
    mock_cp_context.return_value.__enter__.return_value = context_instance

    # Test code using CellProfiler
    # ...

    # Verify CellProfiler operations
    assert context_instance.add_module.called
    # etc.
```

2. **Mock CellProfiler Pipeline Objects**:
```python
@pytest.fixture
def mock_cp_pipeline():
    """Create a mock CellProfiler pipeline."""
    mock = MagicMock()
    # Setup common methods
    mock.modules.return_value = []
    mock.add_module.side_effect = lambda m: mock.modules().append(m)
    mock.dump.side_effect = lambda f: f.write("Mock pipeline content")
    return mock
```

3. **Avoid Java VM initialization**:
```python
@patch("starrynight.algorithms.cp.cellprofiler_core.utilities.java.start_java")
def test_cp_without_java(mock_start_java):
    # Test code that would normally initialize Java VM
    # ...

    # Verify Java VM wasn't actually started
    assert mock_start_java.called
```

### File System Mocking

File operations should be mocked to avoid real filesystem dependencies:

1. **Mock reading/writing files**:
```python
@patch("starrynight.utils.misc.write_pq")
@patch("starrynight.algorithms.index.pl.read_parquet")
def test_with_file_mocks(mock_read_parquet, mock_write_pq):
    # Configure mock return values
    mock_read_parquet.return_value = mock_df

    # Test code that reads/writes files
    # ...

    # Verify file operations
    mock_read_parquet.assert_called_once()
    mock_write_pq.assert_called_once()
```

2. **Use temporary directories** when actual file operations are needed:
```python
def test_with_temp_dir(tmp_path):
    # tmp_path is a pytest built-in fixture
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    test_file = test_dir / "test_file.txt"
    test_file.write_text("Test content")

    # Test code using these files
    # ...
```

## Test Fixtures Strategy

Based on the existing `test_index_algorithm.py`, we should create fixtures at different levels:

1. **Module-level fixtures** in test files for specific tests
2. **Package-level fixtures** in `conftest.py` files in each test directory
3. **Global fixtures** in the root `conftest.py` for commonly used fixtures

Examples of useful fixtures:

1. **Mock data fixtures**:
```python
@pytest.fixture
def mock_index_data():
    """Create a mock index dataframe for testing."""
    return pl.DataFrame({
        "key": ["test/path/image1.tiff", "test/path/image2.tiff"],
        "dataset_id": ["test_dataset", "test_dataset"],
        "batch_id": ["batch1", "batch1"],
        "plate_id": ["plate1", "plate1"],
        "cycle_id": ["1", "2"],
        "extension": ["tiff", "tiff"]
    })
```

2. **Mock object fixtures**:
```python
@pytest.fixture
def mock_experiment():
    """Create a mock experiment configuration."""
    return MagicMock(
        cp_config=MagicMock(
            nuclear_channel="DAPI",
            cell_channel="CellMask"
        )
    )
```

3. **Path fixtures**:
```python
@pytest.fixture
def test_data_paths():
    """Create standard test data paths."""
    return {
        "index": Path("/test/index.parquet"),
        "output": Path("/test/output"),
        "workspace": Path("/test/workspace")
    }
```

## Challenges and Mitigation Strategies

### Challenge: CellProfiler Dependency

CellProfiler requires Java and has complex dependencies that make testing difficult.

**Mitigation**:
- Mock CellProfiler interface completely
- Test pipeline generation output structure rather than actual CellProfiler operation
- Use separate integration tests for actual CellProfiler execution

### Challenge: Complex Directory Structures

StarryNight relies on specific directory structures.

**Mitigation**:
- Use fixtures to create standardized directory structures
- Mock file system operations when possible
- Use temporary directories for tests that need real file operations

### Challenge: Path Parsing Complexity

Path parsing is complex and may vary across systems.

**Mitigation**:
- Use consistent test paths that work across platforms
- Mock path parsing functions when testing higher-level functionality
- Create dedicated tests for path parsers with a wide range of test cases

## Next Steps for Implementation

1. **Start with algorithm layer tests**:
   - Complete index algorithm tests
   - Implement illumination calculation algorithm tests
   - Add illumination application algorithm tests
   - Develop segmentation check algorithm tests

2. **Create core test fixtures**:
   - Develop standardized mock data
   - Create mock path structures
   - Implement mock CellProfiler interfaces

3. **Move to CLI layer tests**:
   - Test command registration
   - Implement parameter validation tests
   - Add command execution tests

4. **Continue with module and pipeline tests**:
   - Test module specifications
   - Test pipeline composition
   - Implement integration tests

## Conclusion

This implementation guide provides detailed strategies for testing the StarryNight codebase. By following these patterns and priorities, we can develop a comprehensive test suite that ensures the reliability and maintainability of the system.

Remember to review and update these implementation notes as the testing progresses and new patterns or challenges emerge.
