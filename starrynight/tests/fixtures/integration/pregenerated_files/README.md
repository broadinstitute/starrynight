# Pre-generated Test Fixtures

Pre-generated files used for faster test runs without running the full StarryNight CLI.

```bash
# Regenerate a specific fixture
REGENERATE_FIXTURES=1 uv run pytest -xvs fixtures/integration/pregenerated_files/regenerate.py::test_generate_pregenerated_files_files[fix_s1]
```

For complete fixture management instructions, see [../README.md](../README.md).
