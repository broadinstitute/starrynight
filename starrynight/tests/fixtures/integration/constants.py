"""Centralized fixture configuration module for StarryNight tests.

This module provides a single source of truth for all test fixture configurations,
eliminating duplication and inconsistencies across the test suite.

The FIXTURE_CONFIGS dictionary defines all available test fixtures with their:
1. Channel mappings - Used for experiment configuration
2. Input archive configuration - Used for downloading and extracting input data
3. Output archive configuration - Used for validation against reference output

Each fixture has a unique identifier (e.g., 'fix_s1') that is used to:
- Reference the fixture in test parameterization
- Locate pregenerated files in the pregenerated_files/ directory
- Generate fixture-specific pytest fixtures in conftest.py
"""

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
            "sha256": "bcbd01ed62533f92b6657734a87df3f360585950e9b1c76f6bbb86dfa0019ea3",
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
            "sha256": "bcbd01ed62533f92b6657734a87df3f360585950e9b1c76f6bbb86dfa0019ea3",
        },
    },
}
