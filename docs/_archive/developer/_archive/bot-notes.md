# StarryNight Assistant Notes

This document contains notes to help Claude Code assist with the StarryNight project.

## Project Architecture

### Component Overview
1. **StarryNight Core**: CellProfiler-based image processing system
   - Command-line tools for individual algorithms
   - Registry of processing modules
   - CellProfiler pipeline generation and execution

2. **PipeCraft**: Workflow engine
   - Pipeline definition framework
   - Node system for processing tasks
   - Execution backends (local, Docker, AWS)

3. **Conductor**: Job management service
   - REST API for job control
   - Database for configuration and results
   - Job scheduling and monitoring

4. **Canvas**: Web UI
   - React-based interface
   - Project management
   - Job monitoring and configuration

### Key File Paths

```
starrynight/
├── src/starrynight/
│   ├── algorithms/    # Core image processing implementations
│   ├── cli/           # Command-line interface modules
│   ├── modules/       # Module registry and specifications
│   ├── parsers/       # Path parsing for metadata extraction
│   └── utils/         # Utility functions
│
├── pipecraft/         # Workflow engine
│   └── src/pipecraft/
│
├── conductor/         # Job management service
│   └── src/conductor/
│
└── canvas/            # Web interface
    └── app/           # Next.js application
```

## Common CLI Patterns

```sh
# General pattern for most modules:
starrynight [module] loaddata -i [index] -o [output]
starrynight [module] cppipe -l [loaddata] -o [output] -w [workspace]
starrynight cp -p [pipeline] -l [loaddata] -o [output]

# Important flags:
--sbs      # For sequence-based screening
--nuclei   # Nuclear channel (e.g., DAPI)
--cell     # Cell boundary channel (e.g., PhalloAF750)
```

## Module System

The module system follows a three-tier architecture:
1. **LoadData Generation**: Creates CSVs for CellProfiler
2. **Pipeline Generation**: Creates .cppipe files
3. **Pipeline Execution**: Uses CellProfiler to process images

Each module is registered in the central registry, making them discoverable through the CLI.

## CellProfiler Integration

- StarryNight uses `cellprofiler_core` to interact with CellProfiler
- Manages JVM for CellProfiler's Java dependencies
- Generates pipeline files (.cppipe) from templates
- Creates LoadData CSV files that tell CellProfiler which images to process

## Development Workflow

1. Start with inventory generation to catalog files
2. Generate index to extract metadata from paths
3. Implement module-specific processing:
   - Generate LoadData CSVs
   - Create CellProfiler pipelines
   - Execute pipelines
4. Connect modules into complete pipelines using PipeCraft
5. Run tests and validate results

## Common Issues

- Path resolution: Ensure absolute paths are used with the CellProfiler modules
- Channel naming: Be careful with channel name consistency
- Python environment: CellProfiler has specific dependencies that must be maintained
- Memory usage: Image processing can be memory-intensive, especially with large datasets

## Testing

- Use pytest for unit and integration tests
- Test modules individually before composing workflows
- Validate image processing results with metadata extraction
- Check result files for expected formats and values

## Performance Considerations

- Use parallelization when processing multiple images
- Consider batch size when dealing with large datasets
- Monitor memory usage for large image operations
- Use sampling for preprocessing steps when possible
