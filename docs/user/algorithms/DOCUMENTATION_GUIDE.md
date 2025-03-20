# Algorithm Documentation Guide

This guide provides detailed instructions for documenting algorithms in the StarryNight project. Following these guidelines ensures consistency and thoroughness across all algorithm documentation.

## Understanding the CellProfiler-Based Architecture

Before documenting a StarryNight algorithm, it's essential to understand the core architectural pattern:

StarryNight uses a **three-tier architecture** built around CellProfiler:

1. **Load Data Generation**: Python code that prepares CSV files describing which images to process
2. **Pipeline Generation**: Python code that programmatically constructs CellProfiler pipelines
3. **Pipeline Execution**: Running the generated pipelines with CellProfiler (handled by separate mechanisms)

This means that StarryNight's "algorithms" are primarily pipeline generators, not direct image processing implementations. The actual image processing happens inside CellProfiler.

## Documentation Structure

Each algorithm should be documented using the following structure:

### 1. Title and Overview

```markdown
# Algorithm Name (file.py) - Technical Documentation

This document provides a detailed explanation of the [algorithm name] implementation in the StarryNight project.

## Overview

The `[file.py]` module implements [brief description of what the algorithm does and its purpose].

The module follows StarryNight's standard three-tier architecture:
1. Load data generation
2. CellProfiler pipeline generation
3. Pipeline execution (handled elsewhere)
```

The overview should clearly state:
- What problem the algorithm solves
- Where it fits in the overall workflow
- That it generates CellProfiler pipelines rather than implementing processing directly

### 2. Dependencies

```markdown
## Dependencies

The module relies on several key libraries:
- **CellProfiler**: Core image processing functionality through modules like [list key CP modules]
- **[Other Library]**: [Description of functionality provided]
```

Always list CellProfiler first, with specific modules it uses. This emphasizes the CellProfiler foundation.

### 3. Key Components

```markdown
## Key Components

### 1. Load Data Generation

#### Main Functions
- `function1`: [Description]
- `main_entry_function`: Main entry point for load data generation

#### Data Organization
- [Describe how data is organized]

### 2. CellProfiler Pipeline Generation

#### Main Functions
- `function1`: [Description]
- `main_entry_function`: Main entry point for pipeline generation

#### Pipeline Structure
[Describe the CellProfiler pipeline structure created by this algorithm]
1. **[CP Module Name]**: [What it does]
2. **[CP Module Name]**: [What it does]
```

For each CellProfiler module:
- Name the specific module (e.g., CorrectIlluminationCalculate)
- Explain how it's configured in this particular algorithm
- List key parameters that affect its behavior

### 4. Technical Details

```markdown
### Technical Details

#### Key Parameters
- Parameter 1: [Value and meaning]
- Parameter 2: [Value and meaning]

#### File Naming and Organization
- [Explain file naming conventions]

#### Special Considerations
- [Describe any special cases]
```

### 5. Workflow

```markdown
## Workflow

1. **Step 1**:
   - [Detail what happens]

2. **Step 2**:
   - [Detail what happens]
```

Include a complete workflow from data input to output, emphasizing the transitions between:
- Data preparation
- Load data generation
- Pipeline generation
- What happens during execution

### 6. Resources and Implementation Notes

```markdown
## Key Classes and Resources
- **Class/Resource 1**: [Description]

## Technical Implementation Notes
1. **Note 1**:
   - [Detailed explanation]
```

### 7. Conclusion

```markdown
## Conclusion

The [algorithm name] module provides [summary of what it accomplishes]. By leveraging CellProfiler's [specific capabilities], it enables [key capabilities] in the StarryNight platform.
```

Always emphasize the CellProfiler foundation in the conclusion.

## Documentation Best Practices

1. **Be Specific About CellProfiler Usage**
   - Name the exact CellProfiler modules used
   - Describe module parameters and their effects
   - Explain how StarryNight configures these modules programmatically

2. **Include Concrete Examples**
   - Show example CSV structure for LoadData
   - Provide example pipeline snippets for key CellProfiler configurations
   - Demonstrate file naming patterns

3. **Emphasize the Generation Pattern**
   - Clarify that StarryNight generates the pipelines rather than implementing processing
   - Explain how the generation code adapts to different data organizations

4. **Document Both Tiers**
   - Load data generation: How StarryNight organizes image data for CellProfiler
   - Pipeline generation: How StarryNight configures CellProfiler to process that data

5. **Clarify Special Cases**
   - SBS vs. non-SBS images
   - Batch/plate/cycle organization
   - Error handling and fallbacks

## Review Checklist

Before submitting new algorithm documentation, verify that it:

- [ ] Clearly states the algorithm uses CellProfiler for actual processing
- [ ] Lists all CellProfiler modules used by the algorithm
- [ ] Explains how each module is configured and connected
- [ ] Documents the three-tier architecture implementation
- [ ] Provides concrete examples of inputs and outputs
- [ ] Describes the end-to-end workflow

## Template

Use the [documentation-template.md](documentation-template.md) file as a starting point for new algorithm documentation.
