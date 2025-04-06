# StarryNight Testing Framework

Tools for testing, validating, and creating test fixtures for PCPIP (Pooled Cell Painting Image Processing) workflows.

## Components

The tester directory contains several specialized tools:

- [**pcpip-pipelines**](assets/pcpip-pipelines/README.md): Documentation for pipeline selection and comparison
- [**pcpip-create-fixture**](assets/pcpip-create-fixture/README.md): Tools for creating test fixtures from AWS S3 data
- [**pcpip-test**](assets/pcpip-test/README.md): Test suite for validating pipeline outputs using structure validation
- [**pcpip-generate-dummy-structures**](assets/pcpip-generate-dummy-structures/README.md): Utilities to simulate directory structures

## Purpose

These tools enable reliable testing of the PCPIP workflow by:

1. Ensuring consistency between pipeline versions
2. Creating reproducible test fixtures from real data
3. Validating file structure and contents produced by pipelines
4. Generating synthetic test structures when real data isn't available
