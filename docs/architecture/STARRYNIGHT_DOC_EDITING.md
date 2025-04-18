# StarryNight Documentation Guide

This document combines essential guidance for understanding and editing StarryNight documentation.

## Project Structure
- StarryNight is a monorepo with four main packages:
  1. **StarryNight** (core) - Algorithms, CLI, Module system
  2. **PipeCraft** - Pipeline construction, execution backends
  3. **Conductor** - Job orchestration (minimally documented)
  4. **Canvas** - User interface (minimally documented)

## Architecture Layers
1. **00_architecture_overview.md** - Complete system overview with package structure
2. **01_algorithm_layer.md** - Foundation with pure Python functions
3. **02_cli_layer.md** - Command-line wrappers
4. **03_module_system.md** - Module abstraction (specs + compute graphs)
5. **04_pipeline_construction.md** - Module composition with Pipecraft
6. **05_execution_system.md** - Execution backends (Snakemake)
7. **06_experiment_configuration.md** - Parameter inference
8. **07_architecture_for_biologists.md** - Biologist-focused overview

## Key Architectural Principles
- **Algorithm Independence** - Pure functions with no dependencies on other components
- **Module Dual Focus** - Specs (using Bilayers) + compute graphs
- **Package Separation** - Pipeline definition in PipeCraft separate from algorithms
- **Backend-agnostic Execution** - Pipeline definition separate from execution
- **Automated Generation** - Complex workflows from simple definitions

## Document Origin
1. **Creation Background**
   - Documents created from transcripts of discussions/interviews found in `./transcripts/`
   - Originally granular component-focused documents restructured into layer-based documents
   - Original versions preserved in `./_archive/` directory as reference
   - Documentation designed for progressive disclosure (overview → concepts → details)

2. **Documentation Structure**
   - Architecture documentation follows layered approach mirroring the system's layers
   - Files are numbered 00-07 to represent sequential layers in the architecture
   - Documents follow a consistent section structure: Overview → Purpose → Implementation → Examples
   - Special adaptations exist for specific audiences (e.g., biologist-focused documentation)

3. **Restructuring Context**
   - Original component-specific files consolidated into layer-based documents
   - Layer-based approach provides more coherent view of the architecture
   - Each document designed to be read in sequence from bottom layer to top
   - Documents are designed with cross-references to maintain a cohesive narrative

## Documentation Standards
1. **Structural Requirements**
   - Each document must follow this section hierarchy: Overview → Purpose → Implementation → Examples
   - Headers use consistent level structure (# for title, ## for main sections, ### for subsections)
   - Code blocks must use language-specific formatting with triple backticks: ```python
   - Related information grouped together logically within sections
   - Maximum of three levels of nesting (###) within a document
   - Important information presented using annotations `{ .annotate }` rather than callouts
   - Documentation scope/limitations stated upfront

2. **Code Example Standards**
   - All examples must be verified against actual implementation
   - Code blocks must include language identifiers (```python, ```bash)
   - Examples should include necessary imports and context
   - Simplify examples to highlight the specific concept being discussed
   - For CLI examples, use realistic file paths and command structures

3. **Diagram Guidelines**
   - Use Mermaid.js syntax for diagrams where possible
   - Ensure all diagram elements have descriptive labels
   - Balance detail with clarity - include enough detail to be informative
   - Maintain consistent visual style across all diagrams
   - Adjust complexity based on target audience

4. **Cross-Reference Format**
   - Internal document references: "[Section Title](#section-id)"
   - References to other documents: "[Document Title](../path/to/document.md)"
   - API references: "`PackageName.ModuleName.ClassName.method_name`"
   - Code file references: "`/path/to/file.py`"

## Terminology Registry
Maintain consistent terminology across all documents:

1. **Framework Components**
   - StarryNight: Overall framework (not Starrynight)
   - Pipecraft: Library for pipeline creation
   - Bilayers: Schema system for specifications
   - Canvas: UI component
   - Conductor: Execution orchestration component

2. **Pipeline Components**
   - CP: Cell Painting (not CellProfiler)
   - CellProfiler: Image analysis platform (always written in full)
   - PCP: Plate Cell Painting
   - SBS: Sequencing By Synthesis

3. **Technical Terms**
   - ILLUM: Illumination
   - Mito: Mitochondrial
   - Segmentation check: Pipeline validation component
   - Algorithm set: Function group implementing specific pipeline step
   - Module: Wrapper with spec and compute graph
   - Compute Graph: Operations and relationships definition
   - Container: Isolated execution environment
   - Snakemake: Workflow engine executing compiled pipelines
   - Bilayers: Schema system for module I/O
   - Pipecraft: Library for composable pipeline graphs

4. **Technology Stack**
   - Snakemake: Workflow management system
   - CLI: Command Line Interface
   - Docker/Singularity: Container technologies

## Related Code Paths
- `../../starrynight/src/`
- `../../pipecraft/src/`
- `../../conductor/src/`
- `../../canvas/src/`

## Document Analysis Phase
1. **Architecture Context Assessment**
   - Identify document's position in architecture layer stack
   - Examine adjacent layers (document before and after)
   - Review this guide for relevant terminology and concepts
   - **Reference check**: Review 00_architecture_overview.md to understand overall structure

2. **Content Evaluation**
   - Identify direct quotes that need replacement with formal content
   - Check for outdated terminology or structure
   - Note sections that lack concrete examples
   - Identify hypothetical examples that should be replaced with real ones
   - **Redundancy check**: Identify overlapping content between sections

3. **Code Verification**
   - Examine starrynight core code in `../../starrynight/src/`
     - For CLI documents: verify in `../../starrynight/src/starrynight/cli/`
     - For algorithm documents: verify in `../../starrynight/src/starrynight/algorithms/`
     - For module documents: verify in `../../starrynight/src/starrynight/modules/`
   - For PipeCraft documents: verify in `../../pipecraft/src/pipecraft/`
   - Verify examples, command structures, function names against actual implementation
   - Check transcripts in `./transcripts/` for original context

## Critical Reference Materials
1. **Core Architecture Documents**
   - This guide - Essential terminology and structure reference
   - `./_archive/` versions - Check original document versions for context
   - `./transcripts/` - Original transcripts that informed documentation
   - `./_archive/_documentation_guide.md` - Creation methozdology and standards

2. **Implementation Code**
   - For each document, identify the corresponding code folders:
     - 01_algorithm_layer.md → `../../starrynight/src/starrynight/algorithms/`
     - 02_cli_layer.md → `../../starrynight/src/starrynight/cli/`
     - 03_module_system.md → `../../starrynight/src/starrynight/modules/`
     - 04_pipeline_construction.md → `../../pipecraft/`
     - 05_execution_system.md → Snakemake related files
     - 06_experiment_configuration.md → Configuration related files

3. **Adjacent Documents**
   - Always check N-1 and N+1 documents in the sequence
   - Ensure terminology consistency between documents
   - Maintain logical flow between layers
   - **Dependency mapping**: Identify concepts introduced in earlier documents that later documents depend on

## Audience Adaptation Guidelines
1. **Biologist-Focused Content**
   - Minimize technical jargon or explain it clearly
   - Use biological analogies and examples
   - Focus on scientific workflows and results
   - Emphasize GUI and user experience
   - Compare with familiar systems (PCPIP)

2. **Developer-Focused Content**
   - Include implementation details and code examples
   - Explain architectural decisions and patterns
   - Focus on API design and integration points
   - Provide technical depth on algorithms and methods

3. **Technical Level Indicators**
   - Basic: Concept introduction with minimal technical detail
   - Intermediate: Implementation patterns with some code examples
   - Advanced: Detailed technical explanations with complete code

## Focused Editing Strategy
1. **Structural Improvements**
   - Maintain consistent section hierarchy
   - Ensure logical flow from overview → purpose → implementation → examples
   - Preserve document length while improving clarity
   - **Section balance**: Ensure appropriate emphasis on each concept based on its importance

2. **Content Accuracy**
   - Replace transcript quotes with formal explanations
   - Update code examples to match actual implementation
   - Correct command/function names and parameters
   - Clarify layer-specific responsibilities
   - **Technical precision**: Verify class names and technical details against implementation

3. **Architecture Context**
   - Strengthen connection to adjacent layers
   - Clarify layer position in overview and conclusion sections
   - Use consistent terminology from the Terminology Registry
   - **Progressive disclosure**: Avoid introducing concepts before they are explained

4. **Example Enhancement**
   - Use concrete, verified examples from actual code
   - Include realistic usage scenarios
   - Show proper syntax and expected outputs

5. **Technical Simplification**
   - Break down complex concepts into simpler components
   - Use analogies and visual aids for difficult concepts
   - Balance technical accuracy with accessibility
   - Avoid jargon that hasn't been previously introduced

6. **Redundancy Management**
   - Consolidate overlapping sections that repeat the same concepts
   - Ensure each section has a distinct purpose and unique content
   - Replace repetitive explanations with references to previous sections

## Document-Specific Considerations
- **04_pipeline_construction.md**: Focus on PipeCraft integration, verify module connections
- **05_execution_system.md**: Verify Snakemake backend implementation details
- **06_experiment_configuration.md**: Check parameter inference system implementation
- **07_architecture_for_biologists.md**: Ensure biologist-friendly terminology and examples

## Verification Checklist
- [ ] Confirmed terminology with Terminology Registry
- [ ] Verified code examples against actual implementation
- [ ] Checked command structures and function names
- [ ] Validated connections to adjacent architectural layers
- [ ] Replaced all transcript quotes with formal explanations
- [ ] Ensured consistent formatting and structure
- [ ] Verified accuracy of diagrams and illustrations

## General Editing Principles
1. **Incremental Editing**: Make focused, targeted changes rather than complete rewrites. This preserves the original structure while improving accuracy.

2. **Visual Diagrams**: When editing diagrams or flowcharts, ensure they accurately represent the architecture while remaining simple enough to understand.

3. **Technical Debt Identification**: Note areas where documentation and implementation diverge significantly, but focus on accuracy rather than major restructuring.

4. **Cross-Package Boundaries**: Pay special attention to where components cross package boundaries (e.g., StarryNight to PipeCraft) as these interfaces are critical.

5. **Terminology Consistency**: Use terms defined in the Terminology Registry consistently.

6. **Audience Awareness**: Remember that documents have different audiences - keep 07_architecture_for_biologists.md accessible while maintaining technical accuracy in other documents.

7. **Documentation as Code**: Treat documentation with the same rigor as code, ensuring accuracy, consistency, and proper formatting throughout.

8. **Conceptual Scaling**: Adjust technical depth based on the document's purpose and audience:
   - Technical documents: Include implementation details with code examples
   - Overview documents: Focus on architectural patterns and design decisions
   - User-facing documents: Emphasize practical applications over implementation

9. **Analogy Development**: When explaining complex technical concepts:
   - Choose analogies from domains familiar to the target audience
   - Ensure the analogy captures the essential relationships between components
   - Avoid analogies that break down when extended to the full system

10. **External Dependencies Explanation**:
    - Explain third-party tools (Bilayers, Pipecraft) in terms of their role in the architecture
    - Focus on integration points rather than detailed tutorials
    - Include just enough detail for comprehension without overwhelming

## Document-Specific Editing Strategies

### For Module System Documents
1. **Dual-Nature Explanation**: Explain modules as both specification containers and compute graph generators
2. **Implementation Examples**: Include concrete code examples showing both aspects
3. **External Tool Integration**: Clarify how Bilayers and Pipecraft fit into the module system
4. **Architecture Placement**: Emphasize the module system's role as bridge between CLI commands and pipeline execution
5. **Conceptual Hierarchy**: Establish clear relationships between related concepts (modules vs module specs vs module instances)

### For Architecture Overview Documents
1. **Layer Separation**: Maintain clear boundaries between architectural layers
2. **Responsibility Assignment**: Clarify which layer handles which concerns
3. **Information Flow**: Illustrate how data and control flow through the system
4. **Design Rationale**: Explain architectural decisions without repeating across sections
5. **Simplification Strategy**: Use progressive disclosure and analogies for complex concepts

## Lessons from Document Editing

### 02_cli_layer.md Insights
1. **Command Structure Verification**: The command hierarchy diagram needed verification against actual CLI implementation in `main.py` and individual command files.
2. **Path Handling Clarification**: Needed to understand the boundary responsibilities between CLI and algorithm layers.
3. **Quote Replacement**: All direct transcript quotes needed replacement with formal documentation language.
4. **Example Accuracy**: CLI usage examples needed updating to match actual command names and parameters.
5. **Terminology Precision**: Terms like "algorithm sets" required clarification from other documentation.
6. **Layer Positioning**: Conclusion needed to clearly position this layer between algorithm and module layers.

### 03_module_system.md Insights
1. **Dual-Nature Clarification**: The module concept required careful explanation of its dual nature (spec + compute graph).
2. **Technical Precision**: Class names like "CPSegcheckGenCPPipeModule" needed verification against actual code.
3. **External Dependencies**: Bilayers and Pipecraft required concise explanation while avoiding detailed tutorials.
4. **Redundancy Reduction**: Multiple sections repeating architectural advantages needed consolidation.
5. **Progressive Disclosure**: Complex concepts like Bilayers needed introduction before detailed explanation.
6. **Section Balance**: Certain concepts received disproportionate focus relative to their importance.
7. **Narrative Flow**: Maintaining clear transitions between sections required careful attention to logical progression.
