# Basic Test Fixtures for StarryNight

This directory contains basic test fixtures used for testing the StarryNight workflow.

## Directory Structure

Each fixture has its own subdirectory:

- `fix_s1/`: FIX-S1 test fixture (original configuration)
- `fix_s2/`: FIX-S2 test fixture (identical inputs but different channel mappings)

## Fixture Generation

Fixtures are generated using the `fixture_utils.sh` script in the `fixtures/fixture_utils/` directory.

To generate new fixtures:

1. Modify the `FIXTURE_ID` variable in the script (e.g., "s1", "s2")
2. Run the script to create the archives and SHA256 hashes
3. Update the SHA256 hashes in `conftest.py` with the values from the generated `.sha256` files
4. Copy the archives to the appropriate release location

## Using Fixtures in Tests

Fixtures can be used in tests by parameterizing the `fix_starrynight_setup` fixture:

```python
@pytest.mark.parametrize(
    "fix_starrynight_setup",
    [{"mode": "generated", "fixture": "fix_s1"}],
    indirect=True
)
def test_with_fix_s1(fix_starrynight_setup):
    # Test with FIX-S1 configuration
    ...

@pytest.mark.parametrize(
    "fix_starrynight_setup",
    [{"mode": "generated", "fixture": "fix_s2"}],
    indirect=True
)
def test_with_fix_s2(fix_starrynight_setup):
    # Test with FIX-S2 configuration
    ...
```

For faster tests, use the "pregenerated" mode:

```python
@pytest.mark.parametrize(
    "fix_starrynight_setup",
    [{"mode": "pregenerated", "fixture": "fix_s2"}],
    indirect=True
)
```

## Adding New Fixtures

1. Create a new fixture ID in the `FIXTURE_CHANNEL_CONFIGS` dictionary in `conftest.py`
2. Generate the fixture data using `fixture_utils.sh` with the new fixture ID
3. Create a subdirectory with the fixture name and add the required files
4. Update the registry in `conftest.py` with the new SHA256 hashes
