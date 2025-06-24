# Execution Layer

!!! warning "Experimental - Not Reviewed"
    Content may be incomplete or inaccurate.

## Purpose

The Execution Layer manages the actual runtime execution of StarryNight pipelines on computational infrastructure. This layer is primarily implemented within the Pipecraft package and orchestrated by the Conductor service, solving the critical problem of translating abstract workflow definitions into concrete executions across diverse environments—from local workstations to cloud platforms. By abstracting backend-specific details through Pipecraft's backend system, the Execution Layer enables researchers to focus on scientific workflows rather than infrastructure management, while maintaining the flexibility to leverage different computational resources as needed.

## Responsibilities

- Translate Pipecraft graphs into backend-specific execution plans
- Manage container-based execution for reproducibility
- Handle resource allocation, parallelization, and failure recovery
- NOT responsible for: Defining workflows, implementing algorithms, composing modules, or making scientific decisions

## Key Design Decisions

1.  **Backend Abstraction (Decision #10)**: The execution functionality is provided through Pipecraft's backend system `pipecraft/src/pipecraft/backend/`, offering a uniform interface to multiple execution backends. Currently implemented backends include Snakemake (fully functional) and AWS Batch (partial implementation), with extensibility for others. This abstraction ensures that pipeline definitions remain portable and that infrastructure choices can evolve without impacting scientific workflows. The translation from Pipecraft graphs to backend-specific formats happens within Pipecraft's backend implementations.

2.  **Container-Based Execution (Decision #6)**: All computational work executes within containers (Docker/Singularity/Apptainer) to ensure reproducibility across environments. This decision addresses the critical challenge of scientific reproducibility by guaranteeing that analyses produce identical results regardless of the host system. Container specifications are managed at the module level but orchestrated by the Execution Layer.

## Interfaces

### Inputs

- Pipecraft compute graphs from the Pipeline Layer
- Execution configuration (backend selection, resource limits)
- Runtime parameters (parallelism settings, retry policies)

### Outputs

- Execution status and progress information
- Workflow artifacts as defined by pipeline outputs
- Execution logs and metrics for debugging

### Dependencies

- Internal dependencies: Pipeline Layer for workflow definitions (following upward-only rule)
- External dependencies: Workflow orchestrators (e.g., Snakemake), container runtimes

## Patterns

The Execution Layer follows a standard pattern for backend abstraction and pipeline execution:

### Backend Pattern

Each backend implementation `pipecraft/src/pipecraft/backend/` follows this structure:

- Inherits from a base Backend class that defines the interface
- Implements `compile()` to translate Pipecraft graphs to backend-specific formats
- Implements `run()` to execute the compiled workflow
- Returns a run object for monitoring and log access

### Execution Flow Pattern

The Execution Layer follows a four-phase pattern for translating abstract pipelines into concrete executions:

1.  **Backend Selection**: The system instantiates the appropriate backend based on configuration, with each backend providing a uniform interface despite different underlying orchestrators.

2.  **Pipeline Compilation**: Backends translate Pipecraft graphs into their native formats by iterating through pipeline nodes and generating backend-specific execution instructions.

3.  **Execution Management**: The backend configures the runtime environment, manages resource allocation, and launches workflows with appropriate parameters.

4.  **Monitoring and Control**: Standardized run objects provide interfaces for checking execution status, accessing logs, and controlling running workflows.

### Integration Pattern

The Conductor service `conductor/src/conductor/handlers/execute.py` orchestrates execution:

1. Creates data configuration from project/job settings
2. Instantiates the appropriate module or pipeline
3. Creates a backend instance with the compiled pipeline
4. Executes and tracks the run in the database
5. Provides status updates through the API

### Configuration Pattern

Execution configuration typically includes:

- Resource limits (cores, memory, time)
- Container platform selection
- Retry and failure handling policies
- Output and scratch directory paths
- Backend-specific options

This pattern-based approach ensures that new backends can be added without modifying existing code, and that execution details can evolve without breaking the abstraction.

## Implementation Location

- Primary location: `pipecraft/src/pipecraft/backend/`
- Secondary location: `conductor/src/conductor/handlers/execute.py`
- Tests: `pipecraft/tests/backend/`

## See Also

- Previous: [Pipeline Layer](04-pipeline.md), Next: [Configuration Layer](06-configuration.md)
