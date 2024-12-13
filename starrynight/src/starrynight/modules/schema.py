from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'https://w3id.org/my-org/validate_schema/',
     'description': "Validate each of the incoming Algorithm's spec file",
     'id': 'https://w3id.org/my-org/validate_schema',
     'imports': ['linkml:types'],
     'name': 'validate_schema',
     'prefixes': {'default_range': {'prefix_prefix': 'default_range',
                                    'prefix_reference': 'string'}},
     'source_file': 'validate_schema.yaml',
     'title': 'validate_schema'} )

class TypeEnum(str, Enum):
    """
    Type of the parameters, display_only, results
    """
    integer = "integer"
    float = "float"
    boolean = "boolean"
    checkbox = "checkbox"
    files = "files"
    dropdown = "dropdown"
    radio = "radio"
    textbox = "textbox"


class ModeEnum(str, Enum):
    """
    Mode of the parameters, display_only, results
    """
    beginner = "beginner"
    advanced = "advanced"


class FileTypeEnum(str, Enum):
    """
    Type of Number of files
    """
    single = "single"
    multiple = "multiple"



class Container(ConfiguredBaseModel):
    """
    Container class which holds all the high_level keywords from config.yaml file of specific algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/my-org/validate_schema'})

    parameters: Optional[List[TypeParameter]] = Field(None, description="""Parameters of a specific Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'parameters', 'domain_of': ['Container']} })
    display_only: Optional[List[TypeDisplayOnly]] = Field(None, description="""Display only parameters of a specific Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'display_only', 'domain_of': ['Container']} })
    results: Optional[List[TypeResults]] = Field(None, description="""Results of a specific Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'results', 'domain_of': ['Container']} })
    exec_function: Optional[ExecFunction] = Field(None, description="""Function to execute the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'exec_function', 'domain_of': ['Container']} })
    docker_image: Optional[DockerImage] = Field(None, description="""Description of docker_image for the specific algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'docker_image', 'domain_of': ['Container']} })
    algorithm_folder_name: Optional[str] = Field(None, description="""Main folder name of the algorithm to put the generated files in the folder""", json_schema_extra = { "linkml_meta": {'alias': 'algorithm_folder_name', 'domain_of': ['Container']} })
    citations: TypeCitations = Field(..., description="""Citations of the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'citations', 'domain_of': ['Container']} })


class AbstractUserInterface(ConfiguredBaseModel):
    """
    Abstract class for user interface
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'aliases': ['parameters', 'display_only', 'results'],
         'from_schema': 'https://w3id.org/my-org/validate_schema',
         'rules': [{'description': 'Extra flags needed iff type is checkbox',
                    'postconditions': {'slot_conditions': {'append_value': {'name': 'append_value',
                                                                            'required': False}}},
                    'preconditions': {'slot_conditions': {'type': {'equals_string': 'checkbox',
                                                                   'name': 'type'}}}}]})

    name: str = Field(..., description="""Name of the docker_image, algorithm, parameter, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AbstractUserInterface',
                       'ExecFunction',
                       'DockerImage',
                       'TypeAlgorithmFromCitation']} })
    type: TypeEnum = Field(..., description="""Type of the parameter""", json_schema_extra = { "linkml_meta": {'alias': 'type', 'domain_of': ['AbstractUserInterface']} })
    label: Any = Field(..., description="""Label of the object, but also Radio button's label""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['AbstractUserInterface', 'RadioOptions']} })
    description: Optional[str] = Field(None, description="""Description of the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['AbstractUserInterface', 'TypeAlgorithmFromCitation']} })
    cli_tag: str = Field(..., description="""CLI tag of the object""", json_schema_extra = { "linkml_meta": {'alias': 'cli_tag', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })
    optional: Optional[bool] = Field(None, description="""Optional value of the object""", json_schema_extra = { "linkml_meta": {'alias': 'optional', 'domain_of': ['AbstractUserInterface']} })
    section_id: str = Field(..., description="""Section ID of the object""", json_schema_extra = { "linkml_meta": {'alias': 'section_id', 'domain_of': ['AbstractUserInterface']} })
    mode: ModeEnum = Field(..., description="""Mode of the object""", json_schema_extra = { "linkml_meta": {'alias': 'mode', 'domain_of': ['AbstractUserInterface']} })
    output_dir_set: Optional[bool] = Field(None, description="""Output directory set""", json_schema_extra = { "linkml_meta": {'alias': 'output_dir_set', 'domain_of': ['AbstractUserInterface']} })
    folder_name: Optional[str] = Field(None, description="""Folder name of the object""", json_schema_extra = { "linkml_meta": {'alias': 'folder_name', 'domain_of': ['AbstractUserInterface']} })
    file_count: Optional[FileTypeEnum] = Field(None, description="""Type of Number of files""", json_schema_extra = { "linkml_meta": {'alias': 'file_count', 'domain_of': ['AbstractUserInterface']} })
    options: Optional[List[RadioOptions]] = Field(None, description="""Options of the Radio button in parameters, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'options', 'domain_of': ['AbstractUserInterface']} })
    interactive: Optional[bool] = Field(None, description="""Whether the object is interactive on UI""", json_schema_extra = { "linkml_meta": {'alias': 'interactive', 'domain_of': ['AbstractUserInterface']} })
    append_value: Optional[bool] = Field(None, description="""Append value of the hidden argument""", json_schema_extra = { "linkml_meta": {'alias': 'append_value', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })


class TypeParameter(AbstractUserInterface):
    """
    Parameters of a specific Algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['parameters'],
         'from_schema': 'https://w3id.org/my-org/validate_schema'})

    default: Any = Field(..., description="""Default value of the parameter""", json_schema_extra = { "linkml_meta": {'alias': 'default', 'domain_of': ['TypeParameter', 'TypeDisplayOnly']} })
    cli_order: Optional[int] = Field(None, description="""Order of the CLI arguments""", json_schema_extra = { "linkml_meta": {'alias': 'cli_order', 'domain_of': ['TypeParameter', 'HiddenArgs']} })
    name: str = Field(..., description="""Name of the docker_image, algorithm, parameter, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AbstractUserInterface',
                       'ExecFunction',
                       'DockerImage',
                       'TypeAlgorithmFromCitation']} })
    type: TypeEnum = Field(..., description="""Type of the parameter""", json_schema_extra = { "linkml_meta": {'alias': 'type', 'domain_of': ['AbstractUserInterface']} })
    label: Any = Field(..., description="""Label of the object, but also Radio button's label""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['AbstractUserInterface', 'RadioOptions']} })
    description: Optional[str] = Field(None, description="""Description of the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['AbstractUserInterface', 'TypeAlgorithmFromCitation']} })
    cli_tag: str = Field(..., description="""CLI tag of the object""", json_schema_extra = { "linkml_meta": {'alias': 'cli_tag', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })
    optional: Optional[bool] = Field(None, description="""Optional value of the object""", json_schema_extra = { "linkml_meta": {'alias': 'optional', 'domain_of': ['AbstractUserInterface']} })
    section_id: str = Field(..., description="""Section ID of the object""", json_schema_extra = { "linkml_meta": {'alias': 'section_id', 'domain_of': ['AbstractUserInterface']} })
    mode: ModeEnum = Field(..., description="""Mode of the object""", json_schema_extra = { "linkml_meta": {'alias': 'mode', 'domain_of': ['AbstractUserInterface']} })
    output_dir_set: Optional[bool] = Field(None, description="""Output directory set""", json_schema_extra = { "linkml_meta": {'alias': 'output_dir_set', 'domain_of': ['AbstractUserInterface']} })
    folder_name: Optional[str] = Field(None, description="""Folder name of the object""", json_schema_extra = { "linkml_meta": {'alias': 'folder_name', 'domain_of': ['AbstractUserInterface']} })
    file_count: Optional[FileTypeEnum] = Field(None, description="""Type of Number of files""", json_schema_extra = { "linkml_meta": {'alias': 'file_count', 'domain_of': ['AbstractUserInterface']} })
    options: Optional[List[RadioOptions]] = Field(None, description="""Options of the Radio button in parameters, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'options', 'domain_of': ['AbstractUserInterface']} })
    interactive: Optional[bool] = Field(None, description="""Whether the object is interactive on UI""", json_schema_extra = { "linkml_meta": {'alias': 'interactive', 'domain_of': ['AbstractUserInterface']} })
    append_value: Optional[bool] = Field(None, description="""Append value of the hidden argument""", json_schema_extra = { "linkml_meta": {'alias': 'append_value', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })


class TypeDisplayOnly(AbstractUserInterface):
    """
    Display only parameters of a specific Algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['display_only'],
         'from_schema': 'https://w3id.org/my-org/validate_schema'})

    default: Any = Field(..., description="""Default value of the parameter""", json_schema_extra = { "linkml_meta": {'alias': 'default', 'domain_of': ['TypeParameter', 'TypeDisplayOnly']} })
    name: str = Field(..., description="""Name of the docker_image, algorithm, parameter, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AbstractUserInterface',
                       'ExecFunction',
                       'DockerImage',
                       'TypeAlgorithmFromCitation']} })
    type: TypeEnum = Field(..., description="""Type of the parameter""", json_schema_extra = { "linkml_meta": {'alias': 'type', 'domain_of': ['AbstractUserInterface']} })
    label: Any = Field(..., description="""Label of the object, but also Radio button's label""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['AbstractUserInterface', 'RadioOptions']} })
    description: Optional[str] = Field(None, description="""Description of the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['AbstractUserInterface', 'TypeAlgorithmFromCitation']} })
    cli_tag: str = Field(..., description="""CLI tag of the object""", json_schema_extra = { "linkml_meta": {'alias': 'cli_tag', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })
    optional: Optional[bool] = Field(None, description="""Optional value of the object""", json_schema_extra = { "linkml_meta": {'alias': 'optional', 'domain_of': ['AbstractUserInterface']} })
    section_id: str = Field(..., description="""Section ID of the object""", json_schema_extra = { "linkml_meta": {'alias': 'section_id', 'domain_of': ['AbstractUserInterface']} })
    mode: ModeEnum = Field(..., description="""Mode of the object""", json_schema_extra = { "linkml_meta": {'alias': 'mode', 'domain_of': ['AbstractUserInterface']} })
    output_dir_set: Optional[bool] = Field(None, description="""Output directory set""", json_schema_extra = { "linkml_meta": {'alias': 'output_dir_set', 'domain_of': ['AbstractUserInterface']} })
    folder_name: Optional[str] = Field(None, description="""Folder name of the object""", json_schema_extra = { "linkml_meta": {'alias': 'folder_name', 'domain_of': ['AbstractUserInterface']} })
    file_count: Optional[FileTypeEnum] = Field(None, description="""Type of Number of files""", json_schema_extra = { "linkml_meta": {'alias': 'file_count', 'domain_of': ['AbstractUserInterface']} })
    options: Optional[List[RadioOptions]] = Field(None, description="""Options of the Radio button in parameters, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'options', 'domain_of': ['AbstractUserInterface']} })
    interactive: Optional[bool] = Field(None, description="""Whether the object is interactive on UI""", json_schema_extra = { "linkml_meta": {'alias': 'interactive', 'domain_of': ['AbstractUserInterface']} })
    append_value: Optional[bool] = Field(None, description="""Append value of the hidden argument""", json_schema_extra = { "linkml_meta": {'alias': 'append_value', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })


class TypeResults(AbstractUserInterface):
    """
    Results of a specific Algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['results'],
         'from_schema': 'https://w3id.org/my-org/validate_schema'})

    name: str = Field(..., description="""Name of the docker_image, algorithm, parameter, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AbstractUserInterface',
                       'ExecFunction',
                       'DockerImage',
                       'TypeAlgorithmFromCitation']} })
    type: TypeEnum = Field(..., description="""Type of the parameter""", json_schema_extra = { "linkml_meta": {'alias': 'type', 'domain_of': ['AbstractUserInterface']} })
    label: Any = Field(..., description="""Label of the object, but also Radio button's label""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['AbstractUserInterface', 'RadioOptions']} })
    description: Optional[str] = Field(None, description="""Description of the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['AbstractUserInterface', 'TypeAlgorithmFromCitation']} })
    cli_tag: str = Field(..., description="""CLI tag of the object""", json_schema_extra = { "linkml_meta": {'alias': 'cli_tag', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })
    optional: Optional[bool] = Field(None, description="""Optional value of the object""", json_schema_extra = { "linkml_meta": {'alias': 'optional', 'domain_of': ['AbstractUserInterface']} })
    section_id: str = Field(..., description="""Section ID of the object""", json_schema_extra = { "linkml_meta": {'alias': 'section_id', 'domain_of': ['AbstractUserInterface']} })
    mode: ModeEnum = Field(..., description="""Mode of the object""", json_schema_extra = { "linkml_meta": {'alias': 'mode', 'domain_of': ['AbstractUserInterface']} })
    output_dir_set: Optional[bool] = Field(None, description="""Output directory set""", json_schema_extra = { "linkml_meta": {'alias': 'output_dir_set', 'domain_of': ['AbstractUserInterface']} })
    folder_name: Optional[str] = Field(None, description="""Folder name of the object""", json_schema_extra = { "linkml_meta": {'alias': 'folder_name', 'domain_of': ['AbstractUserInterface']} })
    file_count: Optional[FileTypeEnum] = Field(None, description="""Type of Number of files""", json_schema_extra = { "linkml_meta": {'alias': 'file_count', 'domain_of': ['AbstractUserInterface']} })
    options: Optional[List[RadioOptions]] = Field(None, description="""Options of the Radio button in parameters, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'options', 'domain_of': ['AbstractUserInterface']} })
    interactive: Optional[bool] = Field(None, description="""Whether the object is interactive on UI""", json_schema_extra = { "linkml_meta": {'alias': 'interactive', 'domain_of': ['AbstractUserInterface']} })
    append_value: Optional[bool] = Field(None, description="""Append value of the hidden argument""", json_schema_extra = { "linkml_meta": {'alias': 'append_value', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })


class ExecFunction(ConfiguredBaseModel):
    """
    Function to execute the Algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['exec_function', 'generate_cli_command', 'construct_cli_command'],
         'from_schema': 'https://w3id.org/my-org/validate_schema'})

    name: str = Field(..., description="""Name of the docker_image, algorithm, parameter, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AbstractUserInterface',
                       'ExecFunction',
                       'DockerImage',
                       'TypeAlgorithmFromCitation']} })
    script: str = Field(..., description="""Script to execute the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'script', 'domain_of': ['ExecFunction']} })
    module: str = Field(..., description="""Module to execute the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'module', 'domain_of': ['ExecFunction']} })
    cli_command: str = Field(..., description="""CLI command to execute the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'cli_command', 'domain_of': ['ExecFunction']} })
    hidden_args: Optional[HiddenArgs] = Field(None, description="""Hidden arguments for the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'hidden_args', 'domain_of': ['ExecFunction']} })


class DockerImage(ConfiguredBaseModel):
    """
    Description of docker_image for the specific algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['docker_image'],
         'from_schema': 'https://w3id.org/my-org/validate_schema'})

    org: str = Field(..., description="""Organization of the docker image""", json_schema_extra = { "linkml_meta": {'alias': 'org', 'domain_of': ['DockerImage']} })
    name: str = Field(..., description="""Name of the docker_image, algorithm, parameter, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AbstractUserInterface',
                       'ExecFunction',
                       'DockerImage',
                       'TypeAlgorithmFromCitation']} })
    tag: str = Field(..., description="""Tag of the docker image""", json_schema_extra = { "linkml_meta": {'alias': 'tag', 'domain_of': ['DockerImage']} })


class TypeCitations(ConfiguredBaseModel):
    """
    Citations of the Algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['citations'],
         'from_schema': 'https://w3id.org/my-org/validate_schema'})

    algorithm: List[TypeAlgorithmFromCitation] = Field(..., description="""Algorithm's citations""", json_schema_extra = { "linkml_meta": {'alias': 'algorithm', 'domain_of': ['TypeCitations']} })


class TypeAlgorithmFromCitation(ConfiguredBaseModel):
    """
    Algorithm's citations
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'aliases': ['Algorithm', 'citations'],
         'from_schema': 'https://w3id.org/my-org/validate_schema'})

    name: str = Field(..., description="""Name of the docker_image, algorithm, parameter, display_only, results""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['AbstractUserInterface',
                       'ExecFunction',
                       'DockerImage',
                       'TypeAlgorithmFromCitation']} })
    doi: Optional[str] = Field(None, description="""DOI of the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'doi', 'domain_of': ['TypeAlgorithmFromCitation']} })
    description: Optional[str] = Field(None, description="""Description of the Algorithm""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['AbstractUserInterface', 'TypeAlgorithmFromCitation']} })


class HiddenArgs(ConfiguredBaseModel):
    """
    Hidden arguments for the Algorithm
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/my-org/validate_schema'})

    cli_tag: str = Field(..., description="""CLI tag of the object""", json_schema_extra = { "linkml_meta": {'alias': 'cli_tag', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })
    value: Optional[Any] = Field(None, description="""Value of the hidden argument or RadioButton Option's Value""", json_schema_extra = { "linkml_meta": {'alias': 'value', 'domain_of': ['HiddenArgs', 'RadioOptions']} })
    append_value: Optional[bool] = Field(None, description="""Append value of the hidden argument""", json_schema_extra = { "linkml_meta": {'alias': 'append_value', 'domain_of': ['AbstractUserInterface', 'HiddenArgs']} })
    cli_order: Optional[int] = Field(None, description="""Order of the CLI arguments""", json_schema_extra = { "linkml_meta": {'alias': 'cli_order', 'domain_of': ['TypeParameter', 'HiddenArgs']} })


class RadioOptions(ConfiguredBaseModel):
    """
    Options of the Radio button in parameters, display_only, results
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/my-org/validate_schema'})

    label: Any = Field(..., description="""Label of the object, but also Radio button's label""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['AbstractUserInterface', 'RadioOptions']} })
    value: Optional[Any] = Field(None, description="""Value of the hidden argument or RadioButton Option's Value""", json_schema_extra = { "linkml_meta": {'alias': 'value', 'domain_of': ['HiddenArgs', 'RadioOptions']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Container.model_rebuild()
AbstractUserInterface.model_rebuild()
TypeParameter.model_rebuild()
TypeDisplayOnly.model_rebuild()
TypeResults.model_rebuild()
ExecFunction.model_rebuild()
DockerImage.model_rebuild()
TypeCitations.model_rebuild()
TypeAlgorithmFromCitation.model_rebuild()
HiddenArgs.model_rebuild()
RadioOptions.model_rebuild()

