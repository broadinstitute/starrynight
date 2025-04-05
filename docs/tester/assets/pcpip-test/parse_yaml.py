import yaml
import os
import csv
import argparse


def get_file_size(path):
    """Get file size in bytes or None if file doesn't exist."""
    try:
        return os.path.getsize(path) if os.path.exists(path) else None
    except Exception as e:
        print(f"Error getting file size for {path}: {e}")
        return None


def read_csv_headers(file_path, max_headers=20):
    """Read headers from a CSV file and return the first max_headers.
    If there are more than max_headers, the last item will indicate how many more columns exist."""
    try:
        with open(file_path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, [])

            # If we have more headers than max_headers, add a summary entry
            if len(headers) > max_headers:
                remaining = len(headers) - (max_headers - 1)
                return headers[: max_headers - 1] + [f"{remaining} more columns"]
            else:
                return headers
    except Exception as e:
        print(f"Error reading CSV headers from {file_path}: {e}")
        return []


def build_file_paths(yaml_data, path_replacement=None):
    """Process YAML and return structure with full paths and file sizes.

    Args:
        yaml_data: The parsed YAML data
        path_replacement: Tuple of (old_path, new_path) to replace in all paths
    """
    result = {}

    for section_name, section_data in yaml_data.items():
        result[section_name] = section_data.copy()
        base_path = section_data["path"]

        # Apply path replacement if specified
        if path_replacement:
            old_path, new_path = path_replacement
            if base_path.startswith(old_path):
                base_path = base_path.replace(old_path, new_path, 1)
                result[section_name]["path"] = base_path

        if "files" in section_data:
            for set_name, folders in section_data["files"].items():
                result[section_name]["files"][set_name] = []

                for folder_item in folders:
                    folder_path = os.path.join(base_path, folder_item["folder"])
                    processed_folder = {"folder": folder_item["folder"], "files": []}

                    for file_item in folder_item["files"]:
                        if isinstance(file_item, dict):
                            # Handle file type groups (csv, tiff, png)
                            processed_types = {}
                            for file_type, file_list in file_item.items():
                                processed_types[file_type] = []
                                for file_name in file_list:
                                    full_path = os.path.join(folder_path, file_name)
                                    file_info = {
                                        "path": full_path,
                                        "size": get_file_size(full_path),
                                    }

                                    # Add headers for CSV files
                                    if (
                                        file_type.lower() == "csv"
                                        or file_name.lower().endswith(".csv")
                                    ):
                                        file_info["headers"] = read_csv_headers(
                                            full_path
                                        )

                                    processed_types[file_type].append(file_info)

                            processed_folder["files"].append(processed_types)
                        else:
                            # Handle direct file paths
                            full_path = os.path.join(folder_path, file_item)
                            file_info = {
                                "path": full_path,
                                "size": get_file_size(full_path),
                            }

                            # Add headers for CSV files
                            if file_item.lower().endswith(".csv"):
                                file_info["headers"] = read_csv_headers(full_path)

                            processed_folder["files"].append(file_info)

                    result[section_name]["files"][set_name].append(processed_folder)

    return result


def main():
    # Setup command line arguments
    parser = argparse.ArgumentParser(
        description="Parse YAML file and build full paths with sizes"
    )
    parser.add_argument("input_file", help="Input YAML file to process")
    parser.add_argument(
        "-o", "--output_file", help="Output file name (default: input_name_parsed.yaml)"
    )
    parser.add_argument(
        "--replace-path",
        nargs=2,
        metavar=("OLD_PATH", "NEW_PATH"),
        help="Replace OLD_PATH with NEW_PATH in all file paths",
    )
    args = parser.parse_args()

    # If output file not specified, derive it from input filename
    if not args.output_file:
        base, ext = os.path.splitext(args.input_file)
        args.output_file = f"{base}_parsed{ext}"

    # Parse YAML and build full paths with sizes
    with open(args.input_file, "r") as f:
        yaml_data = yaml.safe_load(f)

    # Apply path replacement if specified
    path_replacement = args.replace_path if args.replace_path else None
    processed_data = build_file_paths(yaml_data, path_replacement)

    # Save processed data
    with open(args.output_file, "w") as f:
        yaml.dump(processed_data, f, default_flow_style=False, sort_keys=False)

    print(f"Processed YAML file has been saved to: {args.output_file}")
    if path_replacement:
        print(
            f"Path replacement applied: '{path_replacement[0]}' → '{path_replacement[1]}'"
        )


if __name__ == "__main__":
    main()
