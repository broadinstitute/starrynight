# Developer Guide

This guide provides setup instructions for developers who want to contribute to StarryNight.

## Development Environment Setup

```sh
# Clone the repository
git clone https://github.com/broadinstitute/starrynight.git
cd starrynight

# Set up the Nix environment
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes .

# Synchronize Python dependencies
uv sync

# Verify installation
starrynight --help
pipecraft --help
conductor --help
```

## Documentation

For detailed information on the project architecture and how to extend components, see the [Architecture Overview](../../architecture/00_architecture_overview.md).
