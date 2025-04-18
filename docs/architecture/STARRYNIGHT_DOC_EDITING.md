# StarryNight Documentation Editing Manual

## Document Analysis Phase
1. **Architecture Context Assessment**
   - Identify document's position in architecture layer stack
   - Examine adjacent layers (document before and after)
   - Review CLAUDE_NOTES.md for relevant terminology and concepts
   - **Reference check**: Review 00_architecture_overview.md to understand overall structure

2. **Content Evaluation**
   - Identify direct quotes that need replacement with formal content
   - Check for outdated terminology or structure
   - Note sections that lack concrete examples
   - Identify hypothetical examples that should be replaced with real ones

3. **Code Verification**
   - Examine actual code in `/Users/shsingh/Documents/GitHub/starrynight/starrynight/src/`
   - For CLI documents: verify in `/starrynight/src/starrynight/cli/`
   - For algorithm documents: verify in `/starrynight/src/starrynight/algorithms/`
   - For module documents: verify in `/starrynight/src/starrynight/modules/`
   - For PipeCraft documents: verify in `/pipecraft/src/pipecraft/`
   - Verify examples, command structures, function names against actual implementation
   - Check transcripts in `/docs/architecture/transcripts/` for original context

## Critical Reference Materials
1. **Core Architecture Documents**
   - CLAUDE_NOTES.md - Essential terminology and structure reference
   - _archive/ versions - Check original document versions for context
   - transcripts/ - Original transcripts that informed documentation

2. **Implementation Code**
   - For each document, identify the corresponding code folders:
     - 01_algorithm_layer.md → `/starrynight/src/starrynight/algorithms/`
     - 02_cli_layer.md → `/starrynight/src/starrynight/cli/`
     - 03_module_system.md → `/starrynight/src/starrynight/modules/`
     - 04_pipeline_construction.md → `/pipecraft/`
     - 05_execution_system.md → Snakemake related files
     - 06_experiment_configuration.md → Configuration related files

3. **Adjacent Documents**
   - Always check N-1 and N+1 documents in the sequence
   - Ensure terminology consistency between documents
   - Maintain logical flow between layers

## Focused Editing Strategy
1. **Structural Improvements**
   - Maintain consistent section hierarchy
   - Ensure logical flow from overview → purpose → implementation → examples
   - Preserve document length while improving clarity

2. **Content Accuracy**
   - Replace transcript quotes with formal explanations
   - Update code examples to match actual implementation
   - Correct command/function names and parameters
   - Clarify layer-specific responsibilities

3. **Architecture Context**
   - Strengthen connection to adjacent layers
   - Clarify layer position in overview and conclusion sections
   - Use consistent terminology from CLAUDE_NOTES.md

4. **Example Enhancement**
   - Use concrete, verified examples from actual code
   - Include realistic usage scenarios
   - Show proper syntax and expected outputs

## Document-Specific Considerations
- **04_pipeline_construction.md**: Focus on PipeCraft integration, verify module connections
- **05_execution_system.md**: Verify Snakemake backend implementation details
- **06_experiment_configuration.md**: Check parameter inference system implementation
- **07_architecture_for_biologists.md**: Ensure biologist-friendly terminology and examples

## Verification Checklist
- [ ] Confirmed terminology with CLAUDE_NOTES.md
- [ ] Verified code examples against actual implementation
- [ ] Checked command structures and function names
- [ ] Validated connections to adjacent architectural layers
- [ ] Replaced all transcript quotes with formal explanations
- [ ] Ensured consistent formatting and structure
- [ ] Verified accuracy of diagrams and illustrations

## Lessons from 02_cli_layer.md Editing
1. **Command Structure Verification**: The command hierarchy diagram needed verification against actual CLI implementation in `main.py` and individual command files.
2. **Path Handling Clarification**: Needed to understand the boundary responsibilities between CLI and algorithm layers.
3. **Quote Replacement**: All direct transcript quotes needed replacement with formal documentation language.
4. **Example Accuracy**: CLI usage examples needed updating to match actual command names and parameters.
5. **Terminology Precision**: Terms like "algorithm sets" required clarification from other documentation.
6. **Layer Positioning**: Conclusion needed to clearly position this layer between algorithm and module layers.

## Additional Important Considerations

1. **Incremental Editing**: Make focused, targeted changes rather than complete rewrites. This preserves the original structure while improving accuracy.

2. **Visual Diagrams**: When editing diagrams or flowcharts, ensure they accurately represent the architecture while remaining simple enough to understand.

3. **Technical Debt Identification**: Note areas where documentation and implementation diverge significantly, but focus on accuracy rather than major restructuring.

4. **Cross-Package Boundaries**: Pay special attention to where components cross package boundaries (e.g., StarryNight to PipeCraft) as these interfaces are critical.

5. **Terminology Consistency**: Maintain a consistent set of terms across all documents:
   - StarryNight vs Starrynight (capitalization)
   - CellProfiler (not Cell Profiler or CP)
   - algorithm sets vs modules vs pipelines

6. **Audience Awareness**: Remember that documents have different audiences - keep 07_architecture_for_biologists.md accessible while maintaining technical accuracy in other documents.

7. **Documentation as Code**: Treat documentation with the same rigor as code, ensuring accuracy, consistency, and proper formatting throughout.

This manual will help systematically improve each document while maintaining consistency across the architecture documentation suite.
