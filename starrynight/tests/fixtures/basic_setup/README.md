# Basic Setup Fixtures

Pre-generated files for faster LoadData test execution.

## Files

- `experiment.json`: Generated experiment config (steps 1-5 of getting-started workflow)
- `index.parquet`: Generated index file (steps 1-5 of getting-started workflow)

## Usage

Used by `fix_starrynight_pregenerated_setup` fixture to skip steps 1-5 of workflow.

Run fast tests with:
```bash
pytest test_getting_started_workflow.py -k fast
```
