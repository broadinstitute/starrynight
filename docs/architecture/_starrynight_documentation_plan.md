# Starry Night Documentation Plan (Phase 2)

## Executive Summary
This document outlines the comprehensive plan for Phase 2 of the Starry Night documentation project. The goal is to create detailed technical explanations of the Starry Night architecture based on the transcript discussions, organized into logical components that follow the system's design.

## Documentation Objectives
- Provide clear, accurate explanations of each Starry Night component
- Make complex architectural concepts accessible to developers
- Document component relationships and dependencies
- Create a foundation for future technical documentation

## Target Audience
- Software engineers working on the Starry Night project
- Computational biologists integrating with the system
- Technical stakeholders evaluating the architecture

## Documentation Structure

### 1. Architecture Overview (00_architecture_overview.md)
- System-level explanation of Starry Night
- Layer structure and key abstractions
- Core design principles and patterns
- Visual representation of component relationships

### 2. Component Explanations

#### Algorithm Layer (01-02)
- **01_algorithms_foundation.md**
  - Core algorithm concept and organization
  - Algorithm sets structure (load data, pipeline generation, execution)
  - Common patterns across algorithm implementations
  - Detailed analysis of algorithms/analysis.py as case study

#### CLI Layer (03)
- **03_cli_integration.md**
  - CLI as algorithm wrappers
  - Click library implementation details
  - Command group structure and organization
  - Path handling with cloudpathlib (AnyPath)
  - Example CLI command construction and execution

#### Module System (04-05)
- **04_module_abstraction.md**
  - Module concept and purpose
  - Relationship to algorithms
  - Module structure and organization
  - Standardized interfaces and patterns

- **05_bilayer_integration.md**
  - Bilayer specs for input/output definitions
  - Spec construction and validation
  - Documentation features in specifications
  - Connection to UI representation

#### Pipeline Construction (06, 12)
- **06_pipecraft_integration.md**
  - Pipecraft library overview
  - Container specification
  - Pipeline node definition
  - Graph construction principles

- **12_pipeline_composition.md**
  - Combining modules into pipelines
  - Parallel and sequential execution
  - Pipeline structure patterns
  - Error handling and monitoring

#### Execution System (07-08)
- **07_execution_model.md**
  - Notebook workflow patterns
  - Backend selection and configuration
  - Execution context and state management
  - Logging and monitoring

- **08_snakemake_backend.md**
  - Snakemake file generation process
  - Rule construction from pipelines
  - Container configuration
  - Execution patterns and parallelism

#### Experiment Configuration (09-11)
- **09_experiment_configuration.md**
  - Experiment class structure
  - Parameter inference from data
  - Default configuration patterns
  - Extending for new experiments

- **10_11_module_configuration.md**
  - Module configuration from experiments
  - Configuration patterns and practices
  - Example configurations for CP modules
  - Common configuration issues and solutions

### 3. Integration and Extension Guide
- **13_integration_extension.md**
  - Integrating new algorithms
  - Creating custom modules
  - Extending the pipeline system
  - Best practices for contributions

## Implementation Details

### Source Material References
- Primary source code: `../../starrynight/src/`
- Pipecraft source code: `../../pipecraft/src/`
- Developer documentation: `../../docs/developer-guide.md`
- Transcript sections from indexed document

### Terminology Standards
- **Framework Components**
  - Starry Night: Overall framework
  - Pipecraft: Library for pipeline creation
  - Bilayers: Schema system for specifications
  - Canvas: UI component
  - Conductor: Execution orchestration component

- **Pipeline Components**
  - CP: Cell Painting (not CellProfiler)
  - CellProfiler: Image analysis platform (always written in full)
  - PCP: Plate Cell Painting
  - SBS: Sequencing By Synthesis

- **Technical Terms**
  - ILLUM: Illumination
  - Mito: Mitochondrial
  - Segmentation check: Pipeline validation component
  - Barcode: Cell identification

- **Technology Stack**
  - Snakemake: Workflow management system
  - CLI: Command Line Interface
  - Docker/Singularity: Container technologies
  - Open Telemetry: Observability framework

### Documentation Format
Each document will follow a consistent structure:

1. **Overview**: Brief introduction to the component
2. **Purpose**: Why this component exists and its role
3. **Structure**: How the component is organized
4. **Implementation**: Technical details with code examples
5. **Integration**: How it connects with other components
6. **Examples**: Concrete usage examples
7. **Common Patterns**: Recurring implementations
8. **References**: Links to source code and related components

### Diagrams
Recommended diagrams to include:

1. **System Architecture Diagram**
   - Shows all components and their relationships
   - Highlights data flow between components

2. **Layer Diagram**
   - Illustrates the hierarchical nature of the system
   - Shows dependencies between layers

3. **Module Lifecycle Diagram**
   - Demonstrates the creation, configuration, and execution of a module
   - Shows state transitions

4. **Pipeline Construction Diagram**
   - Visualizes how individual modules connect to form pipelines
   - Shows parallel and sequential execution paths

5. **Execution Flow Diagram**
   - Traces a request from notebook to container execution
   - Highlights the transformation of high-level requests to low-level commands

## Development Process

### Phase Structure
1. **Research Phase** (1-2 days)
   - Review source code thoroughly
   - Analyze transcript sections
   - Identify key patterns and connections

2. **Content Development** (5-7 days)
   - Create individual component documents
   - Develop diagrams and visual aids
   - Review and refine technical accuracy

3. **Integration and Review** (2-3 days)
   - Ensure consistency across documents
   - Verify terminology usage
   - Test document navigation and flow

### Quality Standards
- Technical accuracy validated against source code
- Clear, concise explanations without unnecessary jargon
- Consistent terminology throughout documents
- Practical examples that demonstrate real usage
- Proper attribution of source material

## Next Steps
1. Begin with the Architecture Overview document
2. Progress through component explanations in sequential order
3. "Develop integration guide once component docs are complete""
4. Create final index document linking all resources

## Future Considerations
- Interactive documentation with executable examples
- Video tutorials for complex workflows
- Contribution guidelines for documentation maintenance
- Version-specific documentation branches
