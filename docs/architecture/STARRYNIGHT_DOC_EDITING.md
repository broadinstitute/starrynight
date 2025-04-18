# StarryNight Documentation Guide

## Architecture Layers
1. **00_architecture_overview.md** - Architecture overview with package structure
2. **01_algorithm_layer.md** - Pure Python functions foundation
3. **02_cli_layer.md** - Command-line wrappers
4. **03_module_layer.md** - Module abstraction (specs + compute graphs)
5. **04_pipeline_layer.md** - Module composition with Pipecraft
6. **05_execution_layer.md** - Execution backends (Snakemake)
7. **06_configuration_layer.md** - Parameter inference
8. **07_architecture_for_biologists.md** - Biologist-focused overview

## Key Reference Materials
- **Original Content**: `./transcripts/` - Interview transcripts that informed documentation
- **Previous Versions**: `./_archive/` - Original component-based documents
- **Source Code**:
  - Algorithms: `../../starrynight/src/starrynight/algorithms/`
  - CLI: `../../starrynight/src/starrynight/cli/`
  - Modules: `../../starrynight/src/starrynight/modules/`
  - Pipecraft: `../../pipecraft/src/pipecraft/`

## Document Structure Requirements
- **Section Hierarchy**: Overview → Purpose → Implementation → Examples
- **Header Levels**: # Title, ## Main sections, ### Subsections (max 3 levels)
- **Code Blocks**: Use language-specific formatting (```python)
- **Cross-References**: Link to adjacent layers and dependencies
- **Progressive Disclosure**: Introduce concepts before detailed explanation

## Terminology Registry
1. **Framework Components**
   - StarryNight: Overall framework (not Starrynight)
   - Pipecraft: Pipeline creation library
   - Bilayers: Schema layer for specifications
   - Canvas: UI component
   - Conductor: Execution orchestration

2. **Technical Terms**
   - Algorithm set: Function group implementing pipeline step
   - Module: Wrapper with spec and compute graph
   - Compute Graph: Operations and relationships definition
   - Container: Isolated execution environment
   - Snakemake: Workflow engine executing compiled pipelines

## Key Architectural Principles
- **Algorithm Independence** - Pure functions with no dependencies
- **Module Dual Focus** - Specs (using Bilayers) + compute graphs
- **Package Separation** - Pipeline definition in PipeCraft separate from algorithms
- **Backend-agnostic Execution** - Pipeline definition separate from execution
- **Automated Generation** - Complex workflows from simple definitions

## Editing Process
1. **Context Assessment**
   - Review adjacent documents (N-1 and N+1 in sequence)
   - Check source code for implementation details
   - Refer to transcripts for original intent

2. **Content Improvement**
   - Replace transcript quotes with formal explanations
   - Verify code examples against implementation
   - Ensure consistent terminology
   - Add concrete examples from actual code
   - Clarify layer-specific responsibilities
   - Strengthen connections between layers

3. **Document-Specific Focus**
   - **04_pipeline_layer.md**: PipeCraft integration, module connections
   - **05_execution_layer.md**: Snakemake backend implementation details
   - **06_configuration_layer.md**: Parameter inference system
   - **07_architecture_for_biologists.md**: Biologist-friendly terminology

## Verification Checklist
- [ ] Confirmed terminology with Terminology Registry
- [ ] Verified code examples against actual implementation
- [ ] Checked command structures and function names
- [ ] Validated connections to adjacent architectural layers
- [ ] Replaced transcript quotes with formal explanations
- [ ] Ensured consistent structure (Overview → Purpose → Implementation → Examples)

## Audience-Specific Guidance
- **Biologist-Focused Content**: Minimize jargon, use biological analogies, focus on workflows
- **Developer-Focused Content**: Include implementation details, explain architectural decisions
- **Technical Depth Scale**: Basic (concepts) → Intermediate (patterns) → Advanced (details)
