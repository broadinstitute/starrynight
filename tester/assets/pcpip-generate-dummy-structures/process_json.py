import json
import pandas as pd
import os

# Create output directories
os.makedirs("csv_output", exist_ok=True)
os.makedirs("filelist_output", exist_ok=True)

# Load the JSON file
with open("generated_csvs.json", "r") as f:
    data = json.load(f)

# Process each section
for section_name, section_data in data.items():
    if not section_data:
        continue

    # Convert to DataFrame and save as CSV in one step
    df = pd.DataFrame(section_data)

    # Create a text file with all filepaths
    filepath_cols = [col for col in df.columns if col.startswith("FilePath_")]
    if filepath_cols:
        all_paths = []
        for col in filepath_cols:
            paths = df[col].dropna().tolist()
            all_paths.extend([p for p in paths if isinstance(p, str)])

        # Write all paths to a text file in filelist_output directory
        path_file = f"filelist_output/{section_name}_filepaths.txt"
        with open(path_file, "w") as f:
            f.write("\n".join(all_paths))
            f.write("\n")

        print(f"Created {path_file} with {len(all_paths)} filepaths")

    # Split FilePath columns into FileName and PathName
    filepath_cols = [col for col in df.columns if col.startswith("FilePath_")]
    for col in filepath_cols:
        suffix = col.replace("FilePath_", "")
        df[f"FileName_{suffix}"] = df[col].apply(
            lambda x: os.path.basename(x) if isinstance(x, str) else x
        )
        df[f"PathName_{suffix}"] = df[col].apply(
            lambda x: os.path.dirname(x) if isinstance(x, str) else x
        )

    # Drop original FilePath columns
    df = df.drop(columns=filepath_cols)

    # Sort columns to put Metadata columns first in specific order
    metadata_order = [
        "Metadata_Plate",
        "Metadata_Well",
        "Metadata_Site",
        "Metadata_Tile",
        "Metadata_SBSCycle",
    ]
    metadata_cols = [col for col in metadata_order if col in df.columns]
    other_cols = [col for col in df.columns if col not in metadata_order]
    df = df[metadata_cols + other_cols]

    output_file = f"csv_output/{section_name}.csv"
    df.to_csv(output_file, index=False)

    print(f"Created {output_file} with {len(df)} rows and {len(df.columns)} columns")

print("All CSV files have been saved to the 'csv_output' directory")
print("All filepath lists have been saved to the 'filelist_output' directory")
