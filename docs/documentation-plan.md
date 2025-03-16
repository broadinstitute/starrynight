# StarryNight Documentation Plan

This document outlines the recommended structure for documentation to support both new developers and users of the StarryNight ecosystem.

## Current Documentation

- `docs/technical-architecture.md` - Overview of system architecture
- `docs/starrynight-cli-docs.md` - CLI usage guide for the illumination correction module
- `docs/data_flow.md` - High-level data flow descriptions for different user types
- `docs/notes.md` - CLI usage examples (may be redundant with starrynight-cli-docs.md)
- `docs/starrynight-docs/` - Partial user documentation in progress

## Recommended Documentation Structure

### For Developers

#### 1. Getting Started (`docs/developer/getting-started.md`)
- Development environment setup instructions
- Nix/flake usage guide
- Package dependencies and management
- Directory structure explanation

#### 2. Architecture (`docs/developer/architecture/`)
- `overview.md` - High-level architecture (extending existing technical-architecture.md)
- `pipecraft.md` - Detailed explanation of Pipecraft's design and components
- `starrynight.md` - Detailed explanation of StarryNight's modules and algorithms
- `conductor.md` - Detailed explanation of Conductor's API and database models

#### 3. Development Guides (`docs/developer/guides/`)
- `contributing.md` - Contribution guidelines and workflows
- `testing.md` - Testing approaches and patterns
- `extending.md` - How to extend the system with new modules or algorithms
- `deployment.md` - Deployment considerations and strategies

#### 4. API Reference (`docs/developer/api/`)
- `pipecraft-api.md` - API documentation for Pipecraft
- `starrynight-api.md` - API documentation for StarryNight
- `conductor-api.md` - API documentation for Conductor's REST endpoints

### For Users

#### 1. Getting Started (`docs/user/getting-started.md`)
- Installation instructions (different options)
- Basic concepts explanation
- Quick start guide

#### 2. Concepts (`docs/user/concepts/`)
- `projects.md` - What is a project and how to work with them
- `inventory-index.md` - Understanding inventory and index generation
- `modules.md` - Overview of available processing modules
- `pipelines.md` - Understanding pipeline structure and execution

#### 3. CLI Usage (`docs/user/cli/`)
- `overview.md` - General CLI usage patterns
- One guide per module, e.g., `illum-correction.md`, `preprocessing.md`, etc.
- `advanced-usage.md` - Advanced CLI features and options

#### 4. Web UI Usage (`docs/user/web-ui/`)
- `overview.md` - Introduction to the Canvas UI
- `projects.md` - Managing projects in the UI
- `jobs.md` - Configuring and running jobs
- `results.md` - Working with and analyzing results

#### 5. Tutorials (`docs/user/tutorials/`)
- End-to-end workflows for common use cases
- `basic-workflow.md` - Complete basic workflow
- `advanced-workflow.md` - More complex scenarios
- `troubleshooting.md` - Common issues and solutions

#### 6. Reference (`docs/user/reference/`)
- `cli-reference.md` - Complete CLI command reference
- `file-formats.md` - Description of file formats used
- `configuration.md` - Configuration options reference

## Documentation Generation

Consider using a documentation generator like MkDocs or Sphinx to:
- Automatically generate API documentation from docstrings
- Create a searchable documentation website
- Support versioning of documentation

## Priority Implementation Plan

1. First phase (highest priority):
   - Complete the developer getting started guide
   - Expand the user CLI documentation to cover all modules
   - Create the basic concepts documentation
   - Finish the web UI overview

2. Second phase:
   - Complete API references
   - Add detailed architecture documentation
   - Create end-to-end tutorials

3. Third phase:
   - Set up automated documentation generation
   - Add advanced usage guides
   - Complete reference documentation
