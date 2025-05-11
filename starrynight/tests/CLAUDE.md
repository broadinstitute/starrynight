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
  - Run all tests with UV: `uv run pytest`
  - Run all tests with Python: `pytest`
  - Run specific test file: `pytest path/to/test_file.py`
  - Run specific test: `pytest path/to/test_file.py::test_function_name`
  - Run tests with coverage: `pytest --cov=starrynight`
  - Run tests with verbose output: `pytest -v`

- **Code Quality**:
  - Run pre-commit checks: `pre-commit run --files <path>`
  - Run specific pre-commit hook: `pre-commit run <hook-id> --files <path>`

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
├── integration/            # End-to-end workflow tests
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

### Key Test Fixtures

- **fix_s1_input_dir**: Provides input test data with FIX-S1 structure
  - `fix_s1_input_dir["input_dir"]`: Path to the extracted fix_s1_input directory

- **fix_s1_workspace**: Provides workspace directory structure with expected paths
  - `fix_s1_workspace["workspace_dir"]`: Base workspace directory
  - `fix_s1_workspace["index_dir"]`: Index directory
  - `fix_s1_workspace["inventory_dir"]`: Inventory directory
  - And other paths needed for workflow testing

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
def test_workflow_integration(fix_s1_input_dir, fix_s1_workspace):
    """Test an end-to-end workflow using CLI commands."""
    # Set up test environment
    workspace_dir = fix_s1_workspace["workspace_dir"]
    input_dir = fix_s1_input_dir["input_dir"]

    # Execute CLI command via subprocess
    cmd = [
        "starrynight",
        "command",
        "subcommand",
        "-i", str(input_dir),
        "-o", str(workspace_dir),
        "--param", "value"
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False
    )

    # Verify command succeeded
    assert result.returncode == 0, f"Command failed: {result.stderr}"

    # Verify output files were created
    output_file = workspace_dir / "expected_output.file"
    assert output_file.exists(), "Output file was not created"

    # Verify the content of the output file
    with output_file.open() as f:
        content = json.load(f)
    assert "expected_key" in content, "Output file missing expected data"
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

### Exception Testing Pattern

```python
def test_specific_exceptions():
    """Test that appropriate exceptions are raised for invalid inputs."""
    # Import specific exception types from the module
    from mymodule import ValidationError, ParseError

    # Test with different invalid inputs that should raise specific exceptions
    with pytest.raises(ValidationError):
        process_data({"invalid": "data"})

    with pytest.raises(ParseError):
        parse_content("invalid content")

    # Test with parameters that would cause specific error conditions
    invalid_paths = [
        "invalid/path/format",
        "missing/fields/images/plate1",
    ]

    for path in invalid_paths:
        with pytest.raises(ParseError):
            parser.parse(path)
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
- [x] End-to-end workflow integration tests
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
- Add docstrings to test functions that explain the purpose of the test
- Focus on testing complex logic and critical paths
- Test boundary conditions and edge cases
- Include proper type annotations for fixtures and functions
- Use specific exception types instead of generic `Exception` when testing error cases
- Make assertions as specific and precise as possible
- Avoid print statements in tests

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

## Code Quality and Pre-commit Workflow

StarryNight uses pre-commit hooks to ensure code quality and consistency:

1. **Linting with Ruff**:
   - Checks for Python best practices and code style
   - Enforces modern type annotations (use `dict` instead of `typing.Dict`)
   - Catches common errors and anti-patterns

2. **Formatting with Ruff Format**:
   - Automatically formats code according to project standards
   - Ensures consistent whitespace and line formatting

3. **Pre-commit Workflow**:
   - Always run pre-commit checks before committing: `pre-commit run --files <path>`
   - Fix any issues identified by the hooks
   - Rerun pre-commit checks to verify all issues are resolved

## Commit Workflow

When making commits to the repository:

1. Ensure all tests pass: `uv run pytest <path_to_test>`
2. Run pre-commit checks: `pre-commit run --files <path>`
3. Use semantic commit messages with type prefixes:
   - `test:` for test-related changes
   - `fix:` for bug fixes
   - `feat:` for new features
   - `docs:` for documentation
   - `refactor:` for code refactoring
4. Include a brief description of the change
5. Add bullet points for significant changes

## Session Workflow

AI assistants should:
1. Review git commit history at the start of each session to understand what has been implemented
2. Focus on the goals specified by the user at the beginning of each session
3. Create meaningful commit messages that document what was tested and implemented
4. Run all tests and pre-commit checks before committing changes
5. Run all tests with UV: `uv run pytest`
