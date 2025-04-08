# StarryNight Testing Framework

Tools for testing, validating, and creating test fixtures for PCPIP (Pooled Cell Painting Image Processing) workflows.

## Components

The tester directory contains several specialized tools:

- [**pcpip-pipelines**](assets/pcpip-pipelines/README.md): Reference CellProfiler pipeline files for PCPIP workflow. These serve as the standard for testing and as the basis for any new systems built on PCPIP.
- [**pcpip-create-fixture**](assets/pcpip-create-fixture/README.md): Tools for repository maintainers to create test fixtures from private AWS S3 data, generating download lists for public access, and filtering LoadData CSVs for testing.
- [**pcpip-test**](assets/pcpip-test/README.md): Scripts to run reference pipelines end-to-end on fixture datasets, verify output file structure, and systematically compare results with reference outputs.

## Usage

The testing framework supports the following workflow:

1. **Reference Pipelines**: Access standard CellProfiler pipelines in `pcpip-pipelines` as reference implementations.
2. **Test Fixture Creation**: Use tools in `pcpip-create-fixture` to:
      - Generate download lists from source S3 data
      - Download files to create local test fixtures
      - Filter LoadData CSV files to create manageable test datasets
3. **Pipeline Testing**: Use scripts in `pcpip-test` to:
      - Run reference pipelines on test fixtures from end to end
      - Verify the structure of pipeline outputs
      - Compare outputs with reference results

For detailed instructions on each step, refer to the individual component README files.
