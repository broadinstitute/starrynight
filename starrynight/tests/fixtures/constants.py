# Comprehensive fixture configuration
FIXTURE_CONFIGS = {
    "fix_s1": {
        # Channel configurations
        "channels": {
            "cp_nuclei_channel": "DAPI",
            "cp_cell_channel": "PhalloAF750",
            "cp_mito_channel": "ZO1AF488",
            "sbs_nuclei_channel": "DAPI",
            "sbs_cell_channel": "PhalloAF750",
            "sbs_mito_channel": "ZO1AF488",
        },
        # Input configuration
        "input": {
            "archive_name": "fix_s1_input.tar.gz",
            "dir_prefix": "fix_s1_input_test",
            "dir_name": "fix_s1_input",
            "dataset_dir_name": "Source1",
            "sha256": "ddba28e1593986013d10880678d2d7715af8d2ee1cfa11ae7bcea4d50c30f9e0",
        },
        # Output configuration
        "output": {
            "archive_name": "fix_s1_output.tar.gz",
            "dir_prefix": "fix_s1_output_test",
            "dir_name": "fix_s1_pcpip_output",
            "dataset_dir_name": "Source1",
            "sha256": "a84788c2d5296c02e58c38c382c9b4019c414162a58021a7bfc7c5f20a38be2a",
        },
    },
    "fix_s2": {
        # Channel configurations
        "channels": {
            "cp_nuclei_channel": "DAPI",
            "cp_cell_channel": "PhalloAF750",
            "cp_mito_channel": "ZO1AF488",
            "sbs_nuclei_channel": "DAPI",
            "sbs_cell_channel": "PhalloAF750",
            "sbs_mito_channel": "ZO1AF488",
        },
        # Input configuration
        "input": {
            "archive_name": "fix_s1_input.tar.gz",
            "dir_prefix": "fix_s1_input_test",
            "dir_name": "fix_s1_input",
            "dataset_dir_name": "Source1",
            "sha256": "ddba28e1593986013d10880678d2d7715af8d2ee1cfa11ae7bcea4d50c30f9e0",
        },
        # Output configuration
        "output": {
            "archive_name": "fix_s1_output.tar.gz",
            "dir_prefix": "fix_s1_output_test",
            "dir_name": "fix_s1_pcpip_output",
            "dataset_dir_name": "Source1",
            "sha256": "a84788c2d5296c02e58c38c382c9b4019c414162a58021a7bfc7c5f20a38be2a",
        },
    },
}
