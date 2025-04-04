#!/usr/bin/env python3

import argparse
import json
import re
import itertools
import os
from typing import List, Dict, Any, Optional, Set


def load_json(json_path: str) -> Dict:
    """Load and parse JSON file."""
    with open(json_path, "r") as f:
        return json.load(f)


def get_wells(specified_wells: Optional[List[str]] = None) -> List[str]:
    """Generate well IDs (A01-H12) if not specified."""
    assert specified_wells is not None, (
        "Wells must be explicitly specified with --wells argument"
    )
    return specified_wells


def get_sites(
    rows: Optional[int] = None,
    columns: Optional[int] = None,
    painting_imperwell: Optional[int] = None,
    default_sites: int = 144,
) -> List[int]:
    """Calculate site numbers based on grid layout or total sites."""
    # Grid-based calculation
    if rows and columns:
        return list(range(0, rows * columns))

    # Total sites
    if painting_imperwell:
        return list(range(0, painting_imperwell))

    # Default
    return list(range(0, default_sites))


def get_tiles(tileperside: int) -> List[int]:
    """Generate tile numbers based on tileperside parameter."""
    if tileperside <= 0:
        raise ValueError("tileperside must be a positive integer")
    # Return tile numbers starting from 0
    return list(range(0, tileperside * tileperside))


def extract_pattern_vars(pattern: str) -> Set[str]:
    """Extract variable names from a pattern string."""
    # Match {variable_name} patterns
    return set(re.findall(r"{([^{}]+)}", pattern))


def expand_pattern(
    pattern: str,
    batch: str,
    plates: List[str],
    wells: List[str],
    sites: List[int],
    cp_channels: List[str],
    bc_channels: List[str],
    cp_microscope_channels: List[str],
    bc_microscope_channels: List[str],
    cycles: List[int],
    tiles: List[int],
    object_types: List[str] = ["Nuclei", "Cells", "Cytoplasm"],
    **other_params: Dict[str, Any],
) -> List[str]:
    """Expand a pattern into all possible file paths."""
    paths = []

    # Extract variables from pattern
    pattern_vars = extract_pattern_vars(pattern)

    # Prepare parameter combinations to expand
    param_options = {}

    # Add standard parameters with their values if used in pattern
    if "batch" in pattern_vars:
        param_options["batch"] = [batch]
    if "plate" in pattern_vars:
        param_options["plate"] = plates
    if "well" in pattern_vars:
        param_options["well"] = wells
    if "site" in pattern_vars:
        param_options["site"] = sites
    if "cp_channel" in pattern_vars:
        param_options["cp_channel"] = cp_channels
    if "bc_channel" in pattern_vars:
        param_options["bc_channel"] = bc_channels
    if "cp_microscope_channel" in pattern_vars:
        param_options["cp_microscope_channel"] = cp_microscope_channels
    if "bc_microscope_channel" in pattern_vars:
        param_options["bc_microscope_channel"] = bc_microscope_channels
    if "cycle" in pattern_vars:
        param_options["cycle"] = cycles
    if "tile_number" in pattern_vars:
        # For patterns that use tile_number (like pipeline 9)
        param_options["tile_number"] = tiles
    if "object_type" in pattern_vars:
        param_options["object_type"] = object_types

    # Add any other parameters
    for param, value in other_params.items():
        if param in pattern_vars:
            param_options[param] = [value] if not isinstance(value, list) else value

    # Check if all pattern variables are accounted for
    missing_vars = pattern_vars - set(param_options.keys())
    if missing_vars:
        print(f"Warning: Missing values for pattern variables: {missing_vars}")
        return []

    # Create all combinations of parameters
    param_names = list(param_options.keys())
    param_values = [param_options[name] for name in param_names]

    # Generate paths for all combinations
    for combination in itertools.product(*param_values):
        param_dict = dict(zip(param_names, combination))
        expanded_path = pattern
        for param, value in param_dict.items():
            expanded_path = expanded_path.replace(f"{{{param}}}", str(value))
        paths.append(expanded_path)

    return paths


def create_dummy_file(filepath: str, base_path: Optional[str] = None) -> None:
    """Create a dummy file with its filename as content."""
    # Apply base path if specified
    if base_path:
        filepath = os.path.join(base_path, filepath)

    # Ensure directory exists
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Create a simple text file for all file types
    with open(filepath, "w") as f:
        f.write(f"This is a dummy placeholder file: {filepath}\n")
        f.write("Generated for simulation purposes only.\n")


def generate_all_outputs(
    io_json_path: str,
    batch_id: str,
    plates: List[str],
    wells: List[str],  # Wells are now required, not optional
    barcoding_cycles: int = 4,
    rows: Optional[int] = None,
    columns: Optional[int] = None,
    bc_rows: Optional[int] = None,
    bc_columns: Optional[int] = None,
    painting_imperwell: Optional[int] = None,
    barcoding_imperwell: Optional[int] = None,
    stitchorder: str = "Grid: row-by-row",
    round_or_square: str = "square",
    overlap_pct: int = 10,
    tileperside: int = 5,
    metadata_dir: str = "metadata",
    raw_image_template: str = "image",
    channel_number: int = 1,
    size: int = 1024,
    final_tile_size: int = 1024,
    painting_rows: Optional[int] = None,
    painting_columns: Optional[int] = None,
    barcoding_rows: Optional[int] = None,
    barcoding_columns: Optional[int] = None,
    create_files: bool = False,
    max_files_per_type: Optional[int] = None,
    base_path: Optional[str] = None,
) -> Dict[str, Dict[str, List[str]]]:
    """Generate all output paths for the entire pipeline."""
    outputs = {}

    # 1. Load io.json and extract patterns
    schema = load_json(io_json_path)

    # 2. Generate parameter lists
    wells_list = get_wells(wells)  # Format wells properly

    # Use appropriate rows/columns values
    painting_rows_val = painting_rows or rows
    painting_columns_val = painting_columns or columns
    barcoding_rows_val = barcoding_rows or bc_rows or rows
    barcoding_columns_val = barcoding_columns or bc_columns or columns

    painting_sites_list = get_sites(
        painting_rows_val, painting_columns_val, painting_imperwell
    )
    barcoding_sites_list = get_sites(
        barcoding_rows_val, barcoding_columns_val, barcoding_imperwell
    )

    # 3. Extract channel information from schema
    cp_channels = schema["metadata_schema"]["cp_channel"]["enum"]
    bc_channels = schema["metadata_schema"]["bc_channel"]["enum"]
    cp_microscope_channels = schema["metadata_schema"]["cp_microscope_channel"]["enum"]
    bc_microscope_channels = schema["metadata_schema"]["bc_microscope_channel"]["enum"]

    # 4. Generate tiles list - ensure tileperside is valid
    assert tileperside > 0, "tileperside must be a positive int"
    tiles_list = get_tiles(tileperside)

    # Print parameter information for debugging
    print(
        f"Generating outputs with: {len(wells_list)} wells, "
        f"{len(painting_sites_list)} painting sites, "
        f"{len(barcoding_sites_list)} barcoding sites, "
        f"{len(tiles_list)} tiles"
    )

    # 5. Process each module and calculate its outputs
    for module_name in schema.keys():
        # Skip non-module sections
        if module_name in ["metadata_schema"]:
            continue

        module = schema[module_name]
        outputs[module_name] = {}

        # Process each output type in this module
        for output_type, output_def in module.get("outputs", {}).items():
            outputs[module_name][output_type] = []

            # Handle each pattern for this output type
            patterns = output_def.get("patterns", [])
            if (
                not patterns and "pattern" in output_def
            ):  # Handle legacy singular pattern
                patterns = [output_def["pattern"]]

            for pattern in patterns:
                # Use appropriate site list based on module
                sites_list = (
                    barcoding_sites_list if "BC" in module_name else painting_sites_list
                )

                # Expand pattern for all parameter combinations
                expanded_paths = expand_pattern(
                    pattern,
                    batch=batch_id,
                    plates=plates,
                    wells=wells_list,
                    sites=sites_list,
                    cp_channels=cp_channels,
                    bc_channels=bc_channels,
                    cp_microscope_channels=cp_microscope_channels,
                    bc_microscope_channels=bc_microscope_channels,
                    cycles=[f"{cycle:02d}" for cycle in range(1, barcoding_cycles + 1)],
                    tiles=tiles_list,
                    # Include all other parameters
                    stitchorder=stitchorder,
                    round_or_square=round_or_square,
                    overlap_pct=overlap_pct,
                    metadata_dir=metadata_dir,
                    raw_image_template=raw_image_template,
                    channel_number=channel_number,
                    size=size,
                    final_tile_size=final_tile_size,
                    painting_rows=painting_rows_val,
                    painting_columns=painting_columns_val,
                    barcoding_rows=barcoding_rows_val,
                    barcoding_columns=barcoding_columns_val,
                    painting_imperwell=painting_imperwell,
                    barcoding_imperwell=barcoding_imperwell,
                )

                # Limit files if requested
                if (
                    max_files_per_type is not None
                    and len(expanded_paths) > max_files_per_type
                ):
                    print(
                        f"Limiting {module_name}.{output_type} from {len(expanded_paths)} to {max_files_per_type} files"
                    )
                    expanded_paths = expanded_paths[:max_files_per_type]

                outputs[module_name][output_type].extend(expanded_paths)

                # Create files if requested
                if create_files:
                    file_count = 0
                    for path in expanded_paths:
                        create_dummy_file(path, base_path)
                        file_count += 1
                        # Log progress for large file sets
                        if file_count % 100 == 0:
                            print(
                                f"Created {file_count}/{len(expanded_paths)} files for {module_name}.{output_type}"
                            )

                    if file_count > 0:
                        print(
                            f"Created {file_count} dummy files for {module_name}.{output_type}"
                        )

    return outputs


def output_to_file(outputs: Dict[str, Dict[str, List[str]]], output_file: str) -> None:
    """Write outputs to file."""
    with open(output_file, "w") as f:
        json.dump(outputs, f, indent=2)


def output_summary(outputs: Dict[str, Dict[str, List[str]]]) -> None:
    """Display summary of outputs."""
    total_files = 0

    print("\nOutput Summary:")
    print("==============")

    for module, module_outputs in outputs.items():
        module_total = sum(len(paths) for paths in module_outputs.values())
        total_files += module_total

        print(f"\n{module}:")
        for output_type, paths in module_outputs.items():
            print(f"  {output_type}: {len(paths)} files")

    print(f"\nTotal output files: {total_files}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate all pipeline output paths and optionally create dummy files"
    )

    # Required parameters
    parser.add_argument("--io-json", required=True, help="Path to io.json file")
    parser.add_argument("--batch", required=True, help="Batch identifier")
    parser.add_argument(
        "--plates", required=True, nargs="+", help="List of plate identifiers"
    )
    parser.add_argument(
        "--wells",
        required=True,
        nargs="+",
        help="List of wells (required, format: A01 or A1)",
    )

    # Grid layout
    parser.add_argument("--rows", type=int, help="Number of rows in acquisition grid")
    parser.add_argument(
        "--columns", type=int, help="Number of columns in acquisition grid"
    )
    parser.add_argument(
        "--painting-rows",
        type=int,
        help="Number of rows in painting acquisition grid (if different)",
    )
    parser.add_argument(
        "--painting-columns",
        type=int,
        help="Number of columns in painting acquisition grid (if different)",
    )
    parser.add_argument(
        "--bc-rows",
        type=int,
        help="Number of rows in barcoding acquisition grid (if different)",
    )
    parser.add_argument(
        "--bc-columns",
        type=int,
        help="Number of columns in barcoding acquisition grid (if different)",
    )

    # Or total sites
    parser.add_argument(
        "--painting-imperwell",
        type=int,
        help="Total number of painting images per well",
    )
    parser.add_argument(
        "--barcoding-imperwell",
        type=int,
        help="Total number of barcoding images per well",
    )

    # Barcoding
    parser.add_argument(
        "--barcoding-cycles", type=int, default=4, help="Number of barcoding cycles"
    )

    # Stitching parameters
    parser.add_argument(
        "--stitchorder", default="Grid: row-by-row", help="Order for stitching tiles"
    )
    parser.add_argument(
        "--round-or-square",
        default="square",
        choices=["round", "square"],
        help="Well shape",
    )
    parser.add_argument(
        "--overlap-pct",
        type=int,
        default=10,
        help="Percentage overlap between adjacent tiles",
    )
    parser.add_argument(
        "--tileperside",
        type=int,
        default=5,
        help="Number of tiles per side after cropping",
    )
    parser.add_argument(
        "--size", type=int, default=1024, help="Size parameter for stitching"
    )
    parser.add_argument(
        "--final-tile-size",
        type=int,
        default=1024,
        help="Pixel dimensions of output tiles",
    )

    # Other parameters
    parser.add_argument(
        "--metadata-dir", default="metadata", help="Directory containing metadata files"
    )
    parser.add_argument(
        "--raw-image-template", default="IMAGE", help="Template for raw image filenames"
    )
    parser.add_argument(
        "--channel-number",
        type=int,
        default=1,
        help="Channel number for overlay images",
    )

    # File creation options
    parser.add_argument(
        "--create-files", action="store_true", help="Create dummy files for all paths"
    )
    parser.add_argument(
        "--max-files-per-type",
        type=int,
        help="Limit number of files per output type (to avoid creating too many files)",
    )
    parser.add_argument(
        "--base-path",
        help="Base directory where files will be created (default: current directory)",
    )

    # Output control
    parser.add_argument(
        "--output-file", help="Output file to write all paths (JSON format)"
    )
    parser.add_argument(
        "--output-format",
        default="summary",
        choices=["summary", "full", "both"],
        help="Output format: summary, full listing, or both",
    )

    args = parser.parse_args()

    # Generate outputs
    outputs = generate_all_outputs(
        io_json_path=args.io_json,
        batch_id=args.batch,
        plates=args.plates,
        wells=args.wells,
        barcoding_cycles=args.barcoding_cycles,
        rows=args.rows,
        columns=args.columns,
        painting_rows=args.painting_rows,
        painting_columns=args.painting_columns,
        bc_rows=args.bc_rows,
        bc_columns=args.bc_columns,
        painting_imperwell=args.painting_imperwell,
        barcoding_imperwell=args.barcoding_imperwell,
        stitchorder=args.stitchorder,
        round_or_square=args.round_or_square,
        overlap_pct=args.overlap_pct,
        tileperside=args.tileperside,
        metadata_dir=args.metadata_dir,
        raw_image_template=args.raw_image_template,
        channel_number=args.channel_number,
        size=args.size,
        final_tile_size=args.final_tile_size,
        create_files=args.create_files,
        max_files_per_type=args.max_files_per_type,
        base_path=args.base_path,
    )

    # Output results
    if args.output_format in ["summary", "both"]:
        output_summary(outputs)

    if args.output_format in ["full", "both"]:
        # Print full listing to console
        for module, module_outputs in outputs.items():
            print(f"\n{module}:")
            for output_type, paths in module_outputs.items():
                print(f"  {output_type}:")
                for i, path in enumerate(paths):
                    if i < 10 or i > len(paths) - 10:  # Show first/last 10
                        print(f"    {path}")
                    elif i == 10:
                        print(f"    ... ({len(paths) - 20} more) ...")

    # Write to file if requested
    if args.output_file:
        output_to_file(outputs, args.output_file)
        print(f"\nDetailed output written to {args.output_file}")


if __name__ == "__main__":
    main()
