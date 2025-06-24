# Configuration Layer

!!! warning "Experimental - Not Reviewed"
    Content may be incomplete or inaccurate.

## Purpose

The Configuration Layer provides experiment-specific parameters and intelligent defaults across all StarryNight components, solving the problem of adapting generic image processing workflows to specific experimental contexts. Unlike other layers that follow a strict vertical hierarchy, the Configuration Layer operates orthogonally, influencing behavior at every level from algorithm parameters to execution resources. By combining automated parameter inference with explicit configuration options, this layer minimizes manual setup while maintaining full control when needed.

## Responsibilities

- Infer processing parameters from experimental data and metadata
- Provide experiment-specific adaptations across all layers
- Generate module configurations based on data characteristics
- NOT responsible for: Implementing algorithms, executing workflows, managing infrastructure, or enforcing layer boundaries

## Key Design Decisions

1.  **Cross-Cutting Concern (Decision #5)**: Configuration operates orthogonally to the layered architecture rather than as another sequential layer. This design recognizes that experimental parameters influence every aspect of processing—from algorithm thresholds to resource allocation. The orthogonal nature enables consistent configuration management without violating layer independence or creating circular dependencies.

2.  **Parameter Inference (Decision #11)**: The system automatically infers structural parameters from data wherever possible, reducing configuration burden while maintaining reproducibility. This inference currently focuses on data organization: extracting images per well, cycle counts, channel lists, and dataset identifiers from index files. While the architecture supports more sophisticated inference (like analyzing intensity distributions), current implementation provides basic structural inference with plans for enhancement. Users can always override inferred values when domain knowledge suggests better choices.

## Interfaces

### Inputs

- Experimental metadata (plate layouts, channel configurations)
- Sample data for parameter inference
- User-provided configuration overrides

### Outputs

- Algorithm-specific parameters for each processing step
- Module configurations with inferred settings
- Execution hints for resource allocation

### Dependencies

- No direct layer dependencies (cross-cutting nature)
- External dependencies: Configuration libraries (YAML/JSON parsing), data analysis tools for inference

## Patterns

The Configuration Layer follows consistent patterns across the codebase:

### Experiment Configuration Pattern

The system uses validated data models to define experiment types with configuration schemas that capture dataset metadata, experiment-specific parameters (images per well, cycle counts), channel mappings and acquisition details, and processing preferences with override capabilities.

### Module Configuration Pattern

Each module receives configuration through standardized interfaces: a `DataConfig` object containing paths to dataset, storage, and workspace; an `Experiment` object with experiment-specific parameters; and module-specific spec containers for algorithm parameters.

### Parameter Inference Pattern

The system implements parameter inference through index analysis (reading experimental metadata), data sampling (analyzing representative samples), smart defaults (based on experiment type), and an override mechanism for explicit user control.

### Resource Estimation Pattern

Processing requirements are dynamically estimated based on data volume (images, plates, wells), processing complexity, historical performance metrics, and module-specific scaling factors. This enables appropriate resource allocation without manual tuning.

## Implementation Location

- Primary location: `starrynight/src/starrynight/experiments/`
- Configuration handling: `starrynight/src/starrynight/modules/common.py`
- Tests: `starrynight/tests/experiments/`

## See Also

- Previous: [Execution Layer](05-execution.md)
- Note: Configuration is a cross-cutting concern that influences all layers
