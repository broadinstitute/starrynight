# StarryNight Operational Challenges FAQ

## Introduction

This FAQ addresses the most common operational challenges encountered when transitioning from PCPIP to StarryNight for high-throughput microscopy image processing. These questions emerged from real-world usage scenarios and represent the day-to-day operational needs of research teams processing Cell Painting and Sequencing by Synthesis (SBS) data.

StarryNight is designed to handle these scenarios through its modular architecture, flexible configuration system, and cloud-native approach. While some solutions require advanced user knowledge, the platform provides robust mechanisms to address each challenge.

---

## 1. Starting Processing Before All Images Are Available

**Problem**: "Sometimes we want to start before all the images are available (because image generation can take up to a couple of weeks on the SBS arm, so we want to do processing of the phenotyping arm while the barcoding is not started or only partially done). Sometimes they decide to add a cycle partway through because one cycle got screwed up, so the cycle counts we put in at the beginning are now wrong."

**Status**: ✅ **Available**

**Solution**:
StarryNight supports partial data processing through separate pipeline workflows and automatic cycle detection:

1. **Separate Pipeline Workflows**: Create distinct pipelines for phenotypic and SBS arms using PipeCraft composition
   - Copy the existing `PCP_generic.py` pipeline
   - Create specialized versions (e.g., `PCP_phenotype.py`) by removing unwanted modules
   - Add new pipeline variants to the pipeline registry for user selection

2. **Automatic Cycle Management**: StarryNight automatically infers cycle counts from indexing rather than requiring fixed configuration
   - When cycles are added partway through, simply re-index the data
   - The system automatically detects new cycles and updates load data generation
   - No manual cycle count updates required

**Implementation**:
```bash
# Create separate phenotypic pipeline
starrynight exp run --pipeline pcp_phenotype --config phenotype_config.json

# Later, run SBS pipeline when data is ready
starrynight exp run --pipeline pcp_sbs --config sbs_config.json
```

**User Requirements**: Basic understanding of pipeline configuration and module composition.

---

## 2. Task Retry on Larger Machines

**Problem**: "Sometimes tasks fail and need to be retried on a larger machine"

**Status**: 🚧 **Planned (6-12 months)**

**Solution**:
A resource hints system is being developed to specify computational requirements:

1. **Resource Hints API**: Add vCPU and memory parameters to module configuration
2. **Pipeline Compilation**: Resource hints flow from StarryNight modules → PipeCraft → backend compilers
3. **Backend Integration**: Compilers (Snakemake/AWS Batch) make resource allocation decisions based on hints
4. **Automatic Retry**: Failed tasks can be automatically retried with increased resources

**Current Workaround**: Manual job resubmission with modified container configurations.

**Implementation Timeline**: Requires integration across multiple system layers and backend targets.

---

## 3. Rerunning Steps with New Pipeline Versions

**Problem**: "Sometimes I need to run the same step with a new version of my pipeline. (a) Sometimes I want to do that only on failed jobs, (b) Sometimes I want to do that on a subset of all jobs which previously succeeded"

**Status**:
- **3a (Failed Jobs Only)**: ✅ **Available**
- **3b (Subset of Successful Jobs)**: ⚙️ **Workaround Available**

**Solution**:

**3a - Failed Jobs Only**:
```bash
# Upload new pipeline version and rerun
starrynight exp upload-pipeline --pipeline updated_pipeline.py
starrynight exp rerun --failed-only
```
Snakemake automatically skips completed jobs and reruns only failed ones.

**3b - Subset of Successful Jobs**:
Currently requires manual job-by-job force execution:
```bash
# Force execution for specific jobs
starrynight job force-run --job-id job_123
starrynight job force-run --job-id job_456
```

**Future Enhancement**: Bulk selection UI for arbitrary job subsets (planned for 6-12 months).

**User Requirements**: Understanding of job management and pipeline versioning concepts.

---

## 4. Dropping Corrupted Images

**Problem**: "Sometimes an image is corrupted and needs to be dropped from the experiment (and/or replaced with a dummy image)"

**Status**: 🚧 **Planned (6-12 months)**

**Solution**:
Index-based filtering system without mutating original data:

1. **Blacklist Creation**: Generate filter index files identifying corrupted images
2. **Anti-join Processing**: During data loading, exclude blacklisted files automatically
3. **Filter Interface**: Marimo-based interface for creating and managing filters
4. **Workflow Integration**: All downstream tasks respect filters during processing

**Technical Approach**:
- Parquet index files remain read-only (by design)
- Filtering layer sits between indexing and processing
- Maintains data integrity while enabling selective exclusion

**Current Workaround**: Manual file deletion and re-indexing (requires careful coordination).

**User Requirements**: Understanding of data filtering concepts and file management.

---

## 5. Different Pipeline Versions Per Plate

**Problem**: "Sometimes some plates need a different version of the pipeline than other plates (within the same experiment) - which we won't know ahead of time"

**Status**: ⚙️ **Available (via workaround)**

**Solution**:
Two-step process using index filtering and multiple projects:

1. **Create Separate Projects**: One project per plate requiring different pipeline
2. **Index Filtering**: During project creation, filter index to include only target plate
3. **Pipeline Assignment**: Apply different pipeline configurations per project
4. **Parallel Processing**: Run projects independently with appropriate pipelines

**Implementation**:
```bash
# Project for plate 1 with standard pipeline
starrynight project create --name plate1_project --filter "plate=='Plate1'"
starrynight exp run --pipeline standard_pipeline

# Project for plate 2 with modified pipeline
starrynight project create --name plate2_project --filter "plate=='Plate2'"
starrynight exp run --pipeline modified_pipeline
```

**User Requirements**: Understanding of project management and index filtering.

**Notes**: Functionally equivalent to current practice of separate processing runs, though requires multiple project management.

---

## 6. Different Pipeline Versions Per Well

**Problem**: "Sometimes a single well needs a different version of the pipeline than other wells (within the same experiment) - which we won't know ahead of time"

**Status**: ⚙️ **Available (via workaround)**

**Solution**:
Same index filtering approach as plate-level differentiation, but at well granularity:

1. **Single-Well Filtering**: Filter index to single well/row during project setup
2. **Granular Projects**: Create separate projects for wells requiring different pipelines
3. **Manual Coordination**: Manage multiple small projects for well-specific processing

**Implementation**:
```bash
# Project for specific well with custom pipeline
starrynight project create --name well_A01_project --filter "well=='A01'"
starrynight exp run --pipeline custom_pipeline
```

**User Requirements**: Advanced workflow management skills and understanding of granular data selection.

**Notes**: Extreme edge case requiring significant manual coordination. Functional but not streamlined.

---

## 7. Machine Failures During Job Launch

**Problem**: "Sometimes whatever machine is being used to launch the jobs locks up or dies. (User said 'Possible evasion of this - the machine starrynight runs on is EFS backed, at least for wherever state is being stored')"

**Status**: ✅ **Available (Built-in)**

**Solution**:
Cloud-native architecture provides automatic failure recovery:

1. **S3 Storage Backend**: All state persisted to cloud storage, eliminating local dependencies
2. **AWS Batch Recovery**: Automatic machine failure detection and job reallocation
3. **No EFS Required**: S3-based approach eliminates need for EFS-backed state storage
4. **Transparent Recovery**: Job recovery handled automatically without user intervention

**Architecture Benefits**:
- No single points of failure for job state
- Automatic infrastructure-level recovery
- Persistent storage independent of compute resources

**User Requirements**: None - handled transparently at infrastructure level.

**Setup Requirements**: Proper S3 storage backend configuration.

---

## 8. Incorrect Channel Mapping Information

**Problem**: "Sometimes the biologist shared incorrect information about what was in each channel and our original mapping is wrong"

**Status**: ✅ **Available**

**Solution**:
Configuration update and project reconfiguration:

1. **Syntactic Validation**: Channel names automatically verified against index data
2. **Configuration Update**: Modify channel mapping through Project Settings or experiment config
3. **Project Reconfiguration**: Apply new mapping and reconfigure affected modules
4. **Full Rerun**: Execute complete pipeline with corrected mapping

**Implementation**:
```bash
# Update channel mapping in project settings
starrynight project configure --channel-map updated_channels.json
starrynight exp rerun --full
```

**Validation Features**:
- Automatic detection of non-existent channel names
- Clear error messaging for impossible mappings
- Semantic validation requires manual review

**User Requirements**: Understanding of channel mapping concepts and biological implications.

---

## 9. Incorrect Non-Channel Parameters

**Problem**: "Sometimes the biologist shared incorrect information about some other parameter that doesn't affect channel mapping (like we need to adjust the stitchcrop hyperparameters to be for round vs square; or we need to update the path to the barcodes because the first ones were bad)"

**Status**: ✅ **Available**

**Solution**:
Parameter updates through UI and configuration management:

1. **Project Settings UI**: Update parameters directly through web interface
2. **Notebook Configuration**: Modify experiment config in Marimo notebooks
3. **Selective Rerun**: Execute only affected pipeline modules
4. **Parameter Scope**: Supports stitchcrop hyperparameters, barcode CSV locations, and other pipeline parameters

**Common Parameter Updates**:
- Stitchcrop hyperparameters (round vs. square acquisition)
- Barcode CSV file locations
- Analysis thresholds and settings
- Output path configurations

**Implementation**:
- Navigate to Project Settings in web interface
- Update relevant parameters
- Save configuration and rerun affected modules

**User Requirements**: Understanding of parameter impacts on different pipeline stages.

---

## 10. Mixed Round and Square Acquisition

**Problem**: "Sometimes the biologist uses both round acquisition (e.g. for phenotyping) and square acquisition (e.g. for SBS)"

**Status**: ✅ **Available**

**Solution**:
Built-in support for mixed acquisition types through separate configuration:

1. **Separate SBS/CP Configs**: Independent image frame type settings for SBS and Cell Painting
2. **Acquisition Order Settings**: Configure acquisition patterns separately for each processing arm
3. **Module Support**: Stitchcrop module handles different acquisition types automatically
4. **Configuration UI**: Settings available through standard experiment setup

**Configuration Options**:
- SBS config: image frame type and acquisition order
- CP config: independent image frame type and acquisition order
- Stitchcrop: separate processing for phenotypic and SBS images

**User Requirements**: Understanding of acquisition type implications for image processing.

**Notes**: This feature is already implemented and requires no additional development.

---

## General Implementation Notes

### Advanced User Requirements
Most solutions assume users have reasonable competency with the system architecture. While StarryNight provides robust technical capabilities, implementing highly user-friendly interfaces for all edge cases would require significant additional development effort beyond core functionality.

### Common Solution Patterns
- **Index-based filtering**: Primary approach for selective data processing
- **Project-level configuration**: Handles most parameter variations and pipeline customization
- **S3-based storage**: Provides resilience against infrastructure failures
- **Modular pipeline composition**: Enables workflow customization and specialization

### Development Timeline
- **✅ Immediate solutions**: Leverage existing configuration and workflow capabilities
- **🚧 6-12 month features**: Require new UI development and architectural extensions
- **Major development efforts**: Resource management system and bulk operation interfaces

### Related Documentation
- [Getting Started Guide](../user/getting-started.md) - Basic StarryNight setup and usage
- [Parser Configuration](../user/parser-configuration.md) - Data indexing and path parsing
- [Architecture Overview](../architecture/00_architecture_overview.md) - System design and components

---

*This FAQ is based on real user feedback and technical discussions. For additional support or feature requests, please consult the StarryNight documentation or contact the development team.*
