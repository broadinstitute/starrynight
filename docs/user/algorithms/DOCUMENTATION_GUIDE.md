# Algorithm Documentation Guide

This guide provides instructions for documenting algorithms in the StarryNight project. Following these guidelines ensures consistency while being concise and developer-friendly.

## Core Documentation Principles

1. **Be concise**: Developers can read code. Focus on explaining "why" not "how".
2. **Emphasize unique aspects**: Document what makes each algorithm special, not what's common.
3. **Focus on architecture decisions**: Explain key design choices and their rationale.
4. **Include non-obvious information**: Document things that aren't immediately clear from the code.

## Understanding the CellProfiler-Based Architecture

Most StarryNight algorithms follow a common pattern:

1. **Load Data Generation**: Python code that prepares CSVs for CellProfiler's LoadData module
2. **Pipeline Generation**: Python code that programmatically constructs CellProfiler pipelines
3. **Pipeline Execution**: Handled elsewhere

This pattern doesn't need to be extensively documented in each algorithm file. Focus on what's unique.

## Documentation Sections

### 1. Title and Overview

```markdown
# Algorithm Name (file.py)

Brief explanation of what this algorithm does and its purpose within StarryNight.
```

Keep the overview to 2-3 sentences. Focus on:
- What problem the algorithm solves
- Where it fits in the overall workflow

### 2. Key Components and Special Features

```markdown
## Key Components

- **Unique Feature A**: Brief explanation of what makes this feature special
- **Unique Feature B**: Brief explanation of what makes this feature special

### CellProfiler Configuration

Key CellProfiler modules and configurations:
- **ModuleA**: Configured with X parameters for Y purpose
- **ModuleB**: Configured with X parameters for Y purpose
```

Focus on what's unique to this algorithm, not what's common across all algorithms.

### 3. Technical Implementation Notes

```markdown
## Implementation Notes

- **Special case handling**: How this algorithm handles X edge case
- **Performance considerations**: Any optimizations or considerations
- **Key parameters**: Only the non-obvious or critical parameters
```

Include information that would help a developer understand non-obvious aspects of the implementation.

## Documentation Best Practices

1. **Be specific about differences**
      - Highlight what makes this algorithm unique
      - Don't repeat architectural patterns common to all algorithms
2. **Include only non-obvious examples**
      - Show examples only for complex or unusual configurations
      - Skip examples for standard patterns
3. **Focus on design decisions and trade-offs**
      - Explain why certain approaches were chosen
      - Document alternative approaches that were considered
4. **Document edge cases and limitations**
      - Note known limitations or constraints
      - Document special case handling

## Template

Use the [documentation-template.md](documentation-template.md) file as a starting point for new algorithm documentation.
