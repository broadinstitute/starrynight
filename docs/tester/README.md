# StarryNight Testing Framework

Tools for testing, validating, and creating test fixtures for PCPIP (Pooled Cell Painting Image Processing) workflows.

## Components

The tester directory contains several specialized tools:

- **pcpip-pipelines**: Documentation for pipeline selection and comparison
- **pcpip-create-fixture**: Tools for creating test fixtures from AWS S3 data
- **pcpip-test**: Test suite for validating pipeline outputs using structure validation
- **pcpip-generate-dummy-structures**: Utilities to simulate directory structures

## Purpose

These tools enable reliable testing of the PCPIP workflow by:

1. Ensuring consistency between pipeline versions
2. Creating reproducible test fixtures from real data
3. Validating file structure and contents produced by pipelines
4. Generating synthetic test structures when real data isn't available
