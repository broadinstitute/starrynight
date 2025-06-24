# StarryNight Architecture: End-to-End Flow Examples

!!! warning "Experimental - Not Reviewed"
    Content may be incomplete or inaccurate.

This document demonstrates how StarryNight's six architectural layers work together to accomplish real-world scientific workflows. Each example traces the complete path from user command to final results, showing how data and control flow through the system.

> **Note**: Code examples in this document illustrate patterns and concepts rather than exact implementations. Refer to the actual source files for current signatures and parameters.

## Example 1: Illumination Correction Workflow

This example shows how a researcher corrects illumination artifacts in microscopy images—a common preprocessing step required before analysis.

### User Command

```bash
starrynight illum calc loaddata [options]
```

This command prepares illumination correction data for a specific plate from an experiment index.

### Flow Through Layers

#### 1. CLI Layer Entry Point

**File**: `starrynight/src/starrynight/cli/illum.py`

The CLI layer receives the command and parses arguments. The pattern follows:

- Click decorators define command structure and options
- Arguments are converted to appropriate types (e.g., paths to AnyPath objects)
- Direct delegation to algorithm functions for business logic

#### 2. Algorithm Layer Processing

**File**: `starrynight/src/starrynight/algorithms/illum_calc.py`

The algorithm function performs the actual computation following this pattern:

- Read input data from specified paths
- Filter and transform data based on experiment parameters
- Utilize shared utilities for consistent data formatting
- Write results to specified output paths

#### 3. Module Layer Encapsulation

**File**: `starrynight/src/starrynight/modules/cp_illum_calc/` (module implementation)

The module layer wraps CLI functionality for pipeline use:

- Extends `StarrynightModule` base class (from `modules/common.py`)
- Defines container-based execution with appropriate image
- Maps pipeline parameters to CLI command arguments
- Provides specification for inputs and outputs

#### 4. Pipeline Layer Composition

**File**: `starrynight/src/starrynight/pipelines/pcp_generic.py`

The pipeline layer assembles modules into workflows using:

- Sequential (`Seq`) containers for dependent steps
- Parallel (`Parallel`) containers for independent operations
- Module references through a registry pattern (`modules/registry.py`)
- Named workflows for clarity and debugging

#### 5. Execution Layer Runtime

**Backend**: Pipecraft with Snakemake (`pipecraft/src/pipecraft/backend/snakemake.py`)

Execution patterns include:

- Backend configuration with resource specifications
- Container runtime selection (Docker/Singularity)
- Work directory management
- Asynchronous execution with status monitoring

#### 6. Configuration Layer Cross-Cutting

**Pattern**: Configuration flows orthogonally through all layers

Configuration provides:

- Experiment metadata (plates, channels, wells)
- Resource requirements (CPU, memory)
- Runtime parameters (paths, identifiers)
- Protocol-specific settings

### Result

The workflow produces:

- LoadData CSV files for CellProfiler
- Illumination correction functions for each channel
- Corrected images ready for analysis

## Example 2: Complete Cell Painting Pipeline

This example demonstrates a full Cell Painting analysis from raw images to extracted features.

### Pipeline Initialization

**File**: `starrynight/notebooks/pypct/exec_pcp_generic_pipe.py`

The initialization pattern involves:

- Creating data configuration with dataset and workspace paths
- Loading experiment configuration from index files
- Optional metadata enrichment (e.g., barcode mappings)

### Modular Pipeline Execution

#### Step 1: Generate Index

**Module**: `CPGenIndexModule` (from `modules/gen_index.py`)

The pattern for module parameterization:

- Instantiate module class
- Define parameter dictionary with required values
- Apply parameters to create configured module instance

#### Step 2: Parallel Preprocessing

The pipeline uses parallel execution for independent workflows:

**Pattern**: Parallel container with named sequences

- Cell Painting illumination correction sequence
- SBS (Sequencing by Synthesis) illumination correction sequence
- Each sequence contains ordered preprocessing steps
- Parallel execution maximizes resource utilization

#### Step 3: Sequential Analysis

After preprocessing completes, analysis runs sequentially:

**Pattern**: Sequential execution for dependent operations

- Generate analysis-specific LoadData files
- Create CellProfiler pipeline configuration
- Invoke CellProfiler for feature extraction

### Configuration Adaptation

The configuration layer adapts parameters for each experiment type:

**Cell Painting Configuration**:

- Maps biological targets to fluorescent channels
- Defines organelle-specific imaging parameters
- Supports multiple wavelengths per target

**SBS Configuration**:

- Maps sequencing cycles to detection channels
- Defines base-specific fluorophores
- Supports multi-cycle imaging protocols

### Execution Backend Translation

The backend translates abstract pipelines into executable workflows:

**Translation patterns**:

- Pipeline containers become workflow rules
- Module specifications define inputs/outputs
- Resource requirements map to cluster constraints
- Container definitions ensure reproducibility

## Example 3: Custom Algorithm Integration

This example shows how to add a new algorithm to StarryNight.

### Step 1: Implement Algorithm Function

**Location**: `starrynight/src/starrynight/algorithms/`

Algorithm implementation patterns:

- Accept `AnyPath` objects for file system abstraction
- Separate parameter generation from execution
- Use type hints for clarity
- Leverage utilities for common operations (`utils/`)
- Write outputs to specified paths

### Step 2: Create CLI Wrapper

**Location**: `starrynight/src/starrynight/cli/`

CLI patterns:

- Use Click groups for related commands (see `cli/main.py`)
- Define clear option names with short forms
- Convert string paths to `AnyPath` objects
- Delegate to algorithm functions
- Keep CLI logic minimal

### Step 3: Create Module

**Location**: `starrynight/src/starrynight/modules/`

Module patterns:

- Extend `StarrynightModule` base class (from `modules/common.py`)
- Define input/output specifications
- Create pipeline with container sequences (using pipecraft)
- Reference CLI commands in containers
- Use parameter substitution with `$` prefix

### Step 4: Integration in Pipeline

**Location**: `starrynight/src/starrynight/pipelines/`

Integration patterns:

- Insert new modules into existing workflows
- Maintain clear sequential or parallel relationships
- Use descriptive names for pipeline sections
- Consider data dependencies between modules
- Register in pipeline registry (`pipelines/registry.py`)

## Key Architectural Patterns

These examples demonstrate several key patterns:

1. **Layer Independence**: Each layer has clear responsibilities and interfaces
2. **Bottom-Up Data Flow**: Algorithms → CLI → Modules → Pipelines → Execution
3. **Cross-Cutting Configuration**: Parameters flow orthogonally through all layers
4. **Container Isolation**: All computation happens in reproducible containers
5. **Backend Abstraction**: Same pipeline runs on different infrastructure

## Summary

StarryNight's architecture enables:

- **Modularity**: Add new algorithms without changing the framework
- **Reusability**: Compose existing modules into new pipelines
- **Portability**: Run anywhere from laptops to cloud clusters
- **Reproducibility**: Container-based execution ensures consistent results
- **Flexibility**: Adapt to different experimental protocols through configuration

The layered design separates concerns while maintaining cohesion, allowing researchers to focus on science while the framework handles infrastructure complexity.
