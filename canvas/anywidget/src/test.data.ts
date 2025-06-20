export const data = {
  resource_hints: {
    vcpus: "2",
    memory_gb: "0.5",
  },
  inputs: {
    inventory_path: {
      name: "inventory_path",
      type: "file",
      label: "",
      description: "Path to the inventory.",
      cli_tag: "",
      cli_order: null,
      default: "",
      optional: false,
      format: null,
      folder_name: null,
      file_count: null,
      section_id: "",
      mode: "beginner",
      subtype: null,
      depth: null,
      timepoints: null,
      tiled: null,
      pyramidal: null,
      value:
        "D:\\projects\\github\\broadinstitute\\starrynight\\starrynight\\notebooks\\ipynb\\inventory\\inventory.parquet",
    },
    parser_path: {
      name: "parser_path",
      type: "file",
      label: "",
      description: "Path to a custom parser grammar file.",
      cli_tag: "",
      cli_order: null,
      default: "",
      optional: true,
      format: null,
      folder_name: null,
      file_count: null,
      section_id: "",
      mode: "beginner",
      subtype: null,
      depth: null,
      timepoints: null,
      tiled: null,
      pyramidal: null,
      value: null,
    },
  },
  outputs: {
    project_index_path: {
      name: "project_index",
      type: "file",
      label: "",
      description: "Generated Index",
      cli_tag: "",
      cli_order: null,
      default: "",
      optional: false,
      format: null,
      folder_name: null,
      file_count: null,
      section_id: "",
      mode: "beginner",
      subtype: null,
      depth: null,
      timepoints: null,
      tiled: null,
      pyramidal: null,
      value:
        "D:\\projects\\github\\broadinstitute\\starrynight\\starrynight\\notebooks\\ipynb\\index\\index.parquet",
    },
    index_notebook_path: {
      name: "index_notebook",
      type: "notebook",
      label: "",
      description: "Notebook for inspecting index",
      cli_tag: "",
      cli_order: null,
      default: "",
      optional: false,
      format: null,
      folder_name: null,
      file_count: null,
      section_id: "",
      mode: "beginner",
      subtype: null,
      depth: null,
      timepoints: null,
      tiled: null,
      pyramidal: null,
      value: null,
    },
  },
  parameters: [],
  display_only: [],
  exec_function: {
    name: "",
    script: "",
    module: "",
    cli_command: "",
    hidden_args: null,
  },
  docker_image: null,
  algorithm_folder_name: null,
  citations: {
    algorithm: [
      {
        name: "Starrynight indexing module",
        doi: null,
        license: null,
        description: "This module generates an index for the dataset.",
      },
    ],
  },
  results: [],
};
