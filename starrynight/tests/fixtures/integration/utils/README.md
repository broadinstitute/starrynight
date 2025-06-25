# Test Fixture Creation

Create test fixtures from production microscopy data using `fixture_utils.sh`.

## Quick Start

```bash
# Set required environment variables
export BUCKET="your-source-bucket"
export PROJECT="your-project-path"
export BATCH="your-batch-name"
export DEST_BUCKET="your-destination-bucket"

# Choose fixture type
export FIXTURE_ID="l1"  # Options: s1, s2, l1

# Run sections manually in fixture_utils.sh
cd starrynight/tests/fixtures/integration/utils
# Open fixture_utils.sh and run each section step by step
```

## Available Fixtures

- **s1, s2**: Small fixtures (3 wells, 4 sites each, ~37MB)
- **l1**: Large fixture (1 well, 1025 sites, ~10GB)

## Adding a New Fixture Type

1.  Add a case in `fixture_utils.sh`:

   ```bash
   case "${FIXTURE_ID}" in
       "my_fixture")
           FILTER_PLATE="Plate1"
           FILTER_WELLS="WellA1,WellA2"
           FILTER_SITES="0,1,2,3"
           FILTER_CYCLES="1,2,3"
           ;;
   ```

2.  Add matching configuration in `create_starrynight_download_list.py`:

   ```python
   elif FIXTURE_ID == "my_fixture":
       WELLS = ["A1", "A2"]
       SITES = list(range(0, 4))
       CYCLES = range(1, 4)
   ```

3.  Run with `export FIXTURE_ID="my_fixture"`

## Notes

- See script headers for detailed documentation
- Dataset-specific paths may need adjustment in SECTION 1
- Missing file warnings during validation are expected (see script comments)

For fixture usage in tests, see [../README.md](../README.md).
