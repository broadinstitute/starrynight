"""Global pytest fixtures and configuration.

Place shared test fixtures here to make them available to all tests.

Notes on Test Fixtures Organization:
------------------------------------
This file contains fixtures for test data and workspace setup.

As the project grows, follow these organizational best practices:

1. Keep in conftest.py:
   - Simple fixtures that just extract files or create basic directory structures
   - Fixtures that need to be broadly available to many tests
   - Fixture registrations (even if implementation is elsewhere)

2. Move to specialized modules in tests/fixtures/ directory:
   - Complex fixtures over ~100 lines
   - Fixtures that run CLI commands or invoke application logic
   - Fixtures with extensive validation or setup logic
   - Fixtures that depend on multiple other fixtures

3. General organization principles:
   - Group fixtures by feature or functional area
   - Split into domain-specific conftest.py files in subdirectories as needed
   - Maintain clear documentation on fixture dependencies and usage

Assertion Philosophy:
- Keep minimal assertions in fixtures (only what's needed for the fixture to function)
- Verify basic preconditions (file exists, command succeeded) in fixtures
- Move detailed validation (content structure, schema, values) to test functions
- Fixtures verify "Can I do my job?" while tests verify "Did the fixture do its job correctly?"

Fixture Management:
- For complete instructions on creating and managing fixtures, see fixtures/integration/README.md
- Follow the standard pattern when adding new fixtures (fix_XX_*)
"""

import pytest

from .fixtures.integration.fixture_setup import (
    _setup_input_dir,
    _setup_output_dir,
    _setup_starrynight,
    _setup_workspace,
)


@pytest.fixture(scope="module")
def fix_s1_input_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S1 input data."""
    result = _setup_input_dir(tmp_path_factory, "fix_s1")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="module")
def fix_s2_input_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S2 input data."""
    result = _setup_input_dir(tmp_path_factory, "fix_s2")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="module")
def fix_s1_output_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S1 output data."""
    result = _setup_output_dir(tmp_path_factory, "fix_s1")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="module")
def fix_s2_output_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S2 output data."""
    result = _setup_output_dir(tmp_path_factory, "fix_s2")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="function")
def fix_s1_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-S1 tests."""
    return _setup_workspace(tmp_path_factory, "fix_s1")


@pytest.fixture(scope="function")
def fix_s2_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-S2 tests."""
    return _setup_workspace(tmp_path_factory, "fix_s2")


@pytest.fixture(scope="function")
def fix_s1_starrynight_generated(fix_s1_workspace, fix_s1_input_dir):
    """Fixture for FIX-S1 setup with generated files (via CLI)."""
    return _setup_starrynight(
        fix_s1_workspace, fix_s1_input_dir, "fix_s1", "generated"
    )


@pytest.fixture(scope="function")
def fix_s1_starrynight_pregenerated(fix_s1_workspace, fix_s1_input_dir):
    """Fixture for FIX-S1 setup with pre-generated files."""
    return _setup_starrynight(
        fix_s1_workspace, fix_s1_input_dir, "fix_s1", "pregenerated"
    )


@pytest.fixture(scope="function")
def fix_s2_starrynight_generated(fix_s2_workspace, fix_s2_input_dir):
    """Fixture for FIX-S2 setup with generated files (via CLI)."""
    return _setup_starrynight(
        fix_s2_workspace, fix_s2_input_dir, "fix_s2", "generated"
    )


@pytest.fixture(scope="function")
def fix_s2_starrynight_pregenerated(fix_s2_workspace, fix_s2_input_dir):
    """Fixture for FIX-S2 setup with pre-generated files."""
    return _setup_starrynight(
        fix_s2_workspace, fix_s2_input_dir, "fix_s2", "pregenerated"
    )


@pytest.fixture(scope="module")
def fix_l1_input_dir(tmp_path_factory):
    """Fixture that provides a directory with FIX-L1 input data (local-only)."""
    result = _setup_input_dir(tmp_path_factory, "fix_l1")
    yield result


@pytest.fixture(scope="module")
def fix_l1_output_dir(tmp_path_factory):
    """Fixture that provides a directory with FIX-L1 output data (local-only)."""
    result = _setup_output_dir(tmp_path_factory, "fix_l1")
    yield result


@pytest.fixture(scope="function")
def fix_l1_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-L1 tests."""
    return _setup_workspace(tmp_path_factory, "fix_l1")


@pytest.fixture(scope="function")
def fix_l1_starrynight_generated(fix_l1_workspace, fix_l1_input_dir):
    """Fixture for FIX-L1 setup with generated files (via CLI) - local-only."""
    return _setup_starrynight(
        fix_l1_workspace, fix_l1_input_dir, "fix_l1", "generated"
    )


@pytest.fixture(scope="function")
def fix_l1_starrynight_pregenerated(fix_l1_workspace, fix_l1_input_dir):
    """Fixture for FIX-L1 setup with pre-generated files - local-only."""
    return _setup_starrynight(
        fix_l1_workspace, fix_l1_input_dir, "fix_l1", "pregenerated"
    )
