# StarryNight Documentation

This directory contains documentation for the StarryNight image processing system.

## Building the Documentation

StarryNight uses MkDocs with the Material theme to generate a documentation website.

### Setup

Install the documentation dependencies:

```bash
pip install -r requirements-docs.txt
```

### Local Development

To preview the documentation locally:

```bash
# From the docs directory
mkdocs serve

# Or from the project root
mkdocs serve -f docs/mkdocs.yml
```

This will start a local server at http://localhost:8000 where you can preview the documentation.

### Building the Site

To build the static site:

```bash
# From the docs directory
mkdocs build

# Or from the project root
mkdocs build -f docs/mkdocs.yml
```

This will generate the static site in the `site` directory.

## Documentation Structure

### Conceptual Guides
- [Architecture Overview](architecture.md) - System components and interactions (including data flow)
- [Core Concepts](concepts/overview.md) - What StarryNight does and its purpose
- [Inventory and Index](concepts/inventory-index.md) - Understanding data organization

### User Documentation
- [CLI Workflows](user/cli-workflows/)
  * [Setup Guide](user/cli-workflows/setup.md) - Environment and data preparation
  * [Illumination Correction](user/cli-workflows/illumination-correction.md) - Step-by-step workflow
- [Web UI](user/web-ui/)
  * [Getting Started](user/web-ui/getting-started.md) - How to use the web interface

### Developer Documentation
- [Getting Started](developer/getting-started.md) - Developer environment setup

## Documentation Roadmap

Additional documentation planned for future releases:

1. Module-specific guides for all processing steps
2. Advanced configuration options
3. Extension and customization guide
4. Troubleshooting and FAQ
5. API reference documentation

## Contributing to Documentation

When adding new documentation:
- Place conceptual guides in the `concepts/` directory
- Add user guides based on usage mode (CLI or Web UI)
- Include code examples where appropriate
- Follow the existing documentation style
- Test your changes locally with `mkdocs serve`
