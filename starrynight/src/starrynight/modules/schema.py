from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    pass


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta(
    {
        "default_prefix": "https://w3id.org/my-org/bilayers_schema/",
        "description": "Validate each of the incoming Algorithm's spec file",
        "id": "https://w3id.org/my-org/bilayers_schema",
        "imports": ["linkml:types"],
        "name": "bilayers_schema",
        "prefixes": {
            "default_range": {
                "prefix_prefix": "default_range",
                "prefix_reference": "string",
            }
        },
        "source_file": "/home/ank/workspace/hub/broad/starrynight/starrynight/src/starrynight/modules/validate_schema.yaml",
        "title": "bilayers_schema",
    }
)


class TypeEnum(str, Enum):
    """
    Type of the parameters, display_only
    """

    integer = "integer"
    float = "float"
    boolean = "boolean"
    checkbox = "checkbox"
    dropdown = "dropdown"
    radio = "radio"
    textbox = "textbox"
    image = "image"
    measurement = "measurement"
    array = "array"
    file = "file"
    executable = "executable"
    notebook = "notebook"
    dir = "dir"


class ModeEnum(str, Enum):
    """
    Mode of the parameters, display_only
    """

    beginner = "beginner"
    advanced = "advanced"


class FileTypeEnum(str, Enum):
    """
    Type of Number of files
    """

    single = "single"
    multiple = "multiple"


class SubTypeEnum(str, Enum):
    """
    Subtype of the inputs and outputs, iff type is image
    """

    grayscale = "grayscale"
    color = "color"
    binary = "binary"
    labeled = "labeled"


class SpecContainer(ConfiguredBaseModel):
    """
    SpecContainer class which holds all the high_level keywords from config.yaml file of specific algorithm
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/my-org/bilayers_schema"}
    )

    inputs: dict[str, TypeInput] = Field(
        ...,
        description="""Inputs to the algorithm from the last step of the workflow""",
        json_schema_extra={
            "linkml_meta": {"alias": "inputs", "domain_of": ["SpecContainer"]}
        },
    )
    outputs: dict[str, TypeOutput] = Field(
        ...,
        description="""Outputs of the algorithm to the next step in the workflow""",
        json_schema_extra={
            "linkml_meta": {"alias": "outputs", "domain_of": ["SpecContainer"]}
        },
    )
    parameters: List[TypeParameter] = Field(
        ...,
        description="""Parameters of a specific Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parameters",
                "domain_of": ["SpecContainer"],
            }
        },
    )
    display_only: Optional[List[TypeDisplayOnly]] = Field(
        None,
        description="""Display only parameters of a specific Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "display_only",
                "domain_of": ["SpecContainer"],
            }
        },
    )
    exec_function: ExecFunction = Field(
        ...,
        description="""Function to execute the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "exec_function",
                "domain_of": ["SpecContainer"],
            }
        },
    )
    docker_image: Optional[DockerImage] = Field(
        None,
        description="""Description of docker_image for the specific algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "docker_image",
                "domain_of": ["SpecContainer"],
            }
        },
    )
    algorithm_folder_name: Optional[str] = Field(
        None,
        description="""Main folder name of the algorithm to put the generated files in the folder""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "algorithm_folder_name",
                "domain_of": ["SpecContainer"],
            }
        },
    )
    citations: TypeCitations = Field(
        ...,
        description="""Citations of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "citations",
                "domain_of": ["SpecContainer"],
            }
        },
    )
    # remove me later
    results: list = []


class AbstractWorkflowDetails(ConfiguredBaseModel):
    """
    Abstract class for details needed to fit config in the workflow
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "abstract": True,
            "aliases": ["inputs", "outputs"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
        }
    )

    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    type: TypeEnum = Field(
        ...,
        description="""Type of the inputs, parameters and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "type",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    label: Any = Field(
        ...,
        description="""Label of the object, but also Radio button's label""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "RadioOptions",
                ],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""Description of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    cli_tag: str = Field(
        ...,
        description="""CLI tag of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_tag",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    cli_order: Optional[int] = Field(
        None,
        description="""Order of the CLI arguments""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_order",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    default: Any = Field(
        ...,
        description="""Default value of the parameter""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "default",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "TypeDisplayOnly",
                ],
            }
        },
    )
    optional: bool = Field(
        ...,
        description="""Optional value of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "optional",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    format: Optional[List[str]] = Field(
        None,
        description="""Format of the inputs and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "format",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    folder_name: Optional[str] = Field(
        None,
        description="""Folder name of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "folder_name",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    file_count: Optional[FileTypeEnum] = Field(
        None,
        description="""Type of Number of files""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_count",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    section_id: str = Field(
        ...,
        description="""Section ID of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "section_id",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    mode: ModeEnum = Field(
        ...,
        description="""Mode of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "mode",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    subtype: Optional[List[SubTypeEnum]] = Field(
        None,
        description="""Subtype of the inputs and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subtype",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    depth: Optional[bool] = Field(
        None,
        description="""whether z-dimension i.e. depth is accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "depth",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    timepoints: Optional[bool] = Field(
        None,
        description="""whether t-dimension i.e. timepoints are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "timepoints",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    tiled: Optional[bool] = Field(
        None,
        description="""whether tiled images are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "tiled",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    pyramidal: Optional[bool] = Field(
        None,
        description="""whether pyramidal images are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "pyramidal",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )


class TypeInput(AbstractWorkflowDetails):
    """
    Inputs to the algorithm from the last step of the workflow
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": ["inputs"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
            "rules": [
                {
                    "description": "Extra flags needed iff type is image",
                    "postconditions": {
                        "slot_conditions": {
                            "depth": {"name": "depth", "required": True},
                            "pyramidal": {
                                "name": "pyramidal",
                                "required": True,
                            },
                            "subtype": {"name": "subtype", "required": True},
                            "tiled": {"name": "tiled", "required": True},
                            "timepoints": {
                                "name": "timepoints",
                                "required": True,
                            },
                        }
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "type": {"equals_string": "image", "name": "type"}
                        }
                    },
                }
            ],
        }
    )

    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    type: TypeEnum = Field(
        ...,
        description="""Type of the inputs, parameters and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "type",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    label: Any = Field(
        "",
        description="""Label of the object, but also Radio button's label""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "RadioOptions",
                ],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""Description of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    cli_tag: str = Field(
        "",
        description="""CLI tag of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_tag",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    cli_order: Optional[int] = Field(
        None,
        description="""Order of the CLI arguments""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_order",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    default: Any = Field(
        "",
        description="""Default value of the parameter""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "default",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "TypeDisplayOnly",
                ],
            }
        },
    )
    optional: bool = Field(
        ...,
        description="""Optional value of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "optional",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    format: Optional[List[str]] = Field(
        None,
        description="""Format of the inputs and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "format",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    folder_name: Optional[str] = Field(
        None,
        description="""Folder name of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "folder_name",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    file_count: Optional[FileTypeEnum] = Field(
        None,
        description="""Type of Number of files""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_count",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    section_id: str = Field(
        "",
        description="""Section ID of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "section_id",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    mode: ModeEnum = Field(
        ModeEnum.beginner,
        description="""Mode of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "mode",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    subtype: Optional[List[SubTypeEnum]] = Field(
        None,
        description="""Subtype of the inputs and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subtype",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    depth: Optional[bool] = Field(
        None,
        description="""whether z-dimension i.e. depth is accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "depth",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    timepoints: Optional[bool] = Field(
        None,
        description="""whether t-dimension i.e. timepoints are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "timepoints",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    tiled: Optional[bool] = Field(
        None,
        description="""whether tiled images are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "tiled",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    pyramidal: Optional[bool] = Field(
        None,
        description="""whether pyramidal images are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "pyramidal",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )

    # Added for starrynight
    value: Any = Field(None, description="""Value of the input""")


class TypeOutput(AbstractWorkflowDetails):
    """
    Outputs of the algorithm to the next step in the workflow
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": ["outputs"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
            "rules": [
                {
                    "description": "Extra flags needed iff type is image",
                    "postconditions": {
                        "slot_conditions": {
                            "depth": {"name": "depth", "required": True},
                            "pyramidal": {
                                "name": "pyramidal",
                                "required": True,
                            },
                            "subtype": {"name": "subtype", "required": True},
                            "tiled": {"name": "tiled", "required": True},
                            "timepoints": {
                                "name": "timepoints",
                                "required": True,
                            },
                        }
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "type": {"equals_string": "image", "name": "type"}
                        }
                    },
                }
            ],
        }
    )

    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    type: TypeEnum = Field(
        ...,
        description="""Type of the inputs, parameters and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "type",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    label: Any = Field(
        "",
        description="""Label of the object, but also Radio button's label""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "RadioOptions",
                ],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""Description of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    cli_tag: str = Field(
        "",
        description="""CLI tag of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_tag",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    cli_order: Optional[int] = Field(
        None,
        description="""Order of the CLI arguments""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_order",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    default: Any = Field(
        "",
        description="""Default value of the parameter""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "default",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "TypeDisplayOnly",
                ],
            }
        },
    )
    optional: bool = Field(
        ...,
        description="""Optional value of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "optional",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    format: Optional[List[str]] = Field(
        None,
        description="""Format of the inputs and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "format",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    folder_name: Optional[str] = Field(
        None,
        description="""Folder name of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "folder_name",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    file_count: Optional[FileTypeEnum] = Field(
        None,
        description="""Type of Number of files""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "file_count",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    section_id: str = Field(
        "",
        description="""Section ID of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "section_id",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    mode: ModeEnum = Field(
        ModeEnum.beginner,
        description="""Mode of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "mode",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    subtype: Optional[List[SubTypeEnum]] = Field(
        None,
        description="""Subtype of the inputs and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "subtype",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    depth: Optional[bool] = Field(
        None,
        description="""whether z-dimension i.e. depth is accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "depth",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    timepoints: Optional[bool] = Field(
        None,
        description="""whether t-dimension i.e. timepoints are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "timepoints",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    tiled: Optional[bool] = Field(
        None,
        description="""whether tiled images are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "tiled",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )
    pyramidal: Optional[bool] = Field(
        None,
        description="""whether pyramidal images are accepted via tool""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "pyramidal",
                "domain_of": ["AbstractWorkflowDetails"],
            }
        },
    )

    # Added for starrynight
    value: Any = Field(None, description="""Value of the output""")


class AbstractUserInterface(ConfiguredBaseModel):
    """
    Abstract class for user interface
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "abstract": True,
            "aliases": ["parameters", "display_only"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
            "rules": [
                {
                    "description": "Extra flags needed iff type is checkbox",
                    "postconditions": {
                        "slot_conditions": {
                            "append_value": {
                                "name": "append_value",
                                "required": True,
                            }
                        }
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "type": {
                                "equals_string": "checkbox",
                                "name": "type",
                            }
                        }
                    },
                },
                {
                    "description": "Extra flags needed iff type is radio",
                    "postconditions": {
                        "slot_conditions": {
                            "options": {"name": "options", "required": True}
                        }
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "type": {"equals_string": "radio", "name": "type"}
                        }
                    },
                },
                {
                    "description": "Extra flags needed iff type is dropdown",
                    "postconditions": {
                        "slot_conditions": {
                            "multiselect": {
                                "name": "multiselect",
                                "required": True,
                            },
                            "options": {"name": "options", "required": True},
                        }
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "type": {
                                "equals_string": "dropdown",
                                "name": "type",
                            }
                        }
                    },
                },
            ],
        }
    )

    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    type: TypeEnum = Field(
        ...,
        description="""Type of the inputs, parameters and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "type",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    label: Any = Field(
        ...,
        description="""Label of the object, but also Radio button's label""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "RadioOptions",
                ],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""Description of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    optional: bool = Field(
        ...,
        description="""Optional value of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "optional",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    section_id: str = Field(
        ...,
        description="""Section ID of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "section_id",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    mode: ModeEnum = Field(
        ...,
        description="""Mode of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "mode",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    output_dir_set: Optional[bool] = Field(
        None,
        description="""Output directory set""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "output_dir_set",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    options: Optional[List[RadioOptions]] = Field(
        None,
        description="""Options of the Radio button in parameters, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "options",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    interactive: Optional[bool] = Field(
        None,
        description="""Whether the object is interactive on UI""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "interactive",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    append_value: Optional[bool] = Field(
        None,
        description="""Append value of the hidden argument""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "append_value",
                "domain_of": ["AbstractUserInterface", "HiddenArgs"],
            }
        },
    )
    multiselect: Optional[bool] = Field(
        None,
        description="""Multiselect value of the dropdown""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "multiselect",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )


class TypeParameter(AbstractUserInterface):
    """
    Parameters of a specific Algorithm
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": ["parameters"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
        }
    )

    default: Any = Field(
        ...,
        description="""Default value of the parameter""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "default",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "TypeDisplayOnly",
                ],
            }
        },
    )
    cli_tag: str = Field(
        ...,
        description="""CLI tag of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_tag",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    cli_order: Optional[int] = Field(
        None,
        description="""Order of the CLI arguments""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_order",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    type: TypeEnum = Field(
        ...,
        description="""Type of the inputs, parameters and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "type",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    label: Any = Field(
        ...,
        description="""Label of the object, but also Radio button's label""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "RadioOptions",
                ],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""Description of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    optional: bool = Field(
        ...,
        description="""Optional value of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "optional",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    section_id: str = Field(
        ...,
        description="""Section ID of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "section_id",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    mode: ModeEnum = Field(
        ...,
        description="""Mode of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "mode",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    output_dir_set: Optional[bool] = Field(
        None,
        description="""Output directory set""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "output_dir_set",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    options: Optional[List[RadioOptions]] = Field(
        None,
        description="""Options of the Radio button in parameters, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "options",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    interactive: Optional[bool] = Field(
        None,
        description="""Whether the object is interactive on UI""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "interactive",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    append_value: Optional[bool] = Field(
        None,
        description="""Append value of the hidden argument""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "append_value",
                "domain_of": ["AbstractUserInterface", "HiddenArgs"],
            }
        },
    )
    multiselect: Optional[bool] = Field(
        None,
        description="""Multiselect value of the dropdown""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "multiselect",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )


class TypeDisplayOnly(AbstractUserInterface):
    """
    Display only parameters of a specific Algorithm
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": ["display_only"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
        }
    )

    default: Any = Field(
        ...,
        description="""Default value of the parameter""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "default",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "TypeDisplayOnly",
                ],
            }
        },
    )
    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    type: TypeEnum = Field(
        ...,
        description="""Type of the inputs, parameters and outputs""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "type",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    label: Any = Field(
        ...,
        description="""Label of the object, but also Radio button's label""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "RadioOptions",
                ],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""Description of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    optional: bool = Field(
        ...,
        description="""Optional value of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "optional",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    section_id: str = Field(
        ...,
        description="""Section ID of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "section_id",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    mode: ModeEnum = Field(
        ...,
        description="""Mode of the object""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "mode",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                ],
            }
        },
    )
    output_dir_set: Optional[bool] = Field(
        None,
        description="""Output directory set""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "output_dir_set",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    options: Optional[List[RadioOptions]] = Field(
        None,
        description="""Options of the Radio button in parameters, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "options",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    interactive: Optional[bool] = Field(
        None,
        description="""Whether the object is interactive on UI""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "interactive",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )
    append_value: Optional[bool] = Field(
        None,
        description="""Append value of the hidden argument""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "append_value",
                "domain_of": ["AbstractUserInterface", "HiddenArgs"],
            }
        },
    )
    multiselect: Optional[bool] = Field(
        None,
        description="""Multiselect value of the dropdown""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "multiselect",
                "domain_of": ["AbstractUserInterface"],
            }
        },
    )


class ExecFunction(ConfiguredBaseModel):
    """
    Function to execute the Algorithm
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": [
                "exec_function",
                "generate_cli_command",
                "construct_cli_command",
            ],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
        }
    )

    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    script: str = Field(
        ...,
        description="""Script to execute the Algorithm""",
        json_schema_extra={
            "linkml_meta": {"alias": "script", "domain_of": ["ExecFunction"]}
        },
    )
    module: str = Field(
        ...,
        description="""Module to execute the Algorithm""",
        json_schema_extra={
            "linkml_meta": {"alias": "module", "domain_of": ["ExecFunction"]}
        },
    )
    cli_command: str = Field(
        ...,
        description="""CLI command to execute the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_command",
                "domain_of": ["ExecFunction"],
            }
        },
    )
    hidden_args: Optional[List[HiddenArgs]] = Field(
        None,
        description="""Hidden arguments for the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "hidden_args",
                "domain_of": ["ExecFunction"],
            }
        },
    )


class DockerImage(ConfiguredBaseModel):
    """
    Description of docker_image for the specific algorithm
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": ["docker_image"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
        }
    )

    org: str = Field(
        ...,
        description="""Organization of the docker image""",
        json_schema_extra={
            "linkml_meta": {"alias": "org", "domain_of": ["DockerImage"]}
        },
    )
    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    tag: str = Field(
        ...,
        description="""Tag of the docker image""",
        json_schema_extra={
            "linkml_meta": {"alias": "tag", "domain_of": ["DockerImage"]}
        },
    )
    platform: str = Field(
        ...,
        description="""Platform on which the docker image was built""",
        json_schema_extra={
            "linkml_meta": {"alias": "platform", "domain_of": ["DockerImage"]}
        },
    )


class TypeCitations(ConfiguredBaseModel):
    """
    Citations of the Algorithm
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": ["citations"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
        }
    )

    algorithm: List[TypeAlgorithmFromCitation] = Field(
        ...,
        description="""Algorithm's citations""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "algorithm",
                "domain_of": ["TypeCitations"],
            }
        },
    )


class TypeAlgorithmFromCitation(ConfiguredBaseModel):
    """
    Algorithm's citations
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "aliases": ["Algorithm", "citations"],
            "from_schema": "https://w3id.org/my-org/bilayers_schema",
        }
    )

    name: str = Field(
        ...,
        description="""Name of the docker_image, algorithm, parameter, display_only""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "ExecFunction",
                    "DockerImage",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )
    doi: Optional[str] = Field(
        None,
        description="""DOI of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "doi",
                "domain_of": ["TypeAlgorithmFromCitation"],
            }
        },
    )
    license: Optional[str] = Field(
        None,
        description="""License of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "license",
                "domain_of": ["TypeAlgorithmFromCitation"],
            }
        },
    )
    description: Optional[str] = Field(
        None,
        description="""Description of the Algorithm""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "TypeAlgorithmFromCitation",
                ],
            }
        },
    )


class HiddenArgs(ConfiguredBaseModel):
    """
    Hidden arguments for the Algorithm
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/my-org/bilayers_schema"}
    )

    cli_tag: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_tag",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )
    value: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "value",
                "domain_of": ["HiddenArgs", "RadioOptions"],
            }
        },
    )
    append_value: Optional[bool] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "append_value",
                "domain_of": ["AbstractUserInterface", "HiddenArgs"],
            }
        },
    )
    cli_order: Optional[int] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "cli_order",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "TypeParameter",
                    "HiddenArgs",
                ],
            }
        },
    )


class RadioOptions(ConfiguredBaseModel):
    """
    Options of the Radio button in parameters, display_only
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/my-org/bilayers_schema"}
    )

    label: Any = Field(
        ...,
        description="""Label of the object, but also Radio button's label""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "label",
                "domain_of": [
                    "AbstractWorkflowDetails",
                    "AbstractUserInterface",
                    "RadioOptions",
                ],
            }
        },
    )
    value: Optional[Any] = Field(
        None,
        description="""Value of the hidden argument or RadioButton Option's Value""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "value",
                "domain_of": ["HiddenArgs", "RadioOptions"],
            }
        },
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
SpecContainer.model_rebuild()
AbstractWorkflowDetails.model_rebuild()
TypeInput.model_rebuild()
TypeOutput.model_rebuild()
AbstractUserInterface.model_rebuild()
TypeParameter.model_rebuild()
TypeDisplayOnly.model_rebuild()
ExecFunction.model_rebuild()
DockerImage.model_rebuild()
TypeCitations.model_rebuild()
TypeAlgorithmFromCitation.model_rebuild()
HiddenArgs.model_rebuild()
RadioOptions.model_rebuild()
