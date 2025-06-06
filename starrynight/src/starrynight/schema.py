"""Schema module."""

from pathlib import Path
from typing import Annotated

from cloudpathlib import CloudPath
from cpgdata.measurement import get_is_dir, get_key_parts
from cpgdata.parser import ParsedPrefix, WorkspaceFolder
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, computed_field


class DataConfig(BaseModel):
    """Data configuration schema."""

    dataset_path: Path | CloudPath
    storage_path: Path | CloudPath
    workspace_path: Path | CloudPath


class MeasuredInventory(ParsedPrefix):
    """Schema for measured inventory.

    Attributes
    ----------
    is_parsing_error : bool
        Whether parsing resulted in an error.
    errors : str | None
        Error message if parsing failed.
    is_dir : Annotated[bool, BeforeValidator(get_is_dir)]
        Whether the key represents a directory (validated).
    key_parts : Annotated[list[str], BeforeValidator(get_key_parts)]
        List of parts of the key from validation.

    Model configuration
    -------------------
    model_config : ConfigDict
        Pydantic model configuration.

    Computed properties
    -------------------
    workspace_dir : str | None (computed)
        Computed value for workspace directory.

    Methods
    -------
    get_all_fields() -> dict
        Returns a dictionary containing all fields including computed fields.

    gen_error_entry(obj_key: str, e: Exception) -> MeasuredInventory (static)
        Generates an error entry from the parsed object.

    """

    is_parsing_error: bool = Field(default=False)
    errors: str | None = Field(default=None)
    is_dir: Annotated[bool, BeforeValidator(get_is_dir)] = Field(
        validation_alias="key", default=False
    )
    key_parts: Annotated[
        list[str],
        BeforeValidator(get_key_parts),
    ] = Field(validation_alias="key", default=[])

    # Model configuration
    model_config = ConfigDict(populate_by_name=True)

    @computed_field(return_type=str | None)
    @property
    def workspace_dir(self: "MeasuredInventory") -> str | None:
        """Computed workspace directory value.

        Returns
        -------
        Optional[str]
            Computed workspace directory value.

        """
        workspace_dir = self.workspace_root_dir
        workspace_dir = str(workspace_dir).split("/")[0]
        return WorkspaceFolder(workspace_dir).value

    def get_all_fields(self: "MeasuredInventory") -> dict:
        """Get all the fields of the model.

        Returns
        -------
        dict
            A dict with field key and FieldInfo or ComputedFieldInfo.

        """
        model_fields = self.model_fields
        return {**model_fields, **self.model_computed_fields}

    @staticmethod
    def gen_error_entry(obj_key: str, e: Exception) -> "MeasuredInventory":
        """Generate an error entry for the parsed object.

        Parameters
        ----------
        obj_key : str
            Object key.
        e : Exception
            Pydantic validation error.

        Returns
        -------
        "MeasuredPrefix"
           Validation error as a parsed object.

        """
        print(f"I am called with the error {e}")
        return MeasuredInventory.model_construct(
            obj_key=obj_key,
            is_parsing_error=True,
            errors=str(e),
        )
