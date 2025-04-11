#!/usr/bin/env python3
import json
import argparse
from copy import deepcopy


###### Utility functions ######


def validate_field_source(field, pipeline_name):
    """Extract field name and source from a field definition, ensuring the source exists.

    Performs validation to ensure the field has a 'source' attribute that isn't empty.
    Raises assertions if requirements aren't met.

    Args:
        field: The field definition dictionary containing 'name' and 'source'
        pipeline_name: Name of the pipeline for error reporting

    Returns:
        tuple: (field_name, field_source) extracted from the field
    """
    field_name = field["name"]

    # Source is required
    assert "source" in field, (
        f"Field {field_name} in {pipeline_name} is missing source attribute"
    )
    field_source = field["source"]
    assert field_source, f"Field {field_name} in {pipeline_name} has empty source"

    return field_name, field_source


def create_reverse_channel_mappings(channel_mappings):
    """Create lookups from logical channels to microscope channels for efficient retrieval.

    Converts the original mappings (microscope->logical) to reverse mappings (logical->microscope)
    for direct dictionary lookups rather than linear searching.

    Args:
        channel_mappings: Dictionary containing channel mappings with microscope_mapping

    Returns:
        dict: Dictionary with channel_type keys and {logical_channel: microscope_channel} values
    """
    reverse_mappings = {}
    for channel_type, mapping_data in channel_mappings.items():
        microscope_mapping = mapping_data.get("microscope_mapping", {})
        # Create reverse mapping (logical -> microscope)
        reverse_mappings[channel_type] = {
            logical: microscope for microscope, logical in microscope_mapping.items()
        }
    return reverse_mappings


###### Pattern resolution functions ######


def apply_metadata_to_pattern(pattern, metadata):
    """Replace metadata placeholders in a pattern with their actual values.

    Substitutes all occurrences of {key} in the pattern with the corresponding
    value from the metadata dictionary, converting values to strings.

    Args:
        pattern: String containing {key} placeholders
        metadata: Dictionary of metadata values to substitute

    Returns:
        str: Pattern with all metadata placeholders replaced with values
    """
    result = pattern
    for key, value in metadata.items():
        # Special handling for cycle to ensure consistent zero-padding
        if key == "cycle":
            result = result.replace(f"{{{key}}}", f"{value:02d}")
        else:
            result = result.replace(f"{{{key}}}", str(value))
    return result


def substitute_channel_in_pattern(
    pattern, channel, channel_type, microscope_var, reverse_channel_mappings
):
    """Replace channel and microscope channel placeholders in a pattern.

    Handles two types of substitutions:
    1. {channel_type_microscope_channel} → corresponding microscope channel
    2. {channel_type_channel} → the logical channel value

    Args:
        pattern: String containing channel placeholders
        channel: Current channel value
        channel_type: Channel type ('cp' or 'bc')
        microscope_var: The microscope variable format to replace
        reverse_channel_mappings: Mapping from logical to microscope channels

    Returns:
        str: Pattern with channel placeholders substituted
    """
    result = pattern

    # Handle microscope channel mapping using direct lookup
    if microscope_var in result:
        microscope_channel = reverse_channel_mappings.get(channel_type, {}).get(channel)
        if microscope_channel:
            result = result.replace(microscope_var, microscope_channel)

    # Direct channel substitution
    channel_var = f"{{{channel_type}_channel}}"
    result = result.replace(channel_var, channel)

    return result


def resolve_pattern_from_source(pipelines, source, metadata):
    """Resolve an input source specification to concrete file patterns.

    Navigates through pipeline definitions to find patterns associated with the
    specified input source, applying metadata substitutions as needed.

    The source format is expected to be: "pipeline_name.inputs.output_type"

    Args:
        pipelines: Dictionary of all pipeline definitions
        source: Input source specification string
        metadata: Metadata to apply to patterns

    Returns:
        list: List of resolved pattern strings with metadata applied
    """
    parts = source.split(".")
    pipeline_name = parts[0]
    output_type = parts[2]

    if pipeline_name == "0_Microscope":
        # Base case: get patterns directly from Microscope outputs
        return pipelines[pipeline_name]["outputs"][output_type]["patterns"]

    # Get the pipeline that produces this output
    pipeline = pipelines[pipeline_name]
    output_patterns = pipeline["outputs"][output_type]["patterns"]

    # Substitute metadata in patterns
    resolved_patterns = []
    for pattern in output_patterns:
        resolved_pattern = pattern
        for key, value in metadata.items():
            # Special handling for cycle to ensure consistent zero-padding
            if key == "cycle":
                resolved_pattern = resolved_pattern.replace(
                    f"{{{key}}}", f"{value:02d}"
                )
            else:
                resolved_pattern = resolved_pattern.replace(f"{{{key}}}", str(value))
        resolved_patterns.append(resolved_pattern)

    return resolved_patterns


###### Field processing functions ######


def create_metadata_field(field_name, field_source, metadata):
    """Create a metadata field object if the field name indicates it's a metadata field.

    Extracts metadata values from the metadata dictionary based on the field source.

    Args:
        field_name: Name of the field
        field_source: Source specification for the field
        metadata: Dictionary of available metadata

    Returns:
        dict: Metadata field object with name and value if valid, None otherwise
    """
    # Only process fields that start with Metadata_
    if not field_name.startswith("Metadata_"):
        return None

    # Handle metadata from source mapping
    if field_source.startswith("metadata."):
        meta_key = field_source.split(".")[1]
        if meta_key in metadata:
            return {"name": field_name, "value": metadata[meta_key]}

    return None


def generate_field_variants(
    field_name,
    field_source,
    pipeline,
    pipelines,
    metadata,
    cycles,
    channel_type,
    channels,
    reverse_channel_mappings,
):
    """Generate all concrete field variants by combining channels and cycles.

    For each combination of applicable channels and cycles:
    1. Resolves the appropriate pattern from the input source
    2. Substitutes channel placeholders and cycle values
    3. Applies metadata values to the pattern

    The function handles the following cases differently:
    - Fields with cycle in name vs. fields without cycle
    - Cycle-dependent input sources vs. cycle-independent sources
    - Fields with cycle in their pattern but not in name

    Args:
        field_name: Name template for the field with possible {cycle} and {channel} placeholders
        field_source: Source specification for the field pattern
        pipeline: Current pipeline definition
        pipelines: Dictionary of all pipeline definitions
        metadata: Base metadata to apply to patterns
        cycles: List of cycles to process
        channel_type: Type of channel ('cp' or 'bc')
        channels: List of channels to process
        reverse_channel_mappings: Mapping from logical to microscope channels

    Returns:
        list: List of field objects with name and value pairs
    """
    results = []

    # Skip if source is not specified
    if not field_source:
        return results

    # Get input information
    if not field_source.startswith("inputs."):
        return results

    input_name = field_source.split(".")[1]
    if input_name not in pipeline.get("inputs", {}):
        return results

    input_source = pipeline["inputs"][input_name]["source"]

    # Determine if cycle substitution is needed in field name or pattern
    field_name_contains_cycle = "{cycle}" in field_name

    # Get pattern(s) - either one common pattern or cycle-specific patterns
    if field_name_contains_cycle:
        # We only need cycle-specific patterns if input_source contains {cycle}
        # Otherwise, we can use the same pattern for all cycles
        if "{cycle}" in input_source:
            # Get a specific pattern for each cycle
            cycle_patterns = {}
            for cycle in cycles:
                cycle_metadata = deepcopy(metadata)
                cycle_metadata["cycle"] = cycle
                patterns = resolve_pattern_from_source(
                    pipelines, input_source, cycle_metadata
                )
                if patterns:
                    cycle_patterns[cycle] = patterns[0]

            # If no cycles had valid patterns, return empty results
            if not cycle_patterns:
                return results
        else:
            # If input_source doesn't depend on cycle, use the same pattern for all cycles
            patterns = resolve_pattern_from_source(pipelines, input_source, metadata)
            if not patterns:
                return results

            # Create a mapping with the same pattern for all cycles
            cycle_patterns = {cycle: patterns[0] for cycle in cycles}
    else:
        # For non-cycle fields, we just need one pattern
        patterns = resolve_pattern_from_source(pipelines, input_source, metadata)
        if not patterns:
            return results

        # Since field doesn't need cycle substitution, we only need one pattern
        pattern = patterns[0]

    # Process each channel
    for channel in channels:
        base_name = field_name.replace(f"{{{channel_type}_channel}}", channel)

        # Apply channel mapping to the microscope variable
        microscope_var = f"{{{channel_type}_microscope_channel}}"
        microscope_channel = reverse_channel_mappings.get(channel_type, {}).get(channel)

        if field_name_contains_cycle:
            # Process pattern for each cycle when field name contains cycle
            for cycle, pattern in cycle_patterns.items():
                # Create expanded field name with cycle
                expanded_name = base_name.replace("{cycle}", f"{cycle:02d}")

                # Apply metadata (including cycle) to pattern
                cycle_metadata = deepcopy(metadata)
                cycle_metadata["cycle"] = cycle
                expanded_pattern = apply_metadata_to_pattern(pattern, cycle_metadata)

                # Apply channel mapping
                if microscope_var in expanded_pattern and microscope_channel:
                    expanded_pattern = expanded_pattern.replace(
                        microscope_var, microscope_channel
                    )

                # Replace channel variable
                channel_var = f"{{{channel_type}_channel}}"
                if channel_var in expanded_pattern:
                    expanded_pattern = expanded_pattern.replace(channel_var, channel)

                # Handle cycle substitution in pattern if needed
                if "{cycle}" in expanded_pattern:
                    expanded_pattern = expanded_pattern.replace(
                        "{cycle}", f"{cycle:02d}"
                    )

                results.append({"name": expanded_name, "value": expanded_pattern})
        else:
            # For non-cycle fields, process just once
            expanded_name = base_name

            # Apply metadata to pattern (no cycle specific info needed)
            expanded_pattern = apply_metadata_to_pattern(pattern, metadata)

            # Apply channel mapping
            if microscope_var in expanded_pattern and microscope_channel:
                expanded_pattern = expanded_pattern.replace(
                    microscope_var, microscope_channel
                )

            # Replace channel variable
            channel_var = f"{{{channel_type}_channel}}"
            if channel_var in expanded_pattern:
                expanded_pattern = expanded_pattern.replace(channel_var, channel)

            # Non-cycle fields might still have cycle in pattern (like bc_channels)
            if "{cycle}" in expanded_pattern:
                # Create one entry per cycle
                for cycle in cycles:
                    cycle_pattern = expanded_pattern.replace("{cycle}", f"{cycle:02d}")
                    results.append({"name": expanded_name, "value": cycle_pattern})
            else:
                # No cycle in pattern - just one result
                results.append({"name": expanded_name, "value": expanded_pattern})

    return results


###### Pipeline processing functions ######


def process_pipeline_location_fields(
    pipeline_name,
    pipeline,
    pipelines,
    metadata,
    cycles,
    cp_channels,
    bc_channels,
    location_key,
    pipeline_results,
    reverse_channel_mappings,
):
    """Process all fields for a specific pipeline and location (well/site/tile).

    Handles two distinct pipeline types:
    1. Cycle-grouped pipelines: Creates a nested structure with per-cycle field lists
    2. Non-cycle pipelines: Creates a flat list of field objects

    For each field, determines if it's:
    - A metadata field: Processed directly
    - A channel field: Determines channel type and processes appropriately

    Args:
        pipeline_name: Name of the current pipeline
        pipeline: Current pipeline definition
        pipelines: Dictionary of all pipeline definitions
        metadata: Metadata for this location
        cycles: List of cycles to process
        cp_channels: List of cell painting channels
        bc_channels: List of barcode channels
        location_key: Key for this location (e.g., "A1-1")
        pipeline_results: Dictionary to store results for this pipeline
        reverse_channel_mappings: Mapping from logical to microscope channels

    Modifies:
        pipeline_results: Adds field results for this location
    """
    # Get the load_data_csv_config
    load_data_config = pipeline["load_data_csv_config"]
    grouping_keys = load_data_config["grouping_keys"]
    fields = load_data_config["fields"]

    # Check if cycle is a grouping dimension
    cycle_is_grouping_key = "cycle" in grouping_keys

    # Initialize the result structure based on whether we're grouping by cycle
    if cycle_is_grouping_key:
        result = {}  # Will be a dict mapping cycles to field lists
        for cycle in cycles:
            result[cycle] = []
    else:
        result = []  # Will be a flat list of fields

    # Process all fields
    for field in fields:
        # Get required field name and source
        field_name, field_source = validate_field_source(field, pipeline_name)

        if cycle_is_grouping_key:
            # Process each cycle separately for cycle-grouped pipelines
            for cycle in cycles:
                # Create metadata with cycle
                cycle_metadata = deepcopy(metadata)
                cycle_metadata["cycle"] = cycle

                # Handle metadata fields first
                metadata_field = create_metadata_field(
                    field_name, field_source, cycle_metadata
                )
                if metadata_field:
                    result[cycle].append(metadata_field)
                    continue

                # Determine channel type, channels list, and cycles to use
                if "{cp_channel}" in field_name:
                    channel_type = "cp"
                    channels = cp_channels
                    cycles_to_use = [cycle]  # For cycle-grouped pipelines
                elif "{bc_channel}" in field_name:
                    channel_type = "bc"
                    channels = bc_channels
                    cycles_to_use = [cycle]  # For cycle-grouped pipelines
                else:
                    # Skip if not a channel field
                    continue

                # Expand the field
                expanded = generate_field_variants(
                    field_name,
                    field_source,
                    pipeline,
                    pipelines,
                    cycle_metadata,
                    cycles_to_use,
                    channel_type,
                    channels,
                    reverse_channel_mappings,
                )
                result[cycle].extend(expanded)
        else:
            # Handle non-cycle-grouped pipelines
            # Handle metadata fields first
            metadata_field = create_metadata_field(field_name, field_source, metadata)
            if metadata_field:
                result.append(metadata_field)
                continue

            # Determine channel type, channels list, and cycles to use
            if "{cp_channel}" in field_name:
                channel_type = "cp"
                channels = cp_channels
                cycles_to_use = [0]  # Default for CP channels
            elif "{bc_channel}" in field_name:
                channel_type = "bc"
                channels = bc_channels
                cycles_to_use = cycles  # Use all cycles directly
            else:
                # Skip if not a channel field
                continue

            # Expand the field
            expanded = generate_field_variants(
                field_name,
                field_source,
                pipeline,
                pipelines,
                metadata,
                cycles_to_use,
                channel_type,
                channels,
                reverse_channel_mappings,
            )
            result.extend(expanded)

    # Store the results
    pipeline_results[location_key] = result


def generate_all_pipeline_fields(io_json_path, config=None):
    """Generate fields for all pipelines defined in an IO JSON file.

    Main entry point for field generation that:
    1. Loads and parses pipeline definitions from the IO JSON
    2. Initializes channel mappings, lists, and configuration
    3. Iterates through all pipelines and processes each
    4. For each pipeline, processes all applicable locations (wells/sites/tiles)

    Args:
        io_json_path: Path to the IO JSON file with pipeline definitions
        config: Optional configuration dictionary (falls back to defaults if None)

    Returns:
        dict: Nested dictionary with pipeline, location, and field results:
             {pipeline_name: {location_key: fields}}
    """
    # Default config if none provided
    if config is None:
        config = {
            "metadata": {
                "batch": "Batch1",
                "plate": "Plate1",
                "raw_image_template": "FOV",
            },
            "wells": ["A1"],
            "sites": [1],
            "tile_numbers": [1, 2, 3, 4],
            "cycles": [1, 2],
        }

    # Load the io.json file
    with open(io_json_path, "r") as f:
        io_data = json.load(f)

    # Extract metadata and pipelines
    metadata_schema = io_data.pop("metadata_schema")
    pipelines = io_data

    # Extract channel lists and mappings
    cp_channels = metadata_schema.get("cp_channel", {}).get("enum", [])
    bc_channels = metadata_schema.get("bc_channel", {}).get("enum", [])
    channel_mappings = metadata_schema.get("channel_mapping", {})

    # Create reverse channel mappings once up front
    reverse_channel_mappings = create_reverse_channel_mappings(channel_mappings)

    # Get parameters from config - these must exist
    assert "wells" in config, "wells must be specified in config"
    assert "sites" in config, "sites must be specified in config"
    assert "tile_numbers" in config, "tile_numbers must be specified in config"
    assert "cycles" in config, "cycles must be specified in config"
    assert "metadata" in config, "metadata must be specified in config"

    wells = config["wells"]
    sites = config["sites"]
    tile_numbers = config["tile_numbers"]
    cycles = config["cycles"]

    # Get basic metadata that's the same for all locations
    base_metadata = config["metadata"]

    # Process each pipeline
    results = {}

    for pipeline_name, pipeline in pipelines.items():
        if "load_data_csv_config" not in pipeline:
            continue

        # Create a result container for this pipeline
        pipeline_results = {}

        # Check if this pipeline uses tile_number as a grouping key
        grouping_keys = pipeline["load_data_csv_config"]["grouping_keys"]
        uses_tile_number = "tile_number" in grouping_keys

        # Determine which location parameter to use based on grouping keys
        location_param = tile_numbers if uses_tile_number else sites
        location_key_name = "tile_number" if uses_tile_number else "site"

        # Process locations based on grouping keys
        for well in wells:
            for location_value in location_param:
                # Create metadata for this combination
                metadata = deepcopy(base_metadata)
                metadata["well"] = well
                metadata[location_key_name] = location_value

                # Create a location key with well and location value
                location_key = f"{well}-{location_value}"

                # Process the fields for this location
                process_pipeline_location_fields(
                    pipeline_name,
                    pipeline,
                    pipelines,
                    metadata,
                    cycles,
                    cp_channels,
                    bc_channels,
                    location_key,
                    pipeline_results,
                    reverse_channel_mappings,
                )

        # Add this pipeline's results to the overall results
        results[pipeline_name] = pipeline_results

    return results


###### Input / Output functions ######


def parse_args():
    """Parse command-line arguments for the field generation script.

    Defines and processes all the command-line options:
    - IO JSON file path
    - Configuration options
    - Experimental parameters (wells, sites, cycles, etc.)
    - Output path

    Returns:
        Namespace: Parsed argument values
    """
    parser = argparse.ArgumentParser(
        description="Expand fields for CellProfiler pipelines"
    )
    parser.add_argument(
        "--io_json", type=str, default="../io.json", help="Path to the io.json file"
    )
    parser.add_argument("--config", type=str, help="Path to a JSON config file")
    parser.add_argument("--batch", type=str, default="Batch1", help="Batch identifier")
    parser.add_argument("--plate", type=str, default="Plate1", help="Plate identifier")
    parser.add_argument(
        "--wells",
        type=str,
        nargs="+",
        default=["A1"],
        help="Well identifiers (e.g. A1 B02)",
    )
    parser.add_argument(
        "--sites", type=int, nargs="+", default=[1], help="Site numbers"
    )
    parser.add_argument(
        "--raw_image_template", type=str, default="IMAGE", help="Raw image template"
    )
    parser.add_argument(
        "--cycles", type=int, nargs="+", default=[1, 2], help="Cycle numbers"
    )
    parser.add_argument(
        "--tile_numbers", type=int, nargs="+", default=[1, 2, 3, 4], help="Tile numbers"
    )
    parser.add_argument("--output", type=str, help="Output file path for JSON results")
    return parser.parse_args()


def serialize_fields_to_json(results, output_file):
    """Serialize the generated field results to a JSON file.

    Processes the nested results structure, handling special cases:
    - Ignores nesting structure and just extracts field data
    - Transforms field arrays with name/value pairs into key-value dictionaries

    Args:
        results: Nested dictionary with generated field results
        output_file: Path to write the JSON output

    Side effects:
        Creates or overwrites the output file with formatted JSON
        Prints a confirmation message to stdout
    """
    json_results = {}

    for pipeline_name, locations in results.items():
        pipeline_fields = []

        # Function to process a node in the nested structure
        def process_node(node):
            # We found field data when we have a list of dicts with 'name' and 'value' keys
            if (
                isinstance(node, list)
                and node
                and isinstance(node[0], dict)
                and "name" in node[0]
                and "value" in node[0]
            ):
                # Convert the fields to a simple dictionary
                field_dict = {field["name"]: field["value"] for field in node}
                pipeline_fields.append(field_dict)
            # For dictionaries, process all values recursively
            elif isinstance(node, dict):
                for value in node.values():
                    process_node(value)

        # Start processing from the locations dictionary
        process_node(locations)

        json_results[pipeline_name] = pipeline_fields

    with open(output_file, "w") as f:
        json.dump(json_results, f, indent=2)

    print(f"Expanded fields saved to: {output_file}")


if __name__ == "__main__":
    args = parse_args()

    # Load config from file if provided
    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        # Create config from command line arguments
        config = {
            "metadata": {
                "batch": args.batch,
                "plate": args.plate,
                "raw_image_template": args.raw_image_template,
            },
            "wells": args.wells,
            "sites": args.sites,
            "tile_numbers": args.tile_numbers,
            "cycles": args.cycles,
        }

    # Expand the fields
    results = generate_all_pipeline_fields(args.io_json, config)
    # Save to JSON if output file is specified
    if args.output:
        serialize_fields_to_json(results, args.output)
