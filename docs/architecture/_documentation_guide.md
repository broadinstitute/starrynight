# Starry Night Documentation Guide

## Overview

This document explains how the Starry Night architecture documentation was created, structured, and how to maintain it moving forward. It provides guidelines for documentation standards, organization, and suggestions for future improvements.

## Documentation Creation Process

### Source Materials

The documentation was created based on several key source materials:

1. **Transcript Files**:
   - `Starry Night Pipeline Overview.txt` - Primary transcript with detailed architectural walkthrough
   - `Algorithm System Overview.txt` - Supplementary transcript on algorithm design
   - `Module System Overview.txt` - Supplementary transcript on module system

2. **Source Code**:
   - Starry Night source code at `../../starrynight/src/`
   - Pipecraft source code at `../../pipecraft/src/`
   - Developer guide at `../../docs/developer-guide.md`

3. **PCPIP Documentation**:
   - Documentation on the predecessor system (PCPIP) for reference and comparison

### Creation Methodology

The documentation creation followed this process:

1. **Content Analysis** - The transcript was analyzed to identify key components, relationships, and architectural decisions.

2. **Content Organization** - The transcript was broken down into logical sections following the architecture's natural layering:
   - Algorithm Layer
   - CLI Layer
   - Module Layer
   - Pipeline Layer
   - Execution Layer

3. **Document Structure** - Each document was structured with consistent sections:
   - Overview - Brief introduction
   - Purpose - Why the component exists
   - Implementation details - How it works
   - Examples - Code examples showing usage
   - Relationships - Connections to other components

4. **Critical Points Emphasis** - Based on supplementary transcripts, key architectural principles were emphasized:
   - Algorithm independence
   - Module dual focus (spec + compute graph)
   - Backend-agnostic execution
   - Automatic generation of complex workflows

5. **MkDocs Integration** - Documentation was organized into a hierarchical structure for MkDocs.

6. **Audience Adaptation** - Additional documents were created for specific audiences (e.g., biologists) with appropriate terminology and focus.

## Document Structure

### File Organization

The documentation follows this file organization:

```
architecture/
├── 00_architecture_overview.md      # High-level overview
├── 01_algorithms_foundation.md      # Algorithm layer
├── 03_cli_integration.md            # CLI layer
├── 04_module_abstraction.md         # Module abstraction
├── 05_bilayer_integration.md        # Bilayer specs
├── 06_pipecraft_integration.md      # Pipecraft integration
├── 07_execution_model.md            # Execution model
├── 08_snakemake_backend.md          # Snakemake backend
├── 09_experiment_configuration.md   # Experiment configuration
├── 10_11_module_configuration.md    # Module configuration
├── 12_pipeline_composition_execution.md  # Pipeline composition
└── 13_architecture_for_biologists.md    # Biologist-focused overview
```

### Document Templates

Each document follows a consistent template:

1. **Title** - Component name
2. **Overview** - Brief introduction (1-2 paragraphs)
3. **Purpose** - Component's role in the architecture (bullet points)
4. **Implementation Details** - How the component works
5. **Examples** - Code examples demonstrating usage
6. **Integration** - How it connects with other components
7. **Conclusion** - Summary of key points

Key architectural principles are emphasized with "Critical Point" callouts.

### Audience-Specific Documents

For specialized audiences, additional considerations apply:

1. **Technical Level** - Adjust explanation depth based on audience expertise
2. **Terminology** - Use domain-appropriate language
3. **Focus** - Emphasize aspects most relevant to the specific audience
4. **Visuals** - Include diagrams that communicate effectively to the target audience

The document `13_architecture_for_biologists.md` is designed specifically for biologists with image analysis expertise, focusing on:
- How the architecture supports their scientific workflows
- GUI integration benefits
- Practical advantages for research workflows
- Comparison with previous systems they may have used (PCPIP)

## Documentation Standards

### Terminology Consistency

Throughout the documentation, these terminology standards are maintained:

- **Framework Components**:
  - Starry Night: Overall framework
  - Pipecraft: Library for pipeline creation
  - Bilayers: Schema system for specifications
  - Canvas: UI component
  - Conductor: Execution orchestration component

- **Pipeline Components**:
  - CP: Cell Painting (not CellProfiler)
  - CellProfiler: Image analysis platform (always written in full)
  - PCP: Plate Cell Painting
  - SBS: Sequencing By Synthesis

- **Technical Terms**:
  - ILLUM: Illumination
  - Mito: Mitochondrial
  - Segmentation check: Pipeline validation component

- **Technology Stack**:
  - Snakemake: Workflow management system
  - CLI: Command Line Interface
  - Docker/Singularity: Container technologies

### Code Examples

Code examples follow these standards:

1. **Fenced with triple backticks** with language specified:
   ```python
   # Python code example
   ```

2. **Realistic but simplified** - Show real patterns without unnecessary complexity

3. **Focused on concept** - Highlight the specific concept being discussed

4. **Complete context** - Include necessary imports and context for understanding

### Diagrams

Diagrams should follow these guidelines:

1. **Mermaid Format** - Use Mermaid.js syntax for diagrams where possible
2. **Clear Labels** - All diagram elements should have descriptive labels
3. **Appropriate Detail** - Include enough detail to be informative without overwhelming
4. **Consistent Style** - Use consistent visual style across diagrams
5. **Audience-Appropriate** - Adjust complexity based on the target audience

## MkDocs Integration

### Configuration

The documentation is integrated with MkDocs using the configuration in `mkdocs.yml`:

```yaml
site_name: Starry Night Documentation
# ... other configuration ...

nav:
  - Home: index.md
  - Architecture:
    - Overview: architecture/00_architecture_overview.md
    - Algorithm Foundation: architecture/01_algorithms_foundation.md
    # ... other architecture pages ...
    - Architecture for Biologists: architecture/13_architecture_for_biologists.md
  # ... other sections ...
```

### Theme

The documentation uses the Material for MkDocs theme, which provides:

- Clean, modern appearance
- Good code highlighting
- Mobile responsiveness
- Search functionality
- Navigation features

## Maintenance Guidelines

### Adding New Content

To add new documentation:

1. **Follow the template** - Use the established document template for consistency
2. **Maintain numbering** - Continue the existing numbering scheme (XX_component_name.md)
3. **Update mkdocs.yml** - Add the new document to the navigation structure
4. **Link to related sections** - Add cross-references to related documents

### Audience-Specific Content

When creating documentation for specific audiences:

1. **Understand the audience** - Consider their expertise level and domain knowledge
2. **Use appropriate terminology** - Adjust technical language to match audience expertise
3. **Focus on relevant aspects** - Emphasize components most relevant to that audience
4. **Provide appropriate context** - Explain connections to systems they already understand
5. **Number consistently** - Follow the established numbering scheme for integration

### Updating Existing Content

When updating documentation:

1. **Preserve critical points** - Maintain emphasis on key architectural principles
2. **Follow terminology standards** - Use consistent terminology
3. **Update example code** - If the API changes, update code examples
4. **Review cross-references** - Ensure cross-references remain valid

### Version Control

Documentation changes should follow these practices:

1. **Clear commit messages** - "doc: Update algorithm description in architecture docs"
2. **Logical grouping** - Group related documentation changes in a single commit
3. **Version tagging** - Consider tagging major documentation updates with versions

## Future Improvements

### Short-term Improvements

1. **Diagrams** - Add visual diagrams for:
   - System architecture overview
   - Module structure and relationships
   - Pipeline composition workflow
   - Execution flow from module to container

2. **API Documentation** - Create comprehensive API documentation for:
   - Algorithm functions
   - Module classes
   - Pipeline composition functions
   - Experiment configuration classes

3. **Interactive Examples** - Add executable code samples that demonstrate key concepts

4. **Additional Audience-Specific Guides** - Create guides for:
   - Developers new to the codebase
   - Operations teams deploying the system
   - End users of the GUI interface

### Long-term Improvements

1. **Versioned Documentation** - Implement version control for documentation to match software versions

2. **Search Optimization** - Improve search functionality with better keyword indexing

3. **User Guides** - Create step-by-step guides for common tasks:
   - Creating a new algorithm
   - Creating a new module
   - Creating a new experiment type
   - Running pipelines in different environments

4. **Video Tutorials** - Create video walkthroughs of key concepts

5. **Interactive Architecture Map** - Create an interactive visualization of the architecture

## Tools and References

### Documentation Tools

- **MkDocs** - [Documentation](https://www.mkdocs.org/)
- **Material for MkDocs** - [Documentation](https://squidfunk.github.io/mkdocs-material/)
- **PyMdown Extensions** - [Documentation](https://facelessuser.github.io/pymdown-extensions/)

### Diagram Tools

- **Mermaid.js** - [Documentation](https://mermaid-js.github.io/mermaid/#/) - Can be integrated with MkDocs
- **PlantUML** - [Documentation](https://plantuml.com/) - Good for UML diagrams
- **Draw.io** - [Website](https://app.diagrams.net/) - General purpose diagramming

### Style References

- **Google Developer Documentation Style Guide** - [Link](https://developers.google.com/style)
- **Microsoft Style Guide** - [Link](https://docs.microsoft.com/en-us/style-guide/welcome/)
- **Write the Docs** - [Link](https://www.writethedocs.org/guide/)

## Conclusion

This documentation guide provides a comprehensive overview of how the Starry Night architecture documentation was created and how to maintain it. By following these guidelines, the documentation can remain accurate, consistent, and useful as the software evolves.

The documentation was designed to emphasize the key architectural principles that make Starry Night powerful: algorithm independence, module abstraction with specs and compute graphs, and backend-agnostic execution. These principles should continue to be highlighted in future documentation updates.

Creating specialized versions for different audiences, like the biologist-focused overview, helps ensure that all stakeholders can understand the architecture at an appropriate level of detail for their needs.
