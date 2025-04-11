# StarryNight Testing Framework

Tools for testing, validating, and creating test fixtures for PCPIP (Pooled Cell Painting Image Processing) workflows.

## Components

The testing framework consists of several key components:

### Documentation

- [**Testing Strategy**](testing-strategy.md): Overview of the testing approach and validation process
- [**Pipeline Validations**](pipeline-validations/pipeline-validation-overview.md): Detailed procedures for validating each PCPIP pipeline
- [**Testing Tools**](tools/overview.md): Reference guide for the tools used in validation

### Reference Assets

- [**pcpip-pipelines**](assets/pcpip-pipelines/README.md): Reference CellProfiler pipeline files for PCPIP workflow
- [**pcpip-create-fixture**](assets/pcpip-create-fixture/README.md): Tools for creating test fixtures from AWS S3 data
- [**pcpip-test**](assets/pcpip-test/README.md): Scripts for pipeline execution, validation, and comparison

## Getting Started

**New to StarryNight Testing?** Follow these steps:

1. Read the [Testing Strategy](testing-strategy.md) to understand the overall validation approach
2. Review the [Pipeline Validation Overview](pipeline-validations/pipeline-validation-overview.md) to see all pipelines that need validation
3. Examine the [Pipeline 1 (illum_calc) Validation](pipeline-validations/pipeline-1-validation-illum-calc.md) as a concrete example
4. If needed, consult the [Testing Tools Reference](tools/overview.md) for details on individual tools

## Validation Workflow

The complete validation process involves:

1. **Understand Reference Pipelines**: Examine the CellProfiler pipelines in `pcpip-pipelines` as reference implementations
2. **Prepare Test Data**: Either use existing test fixtures or create new ones with tools in `pcpip-create-fixture`
3. **Run Reference Pipelines**: Execute reference pipelines on test data to establish baseline outputs
4. **Test StarryNight Implementation**: Verify StarryNight produces equivalent outputs through the 5-stage validation process
5. **Document Results**: Update validation documents and GitHub issues with findings

For each pipeline validation, follow the 5-stage process:

1. **Graph Topology**: Compare pipeline structures
2. **LoadData Generation**: Verify compatible CSV generation
3. **Reference Execution**: Run reference pipelines
4. **StarryNight Pipeline**: Test StarryNight-generated pipelines
5. **End-to-End**: Verify complete workflow

For detailed instructions on each step, refer to the individual pipeline validation documents.
