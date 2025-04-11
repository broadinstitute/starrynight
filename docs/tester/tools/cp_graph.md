# cp_graph Tool

The `cp_graph.py` tool converts CellProfiler pipelines into standardized graph representations to analyze data flow between modules. It enables precise comparison of pipeline structures while deliberately excluding module settings.

## Core Functionality

- **Pipeline Comparison**: Generate consistent graph representations to detect functional differences between pipelines
- **Unified Data Flow**: Track all data types (images, objects, lists) in a single comprehensive view
- **Computational Analysis**: Convert pipeline structure to standard graph formats for programmatic analysis
- **Standardized Output**: Create canonical representations that ignore irrelevant differences (like module reordering)
- **Visualization**: View pipeline structure as a directed graph with intuitive color coding

## Usage

```bash
# Run with regular Python
python cp_graph.py <pipeline.json> <output_file> [options]

# Run with UV to automatically install dependencies (recommended)
uv run --script cp_graph.py <pipeline.json> <output_file> [options]
```

- `pipeline.json` - Your CellProfiler pipeline file (v6 JSON format)
- `output_file` - Output file path (supports .graphml, .gexf, or .dot formats)

### Options

**Display Options:**
- `--no-formatting` - Strip all formatting information to focus on topology for comparison
- `--no-module-info` - Hide module information on graph edges
- `--ultra-minimal` - Create minimal output with only essential structure for exact diff comparison
- `--explain-ids` - Print mapping of stable node IDs to original module numbers

**Content Filtering Options:**
- `--include-disabled` - Include disabled modules in the graph (excluded by default)

## Pipeline Comparison Examples

### Confirming Structural Equivalence

When comparing two pipelines with identical structure but different module numbering:

```bash
python cp_graph.py pipeline1.json pipeline1_ultra.dot --ultra-minimal
python cp_graph.py pipeline2.json pipeline2_ultra.dot --ultra-minimal
diff pipeline1_ultra.dot pipeline2_ultra.dot
```

This produces no output if the pipelines are structurally identical.

### Detecting Real Functional Differences

When comparing pipelines with actual differences:

```bash
python cp_graph.py pipeline1.json pipeline1_ultra.dot --ultra-minimal
python cp_graph.py modified_pipeline.json modified_ultra.dot --ultra-minimal
diff pipeline1_ultra.dot modified_ultra.dot
```

This reveals structural differences like missing modules or connections.

## Visualization

While the primary purpose is computational analysis and comparison, the tool also supports visualization:

```bash
# Generate DOT file
python cp_graph.py pipeline.json pipeline.dot

# Generate PNG from DOT file (requires Graphviz)
dot -Tpng pipeline.dot -o pipeline.png
```

### Visual Elements

The graph visually represents different elements:

- **Images**: Gray ovals
- **Objects**: Green ovals
- **Processing Modules**: Blue boxes with the module name and number
- **Disabled Modules**: Pink boxes with dashed borders (when included)
- **Connections**: Arrows showing the flow between data nodes and modules

## Requirements

- Python 3.11+
- NetworkX library
- PyDot (for DOT output)
- Click (for CLI interface)
- Graphviz (for PNG rendering)

Install dependencies with:

```bash
pip install networkx pydot click
```

Or use UV (recommended):

```bash
uv pip install networkx pydot click
```

## Usage in Pipeline Validation

In the pipeline validation process, `cp_graph.py` is used primarily in Stage 1 (Graph Topology) to:

1. Generate DOT graph representations of both reference and StarryNight pipelines
2. Create ultra-minimal versions for exact structural comparison
3. Generate visual representations for human inspection
4. Compare the structures with the diff tool

For detailed usage examples, refer to the individual pipeline validation documents.
