# StarryNight Testing

> **Important**: All commands in this guide assume you're in the `starrynight/` directory, not the repository root.
>
> ```bash
> cd starrynight/  # Run this first!
> ```

## Project Context

StarryNight is a multi-package framework for analyzing Cell Painting microscopy data:

- **starrynight**: Core image processing and analysis (this package)
- **pipecraft**: Pipeline execution framework
- **conductor**: Workflow orchestration

This guide covers testing for the `starrynight` package specifically.

## Overview

-   Pytest-based framework with two distinct testing approaches:
    - **Unit tests**: Simple, focused tests of individual functions
    - **Integration tests**: Complex fixture-based tests of complete workflows
-   Key dependencies: pytest, pytest-cov (optional for coverage), duckdb, polars

## Prerequisites

Ensure you're in the Nix development shell before running tests:

```bash
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes .
```

This provides CellProfiler and other required dependencies. See [Getting Started](../../docs/user/getting-started.md) for full setup instructions.

## Quick Start

```bash
# Run all tests
uv run pytest

# Run only unit tests
uv run pytest tests/algorithms tests/parsers

# Run only integration tests
uv run pytest tests/integration
```

## Test Structure

```text
starrynight/tests/
├── algorithms/         # Unit tests
├── parsers/            # Unit tests
├── utils/              # Test utilities (not tests themselves)
├── integration/        # Integration tests (complex fixtures)
├── fixtures/           # Integration test data only
├── conftest.py         # Shared fixtures (mostly for integration)
└── test_fixtures.py    # Integration fixture validation
```

## Getting Started with Testing

### Your First Test (No Fixtures Needed)

If you're new to the codebase, start with simple unit tests:

```python
# tests/parsers/test_parser_vincent.py
def test_parse_simple_case():
    """My first test - no fixtures or complex setup needed!"""
    from starrynight.parsers.parser_vincent import parse_metadata

    # Just test the function directly
    metadata = parse_metadata("example_data")

    assert metadata is not None
    # Add your assertions here
```

Run it: `uv run pytest tests/parsers/test_parser_vincent.py -v`

### Unit Testing

Simple tests for individual functions - no special setup required.

```python
def test_parse_filename_extracts_metadata():
    """Test that parser correctly extracts metadata from filename."""
    result = parse_filename("Plate1_Well2_Site3_Channel4.tif")
    assert result.plate == "Plate1"
    assert result.well == "Well2"
```

## Integration Testing

Complex tests for complete workflows using the fixture system.

```python
def test_complete_workflow(fix_s1_starrynight_pregenerated):
    """Test end-to-end workflow from raw images to analysis."""
    # Uses pre-generated test data
    # Tests multiple CLI commands in sequence
    # Validates final outputs
```

### Fixture System

-   **Purpose**: Provide consistent test environments with real microscopy data
-   **Naming Convention**:
    - `fix_` prefix - All fixtures start with this
    - `s1`, `s2` - **Small datasets** (1-2 images, ~seconds to process)
    - `l1`, `l2` - **Large datasets** (full plates, ~minutes to process)
    - Numbers (1, 2) - Different example datasets for variety
-   **Available fixtures**:
    - `fix_s1_*` - Small dataset #1 (2 images, 1 well)
    - `fix_s2_*` - Small dataset #2 (2 images, 1 well)
    - `fix_l1_*` - Large dataset #1 (planned)
    - `fix_l2_*` - Large dataset #2 (planned)
-   **Modes**:
    - `generated` - Runs full CLI to create test data (slower, ~30s)
    - `pregenerated` - Uses cached data (faster, ~2s)

### Local Fixtures

```bash
# Skip downloads, use local data
export STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/local/fixtures
uv run pytest tests/integration
```

## Running Tests

```bash
# Specific file
uv run pytest tests/algorithms/test_index_algorithm.py

# Pattern matching
uv run pytest tests/integration -k "fix_s1 and pregenerated"

```

## Adding Tests

### Unit Tests

Just add a `test_*.py` file following existing patterns.

### Integration Tests

1. Use existing fixtures when possible
2. For new fixtures, see [fixtures/integration/README.md](fixtures/integration/README.md)
3. Update `integration/constants.py` for workflow compatibility

## Test Coverage

### Running with Coverage

```bash
# First install pytest-cov if not already installed
uv pip install pytest-cov

# Generate coverage report
uv run pytest --cov=starrynight --cov-report=html

# View coverage in terminal
uv run pytest --cov=starrynight --cov-report=term-missing

# Coverage for specific module
uv run pytest --cov=starrynight.parsers tests/parsers/

# List available fixtures
uv run pytest --fixtures
```

## Continuous Integration

Tests run automatically on:

- Every push to a PR
- Daily on main branch
- Before releases

See `.github/workflows/test.yml` for CI configuration.

## Troubleshooting

### Common Issues

- **Import errors**: Ensure you're in the Nix shell (`nix develop`)
- **Fixture download fails**: Check network connection and AWS access
- **Tests hang**: Use `pytest --timeout=300` to add timeouts

### Debug Commands

```bash
# Debug mode (stop on failure, verbose, show output)
uv run pytest -xvs tests/integration/test_getting_started_workflow.py::test_complete_workflow

# Show fixture setup/teardown
uv run pytest --setup-show

# Run with Python warnings
uv run pytest -W default

# Maximum verbosity
uv run pytest -vvv
```

## Reference

- [fixtures/README.md](fixtures/README.md) - Overview of test fixtures
- [fixtures/integration/README.md](fixtures/integration/README.md) - Detailed integration fixture creation guide

## TODO: Future Improvements

### Documentation

- [ ] Add pytest.ini or pyproject.toml [tool.pytest.ini_options] configuration
- [ ] Document test markers (slow, gpu, integration) if they exist

### Coverage & Quality

- [ ] Add pytest-cov to default dev dependencies
- [ ] Set up coverage badge and thresholds
- [ ] Add pre-commit hooks for test linting

### Infrastructure

- [ ] Document minimal test fixtures for contributors without AWS access
- [ ] Add test data generation scripts for local development
- [ ] Create GitHub Actions matrix for different test categories
- [ ] Set up parallel test execution in CI

### Cross-Package Testing

- [ ] Document how to test interactions between starrynight, pipecraft, and conductor
- [ ] Create integration tests that span multiple packages
- [ ] Add examples of mocking cross-package dependencies
