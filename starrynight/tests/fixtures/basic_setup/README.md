# Basic Setup Fixtures

Pre-generated files for faster LoadData test execution.

## Files

- `experiment.json`: Generated experiment config (steps 1-5 of getting-started workflow)
- `index.parquet`: Generated index file (steps 1-5 of getting-started workflow)
- `generate_fixtures.py`: Utility to regenerate these files when needed

## Usage

Used by fix_starrynight_setup["pregenerated"]` fixture to skip steps 1-5 of workflow.

Run fast tests with:
```bash
pytest test_getting_started_workflow.py -k fast
```

## Regenerating Fixtures

To regenerate these files (if needed after code changes):

```bash
cd /Users/shsingh/Documents/GitHub/starrynight
REGENERATE_FIXTURES=1 uv run pytest -xvs starrynight/tests/fixtures/basic_setup/generate_fixtures.py
```

This will run the fixture generation process and replace the existing files with freshly generated versions.
