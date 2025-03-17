# StarryNight Documentation

Welcome to the StarryNight platform documentation. StarryNight is a comprehensive toolkit for processing, analyzing, and managing optical pooled screening (OPS) image data.

## Documentation

- **Getting Started**
    - [Installation](installation.md)
    - [Quick Start Guide](quickstart.md)
- **User Guide**
    - [Core Concepts](core-concepts.md)
    - [Processing Modules](modules.md)
    - [Illumination Correction](illumination-correction.md)
    - [Canvas UI](ui-guide.md)
- **Reference**
    - [CLI Reference](cli-reference.md)
- **Development**
    - [Developer Guide](developer-guide.md)
- **Help**
    - [FAQ & Troubleshooting](faq.md)

## Platform Overview

StarryNight is composed of three main components:

### StarryNight Core

The foundation of the platform providing specialized algorithms for microscopy image analysis:

- Image inventory and indexing
- Illumination correction
- Image alignment
- Preprocessing and quality control
- Cell Painting specific analyses
- Sequencing-based image processing

### PipeCraft

A workflow engine for orchestrating complex analysis pipelines:

- Pipeline definition framework
- Support for multiple execution backends
- Predefined workflow templates
- Scaling from local to cloud environments

### Conductor

Job management and monitoring system:

- Project organization
- Job configuration and execution
- Run monitoring and results management
- Canvas web UI for intuitive interaction

## License

StarryNight is released under the [MIT License](https://github.com/broadinstitute/starrynight/blob/main/LICENSE).
