# StarryNight Operational Challenges FAQ

## Introduction

This FAQ addresses critical operational challenges faced by research teams transitioning from PCPIP to StarryNight for high-throughput microscopy image processing. These questions emerged from real-world discussions with users processing Optical Pooled Screening (OPS) data at scale.

**Status Legend:**

- ✅ **Available**: Ready to use with current system
- ⚙️ **Workaround**: Possible but requires manual coordination
- 🚧 **Planned**: Architecturally supported, needs implementation
- 🔬 **Design**: Requires significant architectural consideration

---

## 1. Starting Processing Before All Images Are Available

**Real-World Scenario**: Research teams often need to start processing before all images are available, particularly when SBS image generation takes weeks and they want to process the phenotyping arm while barcoding data is still being acquired.

**Status**: ✅ **Currently Available**

**Technical Solution**:
StarryNight's modular pipeline architecture supports this through composition and registry customization:

**Code Location**: `/starrynight/src/starrynight/pipelines/pcp_generic.py`

Current implementation shows parallel CP and SBS processing:

```python
# Existing combined pipeline structure
Parallel([
    Seq([cp_illum_calc_loaddata.pipe, cp_illum_calc_cpipe.pipe, ...]),  # CP pipeline
    Seq([sbs_illum_calc_loaddata.pipe, sbs_illum_calc_cpipe.pipe, ...])  # SBS pipeline
])
```

**Implementation Steps**:

1. **Create Pipeline Variants**: Copy `pcp_generic.py` to create specialized versions (requires developer)
2. **Register New Pipelines**: Add to `PIPELINE_REGISTRY` in `/starrynight/src/starrynight/pipelines/registry.py`
3. **Execute Separately**:
   ```bash
   # Current: Create full experiment
   starrynight exp new -i index.parquet -e "Pooled CellPainting [Generic]" -c config.json -o output/

   # Proposed: Separate pipelines (would need implementation)
   starrynight exp new -e "Pooled CellPainting [Phenotypic]" -c cp_config.json -o cp_output/
   starrynight exp new -e "Pooled CellPainting [SBS]" -c sbs_config.json -o sbs_output/
   ```

**Current Reality**: Must modify codebase to add new pipeline types. The modular architecture supports this, but requires development effort rather than configuration.

**Current Workaround**: Use existing pipeline but filter processing to skip unavailable data (discussed by developers as viable workaround).

---

## 2. Adding Cycles Mid-Experiment

**Real-World Scenario**: Experiments sometimes require additional cycles mid-process due to failed acquisitions, making the original cycle count configuration incorrect.

**Status**: ✅ **Currently Available** (with data loss)

**Technical Solution**: StarryNight auto-detects cycles from data structure, not configuration.

**Code Evidence**: In `/starrynight/src/starrynight/experiments/pcp_generic.py`:
```python
# Auto-detects number of cycles from actual data
sbs_n_cycles = (
    sbs_images_df.select(pl.col("cycle_id").unique().count())
    .collect()
    .rows()[0][0]
)
```

**Recovery Process**:

1. **Add New Cycle Images**: Place additional cycle data in the dataset
2. **Re-inventory**: `starrynight inventory` (detects new files)
3. **Re-index**: `starrynight index` (updates cycle count automatically)
4. **Reconfigure**: `starrynight exp new` (creates new experiment with updated cycle count)
5. **Reprocess**: All downstream processing adapts to detected cycles automatically

**Limitation**: Previous processing results are lost and must be recomputed. No incremental update capability currently exists.

**Limitation**: If you need to *exclude* specific cycles (e.g., skip corrupted cycle 5), this must be handled in the CellProfiler pipeline configuration, not in StarryNight's index layer.

---

## 3. Resource Management and Retry Logic

### 3A. Failed Job Retry on Larger Machines

**Real-World Scenario**: Tasks occasionally fail due to resource constraints and need retry with increased computational resources.

**Status**: 🚧 **Planned Architecture** (6-12 months)

**Current Reality**: Basic retry exists through Snakemake backend (`/pipecraft/src/pipecraft/backend/snakemake.py`), but no resource escalation.

**Planned Solution - Resource Hints System**:
The architecture supports this through a planned resource hints API:

```python
# Conceptual module configuration
module_config = {
    "cpu_cores": 4,
    "memory_gb": 16,
    "retry_with_larger": True  # Escalate resources on failure
}
```

**Technical Flow**: StarryNight modules → PipeCraft compilation → Backend execution (Snakemake/AWS Batch)

**Current Workaround**: Manual job resubmission with modified resource configurations.

### 3B. Rerunning Successful Jobs with New Pipeline Versions

**Real-World Scenario**: Users sometimes need to rerun specific subsets of previously successful jobs with updated pipeline versions.

**Status**: ⚙️ **Manual Workaround Available**

**Current Capability**: Can rerun individual modules or entire workflows through Conductor backend, but no bulk selection interface.

**Technical Reality**: Developers acknowledge this wasn't part of the original design considerations, so implementing bulk job selection would require significant architectural planning.

**Current Workaround**: Force rerun of specific modules through Canvas UI or rebuild entire pipeline with new parameters.

---

## 4. Handling Corrupted Images

**Real-World Scenario**: Corrupted images occasionally need to be excluded from experiments or replaced with dummy images to maintain data consistency.

**Status**: 🚧 **Architectural Design Phase** (6-12 months)

**Technical Challenge**: Index files use Parquet format, which is (practically, given the size) immutable by design.

**Code Location**: Index structure in `/starrynight/src/starrynight/algorithms/index.py`

**Proposed Solution - Filter-Based Approach**:
Rather than modifying index files, create filtering layers:

1. **Blocklist Creation**: Generate separate index files identifying corrupted images
2. **Anti-join Processing**: Filter main index during data loading:
   ```python
   # Conceptual filtering approach using polars
   filtered_df = main_index_df.join(blacklist_df, on="file_path", how="anti")
   ```
3. **Marimo Interface**: Interactive notebook for filter creation and management
4. **Workflow Integration**: All downstream modules respect filtered indices

**Implementation Gap**: No current CLI commands for index manipulation. Would need new filtering utilities in `/starrynight/src/starrynight/utils/dfutils.py`.

**Current Workaround**: Manual file deletion and complete re-indexing (requires careful coordination).

---

## 5. Different Pipeline Versions Per Plate

**Real-World Scenario**: Different plates within the same experiment sometimes require different pipeline versions, with the need for variation only discovered during processing.

**Status**: ⚙️ **Currently Available** (via multiple projects)

**Technical Solution**: Index filtering + separate project management

**Code Location**: `/starrynight/src/starrynight/utils/dfutils.py` provides filtering:
```python
def filter_df_by_column_val(df: pl.LazyFrame, column: str, val: str) -> pl.LazyFrame:
    filtered_df = df.filter(pl.col(column).eq(val))
    return filtered_df
```

**Implementation Workflow**:
Developers suggest a two-step approach: create separate Canvas projects for each plate group, using index filtering during project setup to include only the target plates for each pipeline version.

1. **Canvas UI**: Create separate projects for each plate
2. **Index Filtering**: During project setup, filter to include only target plate
3. **Pipeline Assignment**: Configure different pipeline versions per project
4. **Coordinate Results**: Manually manage multiple project outputs

**Developer Assessment**: While functional, this approach requires manual coordination across multiple projects - a workable but inelegant solution similar to current multi-run workflows.

**User Requirements**: Understanding of project management and index filtering concepts.

**Limitation**: Not elegant - requires multiple project coordination. No single-project, multi-pipeline capability exists.

---

## 6. Different Pipeline Versions Per Well

**Real-World Scenario**: Individual wells occasionally require different pipeline processing than other wells within the same experiment.

**Status**: ⚙️ **Technically Possible** (extreme edge case)

**Technical Solution**: Same approach as plate-level filtering but at well granularity through Canvas project creation with index filtering.

**Technical Reality**: Developers consider this an extreme edge case requiring substantial manual coordination. While technically possible through the filtering system, it's not streamlined for regular use.

**User Requirements**: Advanced workflow management skills and deep understanding of granular data selection.

**Limitation**: Functional but not elegant. Represents the boundary of practical workflow complexity.

---

## 7. Machine Failures During Job Launch

**Real-World Scenario**: Job launch machines occasionally fail or become unresponsive during processing.

**Status**: ✅ **Built-in Architecture Strength**

**Technical Solution**: Cloud-native design provides automatic resilience

**Technical Explanation**: StarryNight's cloud-native design assumes S3-based storage for all operations, which means job state is automatically preserved in cloud storage rather than being dependent on local machine storage.

**Architecture Benefits**:

- **S3 Storage Backend**: All state persisted to cloud storage
- **Stateless Job Design**: Jobs can be relaunched on any machine
- **AWS Batch Recovery**: Automatic instance failure detection and reallocation
- **No EFS Required**: S3-based approach more robust than EFS-backed alternatives

**User Experience**: Transparent recovery - handled automatically at infrastructure level.

---

## 8. Incorrect Channel Mapping Information

**Real-World Scenario**: Channel mapping information provided during experiment setup is sometimes incorrect, requiring updates to the original configuration.

**Status**: ✅ **Currently Available** with built-in validation

**Technical Solution**: StarryNight already provides syntactic validation

**Code Evidence**: In `pcp_generic.py`:
```python
# Existing channel validation
for cp_custom_channel in init_config_parsed.cp_custom_channel_map.keys():
    assert cp_custom_channel in cp_channel_list
```

**Validation Capabilities**:

- **Syntactic**: Ensures channel names exist in indexed data
- **Error Prevention**: Clear error messages for non-existent channels
- **Configuration Update**: Modify mappings through Project Settings or experiment config

**Recovery Process**:

1. **Update Channel Mapping**: Modify experiment configuration with correct channel assignments
2. **Validate Configuration**: Built-in checks verify channel names against index
3. **Reconfigure Project**: Apply new mapping to all modules
4. **Full Rerun**: Execute complete pipeline with corrected mapping

**Limitation**: Only syntactic validation exists. Semantic validation (e.g., detecting swapped biological meanings) requires manual verification.

**User Interface**: Available through Canvas Project Settings at `/canvas/app/dashboard/project/id/[id]/view/project-settings/`

---

## 9. Incorrect Non-Channel Parameters

**Real-World Scenario**: Non-channel parameters like stitchcrop hyperparameters or barcode file paths sometimes need correction due to initially incorrect information or updated requirements.

**Status**: ✅ **Fully Supported**

**Technical Implementation**: Parameter updates through UI and configuration management

**UI Access**: Canvas project settings interface at `/canvas/app/dashboard/project/id/[id]/view/project-settings/`

**Common Parameter Categories**:

- **Stitchcrop hyperparameters**: Round vs. square acquisition settings
- **Barcode CSV locations**: Update path to correct barcode files
- **Analysis thresholds**: CellProfiler module parameters
- **Output configurations**: Result storage and naming

**Update Process**:

1. **Navigate to Project Settings**: Use web interface for parameter modification
2. **Update Relevant Parameters**: Modify specific configuration values
3. **Save and Reconfigure**: Apply changes to affected modules
4. **Selective Rerun**: Execute only modules affected by parameter changes

**Alternative Interface**: Parameters can also be modified in Marimo execution notebooks for advanced users.

**User Requirements**: Understanding of parameter impacts on different pipeline stages and module dependencies.

---

## 10. Mixed Round and Square Acquisition

**Real-World Scenario**: Experiments often combine different acquisition patterns, such as round acquisition for phenotyping and square acquisition for SBS imaging.

**Status**: ✅ **Built-in Support**

**Technical Implementation**: Independent configuration for CP and SBS acquisition types

**Code Evidence**: In `/starrynight/src/starrynight/experiments/pcp_generic.py`:
```python
class CPConfig(BaseModel):
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)

class SBSConfig(BaseModel):
    img_frame_type: ImageFrameType = Field(ImageFrameType.ROUND)
    acquisition_order: AcquisitionOrderType = Field(AcquisitionOrderType.SNAKE)
```

**Configuration Options**:

- **Cell Painting Config**: Independent image frame type (`ROUND`/`SQUARE`) and acquisition order
- **SBS Config**: Separate image frame type and acquisition pattern settings
- **Module Support**: Stitchcrop module automatically handles different acquisition types

**Usage Examples**:

- Phenotypic arm: `ImageFrameType.ROUND` with `AcquisitionOrderType.SNAKE`
- SBS arm: `ImageFrameType.SQUARE` with `AcquisitionOrderType.SNAKE`

**User Interface**: Settings configurable through standard experiment setup process.

**User Requirements**: Understanding of acquisition type implications for downstream image processing.

---

## Related Documentation

- [Getting Started Guide](../user/getting-started.md) - Basic StarryNight setup and usage patterns
- [Parser Configuration](../user/parser-configuration.md) - Data indexing and path parsing configuration
- [Architecture Overview](../architecture/00_architecture_overview.md) - System design and component interactions
- [Pipeline Composition](../architecture/04_pipeline_layer.md) - Understanding modular pipeline design

---

*This FAQ reflects real-world usage scenarios and technical discussions with StarryNight users. The solutions balance practical implementation with architectural constraints, prioritizing functionality for competent users over simplified interfaces for every edge case.*
