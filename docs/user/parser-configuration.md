# Parser Configuration

This guide explains how to configure and customize path parsers in StarryNight to work with your own data organization.

## Understanding Path Parsers

StarryNight uses a grammar-based path parsing system to extract structured metadata from file paths. This allows it to work with a variety of file organization schemes.

### How Path Parsing Works

1. **Grammar Definition**: A grammar file (`.lark`) defines the rules for interpreting file paths
2. **Transformer**: A transformer class converts the parsed structure into usable metadata
3. **Index Generation**: The parsed metadata is stored in a structured index

## The Default Parser

StarryNight includes a default parser ("vincent") that expects paths matching this pattern:

```
[dataset]/Source[source_id]/Batch[batch_id]/images/[plate_id]/[experiment_id]/Well[well_id]_Point[site_id]_[index]_Channel[channels]_Seq[sequence].ome.tiff
```

### Understanding the Grammar File

The default grammar file (`path_parser_vincent.lark`) defines rules for parsing file paths:

```
start: sep? dataset_id sep source_id sep _root_dir

_root_dir: batch_id sep (_images_root_dir | _illum_root_dir | _images_aligned_root_dir | _workspace_root_dir)

_images_root_dir: "images"i sep plate_id sep _plate_root_dir
...
```

Each rule identifies specific components of the path, such as dataset ID, batch ID, plate ID, etc.

## Customizing the Parser

### Option 1: Using CLI Parameters

When generating an index, you can specify a custom parser path:

```sh
starrynight index gen -i ./workspace/inventory/inventory.parquet \
                      -o ./workspace/index/ \
                      --parser /path/to/custom/parser.lark
```

### Option 2: Creating a Custom Grammar File

To create a custom parser for your own file organization:

1. **Create a grammar file** based on your file organization pattern
2. **Test your grammar** with sample file paths
3. **Use it when generating the index**

### Example: Custom Grammar File

Here's an example grammar file for a different file organization pattern:

```
// Custom grammar for example_lab file organization
start: sep? project_name sep experiment_name sep plate_id sep _image_file

_image_file: well_id "_" site_id "_" channel "_" cycle_id "." extension

project_name: stringwithdashcommaspace
experiment_name: stringwithdashcommaspace
plate_id: string
well_id: (LETTER | DIGIT)~2
site_id: DIGIT~1..4
channel: stringwithdash
cycle_id: DIGIT~1..2
extension: stringwithdots

string: (LETTER | DIGIT)+
stringwithdash: (string | "-")+
stringwithdashcommaspace: ( string | "-" | "_" | "," | " " )+
stringwithdots: ( string | "." )+
DIGIT: "0".."9"

%import common.LETTER
```

This would parse paths like:
```
MyProject/Experiment-2023-05/Plate1/A1_01_DAPI_01.tiff
```

## Advanced: Creating Custom Transformers

For even more customization, you can create your own transformer class:

1. Extend the `BaseTransformer` class
2. Override methods for each grammar rule
3. Register your transformer with the system

Example:
```python
from starrynight.parsers.common import BaseTransformer

class MyCustomTransformer(BaseTransformer):
    """Custom transformer for my file organization."""

    def __init__(self) -> None:
        super().__init__()
        self.channel_dict: dict[str, list[str]] = {"channel_dict": []}

    def project_name(self, items) -> dict:
        return {"project_name": items[0]}

    def experiment_name(self, items) -> dict:
        return {"experiment_name": items[0]}

    # Other methods for each rule in your grammar
```

## Best Practices

When configuring parsers:

1. **Start Simple**: Begin with basic grammar rules and refine them
2. **Test Thoroughly**: Validate your parser with representative file paths
3. **Handle Edge Cases**: Consider special file naming conventions
4. **Document Your Schema**: Document your file organization for reference

## Troubleshooting

Common issues with parsers:

- **Parsing Errors**: Check if your file paths match your grammar rules
- **Missing Metadata**: Ensure your grammar extracts all needed metadata fields
- **Performance Issues**: Very complex grammars might be slower to parse

## Next Steps

After configuring your parser:

- Generate an inventory and index with your custom parser
- Validate the index contains the expected metadata
- Proceed with your StarryNight workflow
