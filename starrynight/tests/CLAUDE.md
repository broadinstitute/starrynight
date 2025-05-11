# StarryNight Testing Plan

This document provides guidance for systematic testing of the StarryNight codebase.

> **Note to AI assistants**: This is a living document maintained across multiple sessions. The user will regularly update this file with implementation progress.
>
> Key guidelines for AI assistants:
> - Review git commit history at the start of each session to understand recent progress
> - Read this document for overall testing strategy and examples
> - Follow the current session goals set by the human
> - Prefer concrete, focused tests over trying to test everything
> - Use the provided mocking patterns and test examples as starting points
> - Create meaningful commit messages that document what was tested

## Quick Reference

- **Test Commands**:
  - Run all tests: `pytest`
  - Run specific test file: `pytest path/to/test_file.py`
  - Run specific test: `pytest path/to/test_file.py::test_function_name`
  - Run tests with coverage: `pytest --cov=starrynight`
  - Run only unit tests: `pytest -m "not integration"`
  - Run only integration tests: `pytest -m "integration"`

- **Test Organization**: Mirror source code structure (algorithms/, cli/, etc.)
- **Key Principles**: Test independence, mock dependencies, focus on high-value tests
- **Test Pattern**: Follow Arrange-Act-Assert structure

## Pipeline Terminology Clarification

In StarryNight, we deal with two distinct types of pipelines:

1. **CellProfiler Pipelines**: Specialized processing definitions in `.cppipe` or `.json` formats that CellProfiler executes.

2. **StarryNight Pipelines**: High-level workflow definitions built with Pipecraft that connect modules into complete computational workflows.

## Core Testing Strategy

### Layer-based Testing Approach

- **Algorithm tests**: Pure functionality without dependencies
- **CLI tests**: Command interfaces and parameter handling
- **Module tests**: Specifications and compute graph generation
- **StarryNight Pipeline tests**: Workflow composition and structure
- **Utilities tests**: Supporting functionality

### Testing Philosophy

- **Test Independence**: Each test should be isolated from others
- **Mocking Dependencies**: Use mocks for external dependencies
- **Smart Testing**: Focus on behaviors over implementation details
- **Test Pyramid**: Many unit tests, fewer integration tests, minimal end-to-end tests

## Test Organization

Tests should mirror the structure of the source code:

```
starrynight/tests/
├── algorithms/             # Algorithm tests
├── cli/                    # CLI tests
├── modules/                # Module tests
├── parsers/                # Parser tests
├── pipelines/              # Pipeline tests
├── utils/                  # Utility tests
└── fixtures/               # Shared test fixtures
```

Integration tests can use either:
- Separate files with `_integration` suffix
- Pytest markers: `@pytest.mark.integration`

## Test Data Strategy

- Use small, representative data samples (<100KB)
- Store test images in `tests/fixtures/` directory
- Use parameterization for testing variations
- Create focused fixtures for specific test requirements

## Mocking Strategy

### CellProfiler Mocking

Mock pipeline objects with core methods:
- `modules()`, `add_module()`, `dump()`, `json()`

Mock execution to avoid actual processing:
- Patch `run_cellprofiler` function
- Avoid initializing Java VM

### File System Mocking

- Use pytest's `tmp_path` fixture
- Create temporary workspace directories
- Implement cleanup in fixture teardown

## Test Patterns

### Algorithm Test Pattern

```python
def test_algorithm_function_expected_behavior():
    """Test that algorithm_function behaves as expected under normal conditions."""
    # Arrange: Set up test data
    test_input = {...}
    expected_output = {...}

    # Act: Call the function
    result = algorithm_function(test_input)

    # Assert: Verify the output
    assert result == expected_output
```

### CLI Test Pattern

```python
def test_cli_command_parameter_handling(cli_runner):
    """Test that CLI command handles parameters correctly."""
    # Arrange: Prepare command
    command = ["command_name", "--param1", "value1"]

    # Act: Run the command
    result = cli_runner.invoke(main, command)

    # Assert: Check the result
    assert result.exit_code == 0
    assert "Expected output" in result.stdout
```

### Module Test Pattern

```python
def test_module_spec_configuration():
    """Test that module generates correct specification."""
    # Arrange: Set up configurations
    data_config = DataConfig(...)
    experiment = Experiment(...)

    # Act: Create module
    module = TestModule.from_config(data_config, experiment)

    # Assert: Verify specification
    assert module.spec.inputs["input_name"].path == expected_path
    assert module.spec.outputs["output_name"].path == expected_path
```

### Integration Test Pattern

```python
def test_cp_illum_workflow_integration():
    """Test the Cell Painting illumination calculation and application workflow."""
    # Setup test fixture with minimal test data
    test_data = setup_test_data("cp_illum_test")

    # Stage 1: Generate inventory and index
    run_command(["starrynight", "inv", "gen", "-i", test_data.input_dir, "-o", test_data.workspace])

    # Verify index output
    assert os.path.exists(f"{test_data.workspace}/index/index.parquet")
    validate_index_content(f"{test_data.workspace}/index/index.parquet")

    # Stage 2: Continue workflow and verify outputs
    # ...
```

### Parameter Testing Pattern

```python
@pytest.mark.parametrize("input_value,expected", [
    (0, "zero"),            # Lower boundary
    (100, "maximum"),       # Upper boundary
    (50, "middle"),         # Representative value
    (-1, ValueError),       # Error case
])
def test_function_with_different_inputs(input_value, expected):
    """Test function behavior with key input values."""
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            process_value(input_value)
    else:
        result = process_value(input_value)
        assert result == expected
```

## Implementation Plan

### Phase 1: Algorithm Layer Tests
- [ ] Index algorithm unit tests
- [ ] Illumination calculation algorithm unit tests
- [ ] Illumination application algorithm unit tests
- [ ] Segmentation check algorithm unit tests
- [ ] Algorithm integration tests

### Phase 2: CLI Layer Tests
- [ ] Command registration unit tests
- [ ] Parameter validation unit tests
- [ ] Command execution unit tests
- [ ] Error handling unit tests
- [ ] CLI workflow integration tests

### Phase 3: Module Layer Tests
- [ ] Module specification unit tests
- [ ] Module configuration unit tests
- [ ] Compute graph generation unit tests
- [ ] Container configuration unit tests
- [ ] Module integration tests

### Phase 4: StarryNight Pipeline Tests
- [ ] Pipecraft pipeline composition unit tests
- [ ] Pipeline structure validation tests
- [ ] End-to-end workflow integration tests
- [ ] Error handling and recovery tests

### Phase 5: Utilities and Parsers
- [ ] Extend parser unit tests
- [ ] File utility unit tests
- [ ] Data transformation unit tests
- [ ] Configuration validation tests
- [ ] Parser integration tests

## Best Practices

### Writing Effective Tests
- Use descriptive test names: `test_<function_name>_<scenario_description>`
- Follow Arrange-Act-Assert pattern
- Add docstrings to test functions
- Focus on testing complex logic and critical paths
- Test boundary conditions and edge cases

### Anti-patterns to Avoid

1. **Testing Implementation Details**
   - ❌ Testing private methods directly
   - ✅ Test the observable behavior through public interfaces

2. **Brittle Tests**
   - ❌ Asserting exact string matches or data structures
   - ✅ Test for key properties that should remain stable

3. **Test Duplication**
   - ❌ Testing the same functionality at multiple levels
   - ✅ Test each behavior once at the appropriate level

4. **Over-mocking**
   - ❌ Creating complex mock chains that mirror implementation
   - ✅ Mock external dependencies but use real implementations when practical

5. **Exhaustive Input Testing**
   - ❌ Testing every possible input combination
   - ✅ Test boundaries, representative values, and error cases

## Known Challenges
- **CellProfiler Integration**: May require special handling for Java VM initialization
- **Path Handling**: Cloud paths may need special mocking
- **Pipeline Generation**: Focus on key modules rather than exhaustive validation

## Current Session Goals
- [ ] _Add specific goals for this session here_
- [ ] _Example: Implement tests for index generation algorithms_

## Progress Tracking
AI assistants should:
1. Review git commit history at the start of each session to understand what has been implemented
2. Focus on the goals specified for the current session
3. Create meaningful commit messages that document what was tested and implemented
