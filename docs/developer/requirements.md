# Requirements

## 1. System Overview

This document outlines requirements for a next-generation system for processing, analyzing, and managing high-throughput microscopy data from image-based profiling experiments, in particular, pooled optical screens. The system will orchestrate complex image processing workflows, manage computational resources efficiently, and provide mechanisms for both automated and manual intervention during the processing pipeline.

Key:

- starrynight roadmap: 🟦 planned 🟨 in progress 🔲 not planned
- priority: ☑️ low ☑️☑️ medium ☑️☑️☑️ high

## 2. Core Requirements

### 2.1 Image Processing Capabilities

- 🟨 ☑️☑️☑️: **Must support automated execution of CellProfiler pipelines** for all stages of image processing:
    - Illumination correction calculation and application
    - Cell segmentation and validation
    - Image stitching and cropping
    - Channel alignment across imaging cycles
    - Barcode identification and calling
    - Feature extraction and analysis
- 🟨 ☑️☑️☑️: **Must process both Cell Painting (CP) and Barcoding (BC) image tracks** in parallel, with integration points for combined analysis.
- 🟨 ☑️☑️☑️: **Must allow integration of non-CellProfiler image processing tools** such as FIJI/ImageJ and custom analysis scripts.

### 2.2 Experimental Configuration

Note: This section has been intentionally over-specified to capture everything but should be pruned as needed

TODO:

- Beth and Erin should clarify which of these should ALWAYS be manually specified or should some be guessed
- For example `barcoding_imperwell` can be guessed but say `painting_rows`, `painting_columns` cannot be guessed and in the current system there's an if/then block that specifies the values of `painting_rows`, `painting_columns` based on `barcoding_imperwell`
- Which should be guessed, which should be specified?

- 🟦 ☑️☑️☑️: **Must support all image grid configuration parameters**:
    - `painting_rows`, `painting_columns`: For square acquisition patterns
    - `painting_imperwell`: For circular acquisition patterns (overrides rows/columns)
    - `barcoding_rows`, `barcoding_columns`: For square acquisition patterns
    - `barcoding_imperwell`: For circular acquisition patterns (overrides rows/columns)
- 🟦 ☑️☑️☑️: **Must support complex channel dictionary configuration**:
    - Mapping microscope channel names to biological stains and frame indices
    - Multi-round experiment support (e.g., SABER) with round identifiers
    - Single-round experiment support with simpler configuration
- 🟦 ☑️☑️☑️: **Must support processing configuration settings**:
    - `one_or_many_files`: File organization strategy per well
    - `fast_or_slow_mode`: CSV generation and processing strategy
    - `barcoding_cycles`: Number of barcoding cycles to process
    - `range_skip`: Sampling frequency for quality control
- 🟦 ☑️☑️☑️: **Must support detailed stitching configuration**:
    - `overlap_pct`: Image overlap percentage between fields
    - `stitchorder`: Tile arrangement strategy based on acquisition pattern
    - `tileperside`: Number of tiles along each side of the stitched grid
    - `final_tile_size`: Pixel dimensions of output tiles
    - `round_or_square`: Well shape for cropping calculations
    - `quarter_if_round`: Division strategy for round wells
    - Offset parameters for alignment troubleshooting
    - `compress`: Output file compression settings

### 2.3 Workflow Control

- 🟨 ☑️☑️: **Must support fully automated end-to-end processing** with configurable pipeline sequences:
    - While current optical pooled screening experiments require significant human judgment at multiple stages, the system should be designed to enable full automation as a long-term goal
    - Must support both fully automated workflows for mature processing paths and semi-automated workflows requiring human intervention
    - Must allow gradual transition from manual to automated processing as confidence in automated methods increases
- 🟨 ☑️☑️☑️: **Must enable manual intervention at any stage** with the ability to:
    - Restart pipeline from checkpoint
    - Inspect intermediate results before proceeding
    - Modify parameters between stages
    - Re-run specific stages with adjusted settings
    - Launch inspection notebooks

### 2.4 Compute Resource Management

- 🟦 ☑️☑️: **Must efficiently manage computational resources** appropriate to each processing stage:
    - Scale resources based on workload
    - Optimize resource allocation for memory-intensive vs. CPU-intensive tasks
    - Support parallel processing of independent tasks
- 🟨 ☑️☑️: **Must work across diverse compute environments**:
    - Cloud platforms (☑️☑️☑️: AWS, 🔲: Azure, 🔲: GCP)
    - 🔲: On-premises high-performance computing clusters
    - ☑️☑️☑️: Local workstations (with appropriate scaling)

### 2.5 Data Management

- 🟨 ☑️☑️☑️: **Must organize input and output data** in a consistent, browsable structure:
    - Must maintain compatibility with existing input and output data structures
    - Must produce outputs that match current output structures, which will remain rigid unless changed at the level of code
    - Must provide clear documentation for any structural changes
- 🟦 ☑️☑️: **Must track data provenance** including:
    - Processing history for each image
    - Parameters used at each stage
    - Software versions and dependencies
    - Note: Implementation should prioritize critical tracking elements needed for reproducibility while balancing system performance.
- 🟨 ☑️☑️☑️: **Must handle large data volumes** (terabytes) with AWS backend.
- 🟨 ☑️☑️☑️: **Must implement flexible path parsing and data organization**:
    - Standardized but configurable system for extracting metadata from file paths
    - Support for mapping from various microscope vendor file organizations to internal structure
    - Ability to adapt to different naming conventions without code changes

### 2.6 User Interaction

- 🟨 ☑️☑️☑️: **Must provide multiple interaction mechanisms**:
    - Command-line interface for scripting and automation
    - Web-based or desktop GUI for visualization and control
    - Programmatic API for integration with other systems
- 🟨 ☑️☑️☑️: **Must support both expert and non-expert users** with appropriate levels of abstraction and guidance.
    - Web-based UI must provide two abstraction levels:
        - Simplified interface for non-computational scientists with guided workflows and sensible defaults
        - Advanced interface with full parameter control for experienced users
    - Command-line interface and programmatic API will target computational experts only, with comprehensive documentation
- 🟨 ☑️☑️☑️: **Must integrate result visualization and quality control**:
    - Built-in visualization tools for reviewing processing results, including cell segmentation, barcode calling, and feature data
    - Integrated quality control metrics with contextual interpretations
- 🟨 ☑️☑️☑️: **Must provide interactive inspection tools**:
    - Support for Jupyter notebooks (or similar) as a first-class inspection interface

## 3. Technical Requirements

### 3.1 Cross-Platform Support

- 🟦 ☑️: **Must run on ☑️☑️☑️Linux, ☑️☑️MacOS, and ☑️Windows (WSL)** operating systems.

### 3.2 Extensibility

- 🟦 ☑️☑️☑️: **Must allow addition of new processing tools** beyond CellProfiler.
- 🟦 ☑️: **Must support custom analysis modules** for specialized experiments.

### 3.3 Documentation and Support

- 🟨 ☑️☑️☑️: **Must provide comprehensive user documentation** including installation and setup guides, configuration reference, workflow tutorials, and troubleshooting information.
    - Workflow tutorials and certain aspects of troubleshooting/setup guides will be developed collaboratively with end users, with the expectation that users will eventually maintain these materials
- 🟨 ☑️☑️☑️: **Must include developer documentation** covering architecture overview, API references, extension guides, development setup, and technical decision rationale that explains key design choices and alternatives considered :sta
