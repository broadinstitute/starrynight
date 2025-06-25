# Workflow step configurations for integration tests
#
# Each configuration defines a workflow step with:
# - name: Unique identifier for the workflow step
# - command_parts: CLI command components (used to determine which function to call)
# - output_dir_key: Key to find the output directory in the workspace dict
# - file_pattern: Pattern to match generated LoadData files
# - ref_csv_pattern: Pattern to find reference CSV for validation
# - skip: Whether to skip this test
# - skip_reason: Explanation if skipped
# - optional_params: Additional CLI parameters for this step
#
# NOTE: optional_params is currently empty for all steps. StarryNight uses
# smart defaults to resolve paths (e.g., illum files, corrected images).
# When implementing full pipeline testing, we may need to populate these
# with explicit paths to ensure correct data flow between workflow steps.
WORKFLOW_CONFIGS = [
    # CP illum calc LoadData configuration
    {
        "name": "cp_illum_calc",
        "command_parts": ["illum", "calc", "loaddata"],
        "output_dir_key": "cp_illum_calc_dir",
        "file_pattern": "Batch1^Plate1#illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline1.csv",
        "skip": False,
        "skip_reason": None,
        # Optional parameters for this step
        "optional_params": {},
    },
    # CP illum apply LoadData configuration
    {
        "name": "cp_illum_apply",
        "command_parts": ["illum", "apply", "loaddata"],
        "output_dir_key": "cp_illum_apply_dir",
        "file_pattern": "Batch1^Plate1^*#illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline2.csv",
        "skip": False,
        "skip_reason": None,
        "optional_params": {},
    },
    # CP segmentation check LoadData configuration
    {
        "name": "cp_segmentation_check",
        "command_parts": ["segcheck", "loaddata"],
        "output_dir_key": "cp_segcheck_dir",
        "file_pattern": "Batch1^Plate1^*#segcheck.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline3.csv",
        "skip": False,
        "skip_reason": None,
        "optional_params": {},
    },
    # SBS illum calc LoadData configuration
    {
        "name": "sbs_illum_calc",
        "command_parts": ["illum", "calc", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_calc_dir",
        "file_pattern": "Batch1^Plate1^*#illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline5.csv",
        "skip": False,  # Now testing with simplified validator
        "skip_reason": None,
        "optional_params": {},
    },
    # SBS illum apply LoadData configuration
    {
        "name": "sbs_illum_apply",
        "command_parts": ["illum", "apply", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_apply_dir",
        "file_pattern": "Batch1^Plate1^*#illum_apply_sbs.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline6.csv",
        "skip": False,
        "skip_reason": None,
        "optional_params": {},
    },
    # SBS preprocessing LoadData configuration
    {
        "name": "sbs_preprocessing",
        "command_parts": ["preprocess", "loaddata"],
        "output_dir_key": "sbs_preprocess_dir",
        "file_pattern": "Batch1^Plate1^*#preprocess_sbs.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline7.csv",
        "skip": False,
        "skip_reason": None,
        "optional_params": {},
    },
    # Analysis LoadData configuration
    {
        "name": "analysis",
        "command_parts": ["analysis", "loaddata"],
        "output_dir_key": "analysis_dir",
        "file_pattern": "Batch1^Plate1^*#analysis.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline9.csv",
        "skip": False,
        "skip_reason": None,
        "optional_params": {},
    },
]

# Define which tests are compatible with which fixture IDs
FIXTURE_COMPATIBILITY = {
    "cp_illum_calc": ["fix_s1", "fix_s2", "fix_l1"],
    "cp_illum_apply": ["fix_s1", "fix_s2", "fix_l1"],
    "cp_segmentation_check": ["fix_s1", "fix_s2", "fix_l1"],
    "sbs_illum_calc": ["fix_s1", "fix_s2", "fix_l1"],
    "sbs_illum_apply": ["fix_s1", "fix_s2", "fix_l1"],
    "sbs_preprocessing": ["fix_s1", "fix_s2", "fix_l1"],
    "analysis": ["fix_s1", "fix_s2", "fix_l1"],
}
