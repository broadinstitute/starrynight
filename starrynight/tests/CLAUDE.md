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

## Pipeline Terminology Clarification

In StarryNight, we deal with two distinct types of pipelines:

1. **CellProfiler Pipelines**: Specialized processing definitions in `.cppipe` or `.json` formats that CellProfiler executes. These define image processing operations within the CellProfiler tool.

2. **StarryNight Pipelines**: High-level workflow definitions built with Pipecraft that connect modules into complete computational workflows. These define the overall structure of a processing chain including module coordination, parallel execution, and containerization.

This testing plan addresses both pipeline types but distinguishes them clearly when discussing test implementations.

## Testing Philosophy

1. **Layer-based Testing**: Follow the architecture's layered approach for testing:
   - Algorithm tests: Focus on pure functionality without dependencies
   - CLI tests: Test command interfaces and parameter handling
   - Module tests: Validate specifications and compute graph generation
   - StarryNight Pipeline tests: Ensure proper workflow composition and structure
   - Utilities tests: Verify supporting functionality

2. **Test Independence**: Each test should be isolated and not depend on the state of other tests.

3. **Mocking Dependencies**: Use mocks extensively for external dependencies (CellProfiler, Python libraries, file operations).

4. **Test Coverage**: Strive for comprehensive coverage across all layers.

5. **Test Types**:
   - Unit tests: Test individual functions and classes
   - Integration tests: Test interaction between components
   - Functional tests: Test complete workflows

6. **Smart Testing, Not Overtesting**: Focus on value and maintainability:
   - Test behaviors and outcomes, not implementation details
   - Prioritize complex algorithms and critical paths
   - Avoid redundant tests across different test levels
   - Write fewer, more valuable tests rather than many brittle ones

## Test Organization

Tests should be organized to mirror the structure of the source code:

```
starrynight/tests/
├── algorithms/         # Test algorithm functionality
├── cli/                # Test CLI commands
├── experiments/        # Test experiment configurations
├── modules/            # Test module specifications and compute graphs
├── parsers/            # Test path parsers
├── pipelines/          # Test StarryNight pipeline composition with Pipecraft
└── utils/              # Test utility functions
```

## Test Data Strategy

### Test Fixtures
- Use `conftest.py` for shared fixtures across test modules
- Create layer-specific fixtures in subdirectories (e.g., `algorithms/conftest.py`)
- Keep fixtures focused on specific test requirements
- Use inheritance for fixture hierarchies when appropriate

### Minimal Test Data
- Create small, representative data samples rather than using real datasets
- Store small test images (< 100 KB) in `tests/fixtures/` directory
- For larger files, use factories to generate test data programmatically
- Use parameterization to test variations without duplicating fixture code

### Sample File Structure
```
tests/
├── fixtures/
│   ├── images/         # Small test images
│   ├── cppipe/         # Sample CellProfiler pipelines
│   └── metadata/       # Test metadata files
├── conftest.py         # Shared fixtures
└── algorithms/
    ├── conftest.py     # Algorithm-specific fixtures
    └── test_*.py       # Test modules
```

## Mocking Strategy

### General Approach
- Use `unittest.mock` for Python standard library
- Use `pytest-mock` for pytest integration
- Create mock classes for external dependencies
- Use fixture factories for complex mock objects

### CellProfiler Mocking
When mocking CellProfiler components:

- Create mock pipeline objects that expose core CellProfiler methods:
  - `modules()` - Returns list of modules
  - `add_module()` - Adds a module to the pipeline
  - `dump()` - Writes pipeline to file
  - `json()` - Converts pipeline to JSON format

- Mock CellProfiler execution to avoid actual processing:
  - Patch `run_cellprofiler` function
  - Return status information and mock output paths
  - Avoid initializing actual Java VM

### File System Mocking
For file system operations:

- Use pytest's `tmp_path` fixture when possible
- Create temporary workspace directories with appropriate structure
- Use `.mkdir()` to create temporary directory hierarchies
- Implement cleanup in fixture teardown
- Create parameterized fixture factories that generate common directory structures

## Core Testing Areas

1. **Algorithm Layer Components**:
   - Index generation - Foundation for other components
   - Illumination calculation/application - Critical path feature
   - Image processing - Core functionality
   - CellProfiler pipeline generation - Key integration point

2. **Utility Components**:
   - Path parsing - Used across multiple components
   - File operations - Standard functionality
   - Data structure handling - Used across multiple components

3. **StarryNight Pipeline Components**:
   - Module creation and configuration - Integration foundation
   - Pipecraft workflow structure - Architecture verification
   - Sequential and parallel execution patterns - Performance aspect

## Implementation Plan

### Phase 1: Algorithm Layer Tests

- [ ] Index algorithm tests (builds on existing tests)
- [ ] Illumination calculation algorithm tests
- [ ] Illumination application algorithm tests
- [ ] Segmentation check algorithm tests
- [ ] CellProfiler pipeline generation algorithm tests

### Phase 2: CLI Layer Tests

- [ ] Command registration tests
- [ ] Parameter validation tests
- [ ] Command execution tests
- [ ] Error handling tests

### Phase 3: Module Layer Tests

- [ ] Module specification tests
- [ ] Module configuration tests
- [ ] Compute graph generation tests
- [ ] Container configuration tests

### Phase 4: StarryNight Pipeline and Integration Tests

- [ ] Pipecraft pipeline composition tests
- [ ] Module integration tests
- [ ] End-to-end workflow tests
- [ ] Error handling and recovery tests

### Phase 5: Utilities and Parsers

- [ ] Extend parser tests
- [ ] File utility tests
- [ ] Data transformation tests
- [ ] Configuration validation tests

## Integration Testing Approach

Integration tests verify that components work correctly together across boundaries. For StarryNight workflows, this means testing the connections between different processing stages and ensuring data flows correctly through the pipeline.

### Workflow Integration Testing

For testing complete workflows like those in `/docs/user/example-pipeline-cli.md`:

1. **Create Minimal Test Fixtures**:
   - Generate small, representative test datasets (10-20 images maximum)
   - Create simplified experiment configurations focused on testing
   - Isolate test data in dedicated test directories

2. **Define Checkpoint Verification**:
   - Identify critical outputs at each workflow stage
   - Create validation functions that verify expected file structure and content
   - Define success criteria for each integration point

3. **Test with Staged Execution**:
   - Test pipeline stages sequentially with dependencies
   - Capture and validate outputs after each stage
   - Verify that output from one stage correctly feeds into the next

4. **Stage Isolation Testing**:
   - Test ability to restart workflow from intermediate points
   - Verify correct handling of existing/missing intermediate files
   - Test with pre-generated intermediate files

### Example Integration Test for CLI Workflow

```python
def test_cp_illum_workflow_integration():
    """Test the Cell Painting illumination calculation and application workflow."""
    # Setup test fixture with minimal test data
    test_data = setup_test_data("cp_illum_test")

    # Stage 1: Generate inventory and index
    run_command(["starrynight", "inv", "gen", "-i", test_data.input_dir, "-o", test_data.workspace])
    run_command(["starrynight", "index", "gen", "-i", f"{test_data.workspace}/inventory.parquet",
                 "-o", f"{test_data.workspace}/index"])

    # Verify index output
    assert os.path.exists(f"{test_data.workspace}/index/index.parquet")
    validate_index_content(f"{test_data.workspace}/index/index.parquet")

    # Stage 2: Illumination calculation
    load_data_dir = f"{test_data.workspace}/cellprofiler/loaddata/cp/illum/illum_calc"
    os.makedirs(load_data_dir, exist_ok=True)

    run_command(["starrynight", "illum", "calc", "loaddata",
                 "-i", f"{test_data.workspace}/index/index.parquet",
                 "-o", load_data_dir,
                 "--exp_config", f"{test_data.workspace}/experiment.json"])

    # Verify LoadData files
    assert os.path.exists(f"{load_data_dir}/batch1_plate1.csv")
    validate_loaddata_files(load_data_dir)

    # Continue with pipeline generation and execution...
    # Verify intermediate output files...

    # Stage 3: Illumination application
    # Use output from stage 2 as input to stage 3...

    # Final verification
    validate_workflow_output(f"{test_data.workspace}/illum/cp/illum_apply")
```

### Integration Test Folder Structure

Integration tests should be organized in a dedicated folder structure that separates them from unit tests:

```
starrynight/tests/
├── integration/                      # All integration tests
│   ├── conftest.py                   # Shared fixtures for integration tests
│   ├── fixtures/                     # Test data for integration tests
│   │   ├── minimal_dataset/          # Minimal dataset for basic workflow tests
│   │   │   ├── images/               # Small set of test images
│   │   │   ├── metadata/             # Simplified metadata files
│   │   │   └── expected_outputs/     # Expected output files for validation
│   │   └── edge_cases/               # Test data for edge cases
│   ├── workflows/                    # Tests for complete workflows
│   │   ├── test_cp_workflow.py       # Cell Painting workflow integration tests
│   │   ├── test_sbs_workflow.py      # SBS workflow integration tests
│   │   └── test_complete_workflow.py # Complete workflow integration tests
│   ├── cli/                          # CLI integration tests
│   │   └── test_cli_pipeline.py      # Tests for CLI pipeline commands
│   └── utils/                        # Utilities for integration tests
│       ├── command_runner.py         # Utilities for running CLI commands
│       ├── output_validators.py      # Functions to validate workflow outputs
│       └── test_data_generators.py   # Functions to generate test data
```

For workflow tests that follow the example-pipeline-cli.md pattern:

1. Create a dedicated test file in `integration/workflows/`
2. Use fixtures from `integration/fixtures/minimal_dataset/`
3. Define validation functions in `integration/utils/output_validators.py`
4. Create helper functions in `integration/utils/command_runner.py`

### Key Integration Testing Principles

1. **Test Data Preparation**:
   - Create minimal datasets that exercise all code paths
   - Include edge cases in test data (missing channels, unusual naming)
   - Parameterize tests to run with different data configurations

2. **Workflow Verification**:
   - Verify existence of expected output files
   - Check file formats and basic content
   - Validate metadata consistency between stages
   - Compare key values against expected outcomes

3. **Resource Management**:
   - Use temporary directories to isolate test runs
   - Clean up test resources after execution
   - Mock external services or use containerized versions for consistency

4. **Test Isolation**:
   - Each integration test should run independently
   - Avoid tests that change global state
   - Reset environment between test runs

## Guidelines for Writing Tests

1. **Test Names**:
   - Use descriptive names that indicate what's being tested
   - Format: `test_<function_name>_<scenario_description>`

2. **Test Structure**:
   - Arrange: Set up test data and conditions
   - Act: Call the function/method being tested
   - Assert: Verify the expected outcomes

3. **Documentation**:
   - Add docstrings to test functions explaining the test purpose
   - Include expected behavior description

4. **Fixtures**:
   - Use parameterized fixtures for testing multiple cases
   - Keep fixtures focused on specific test requirements

5. **Mocking**:
   - Mock external dependencies and I/O operations
   - Use context managers for temporary resources

6. **Value vs. Maintenance Balance**:
   - Focus on testing complex logic and error-prone code
   - Test boundary conditions and edge cases
   - Limit tests for simple pass-through or delegation methods
   - Test public interfaces rather than private implementation details

7. **Test Pyramids**:
   - Many unit tests (fast, focused)
   - Fewer integration tests (connections between components)
   - Small number of end-to-end tests (complete workflows)

8. **Writing Effective Assertions**:
   - Assert only what matters for correctness
   - For complex objects, test key properties instead of exact representation
   - Avoid assertions that make tests brittle during refactoring

## Example Test Patterns

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

### StarryNight Pipeline Test Pattern

```python
def test_starrynight_pipeline_composition():
    """Test that StarryNight pipeline is correctly composed with Pipecraft."""
    # Arrange: Create necessary modules and configurations
    data_config = DataConfig(...)
    experiment = Experiment(...)

    # Act: Compose pipeline
    modules, pipeline = create_example_pipeline(data_config, experiment)

    # Assert: Verify pipeline structure
    assert len(modules) == expected_module_count
    # Check for expected patterns of sequential/parallel execution
    # Verify container configurations
```

### CellProfiler Pipeline Generation Test Pattern

```python
def test_cellprofiler_pipeline_generation():
    """Test that a CellProfiler pipeline is generated correctly with expected modules."""
    # Arrange: Set up input data
    sample_data = {...}
    output_dir = Path("/tmp/test_output")

    # Act: Generate pipeline
    pipeline_path = gen_algorithm_cppipe(sample_data, output_dir)

    # Assert: Check key aspects of the pipeline, not every detail
    with open(pipeline_path) as f:
        pipeline_content = f.read()

    # Check for expected modules but not exact configuration
    assert "CorrectIlluminationCalculate" in pipeline_content
    assert "IdentifyPrimaryObjects" in pipeline_content

    # Verify critical settings only
    assert "BackgroundThreshold: 2.0" in pipeline_content
```

### Smart Parameter Testing Pattern

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    # Test boundary conditions and representative values, not every possibility
    (0, "zero"),            # Lower boundary
    (100, "maximum"),       # Upper boundary
    (50, "middle"),         # Representative value
    (-1, ValueError),       # Error case
])
def test_function_with_different_inputs(input_value, expected):
    """Test function behavior with key input values, not exhaustively."""
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            process_value(input_value)
    else:
        result = process_value(input_value)
        assert result == expected
```

## Running Tests

- Run all tests: `pytest`
- Run specific test file: `pytest path/to/test_file.py`
- Run specific test: `pytest path/to/test_file.py::test_function_name`
- Run tests with coverage: `pytest --cov=starrynight`

## Continuous Integration

- Tests should run automatically on push
- Maintain high code coverage
- Fix failing tests promptly

## Session Guidance

### Current Session Goals
- [ ] _Add specific goals for this session here_
- [ ] _Example: Implement tests for index generation algorithms_

### Progress Tracking
AI assistants should:
1. Review git commit history at the start of each session to understand what has been implemented
2. Focus on the goals specified for the current session
3. Create meaningful commit messages that document what was tested and implemented

No manual tracking is needed - git history serves as the record of progress.

## Anti-patterns to Avoid

1. **Testing Implementation Details**
   - ❌ Testing private methods directly
   - ❌ Asserting exact function call counts unnecessarily
   - ✅ Test the observable behavior through public interfaces

2. **Brittle Tests**
   - ❌ Asserting exact string matches for output
   - ❌ Testing exact data structures when only properties matter
   - ✅ Test for key properties and patterns that should remain stable

3. **Test Duplication**
   - ❌ Testing the same functionality at multiple levels
   - ❌ Creating multiple tests that verify the same thing
   - ✅ Test each behavior once at the appropriate level

4. **Over-mocking**
   - ❌ Mocking everything including simple dependencies
   - ❌ Creating complex mock chains that mirror implementation
   - ✅ Mock external dependencies but use real implementations when practical

5. **Exhaustive Input Testing**
   - ❌ Testing every possible input value
   - ❌ Creating tests for every possible parameter combination
   - ✅ Test boundaries, representative values, and error cases

Remember that test code is also code that needs to be maintained. The goal is to maximize the value of tests while minimizing their maintenance cost.

## Implementation Notes

### Component-Specific Guidance

#### CellProfiler Pipeline Tests
- Focus on validating presence of critical modules
- Check key parameters that affect scientific outcomes
- Don't test exact pipeline structure/organization

#### Path Parsing Tests
- Use a small set of representative paths
- Test edge cases (missing fields, extra components)
- Validate transformation of critical metadata fields

#### Module Specification Tests
- Validate paths are constructed correctly
- Verify input/output specifications match requirements
- Don't test every parameter detail

### Known Challenges
- **CellProfiler Integration**: May require special handling for Java VM initialization
- **Path Handling**: Cloud paths may need special mocking
- **Pipeline Generation**: Focus on key modules rather than exhaustive validation

### Test Implementation Shortcuts
- Use factory fixtures for common test data
- Mock file operations for faster tests
- Parameterize rather than duplicate test logic

