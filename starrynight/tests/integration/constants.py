# Workflow step configurations for integration tests
WORKFLOW_CONFIGS = [
    # CP illum calc LoadData configuration
    {
        "name": "cp_illum_calc",
        "command_parts": ["illum", "calc", "loaddata"],
        "output_dir_key": "cp_illum_calc_dir",
        "file_pattern": "Batch1_Plate1_illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline1.csv",
        "skip": False,
        "skip_reason": None,
    },
    # CP illum apply LoadData configuration
    {
        "name": "cp_illum_apply",
        "command_parts": ["illum", "apply", "loaddata"],
        "output_dir_key": "cp_illum_apply_dir",
        "file_pattern": "Batch1_Plate1_*_illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline2.csv",
        "skip": False,
        "skip_reason": None,
    },
    # CP segmentation check LoadData configuration
    {
        "name": "cp_segmentation_check",
        "command_parts": ["segcheck", "loaddata"],
        "output_dir_key": "cp_segcheck_dir",
        "file_pattern": "Batch1_Plate1_*_segcheck.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline3.csv",
        "skip": True,
        "skip_reason": "Not implemented",
    },
    # SBS illum calc LoadData configuration
    {
        "name": "sbs_illum_calc",
        "command_parts": ["illum", "calc", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_calc_dir",
        "file_pattern": "Batch1_Plate1_*_illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline5.csv",
        "skip": False,  # Now testing with simplified validator
        "skip_reason": None,
    },
    # SBS illum apply LoadData configuration
    {
        "name": "sbs_illum_apply",
        "command_parts": ["illum", "apply", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_apply_dir",
        "file_pattern": "Batch1_Plate1_*_illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline6.csv",
        "skip": False,
        "skip_reason": None,
    },
    # SBS preprocessing LoadData configuration
    {
        "name": "sbs_preprocessing",
        "command_parts": ["preprocess", "loaddata"],
        "output_dir_key": "sbs_preprocess_dir",
        "file_pattern": "Batch1_Plate1_*_preprocess.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline7.csv",
        "skip": True,
        "skip_reason": "Not implemented",
    },
    # Analysis LoadData configuration
    {
        "name": "analysis",
        "command_parts": ["analysis", "loaddata"],
        "output_dir_key": "analysis_dir",
        "file_pattern": "Batch1_Plate1_*_analysis.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline9.csv",
        "skip": True,
        "skip_reason": "Not implemented",
    },
]

# Define which tests are compatible with which fixture IDs
FIXTURE_COMPATIBILITY = {
    "cp_illum_calc": ["fix_s1", "fix_s2"],
    "cp_illum_apply": ["fix_s1", "fix_s2"],
    "cp_segmentation_check": ["fix_s1", "fix_s2"],
    "sbs_illum_calc": ["fix_s1", "fix_s2"],
    "sbs_illum_apply": ["fix_s1", "fix_s2"],
    "sbs_preprocessing": ["fix_s1", "fix_s2"],
    "analysis": ["fix_s1", "fix_s2"],
}
