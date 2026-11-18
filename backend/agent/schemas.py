
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class FormField(BaseModel):
    """Metadata discovered from a website form."""

    model_config = ConfigDict(extra="forbid")

    tag: Literal["input", "textarea", "select"]

    type: str
    name: str | None = None
    id: str | None = None
    label: str = ""

    placeholder: str | None = None

    required: bool = False
    disabled: bool = False

    checked: bool | None = None

    choice_value: str | None = None

    options: list[dict] = Field(default_factory=list)


class FieldMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_name: str
    field_key: str
    control_type: Literal[
        "text",
        "email",
        "tel",
        "url",
        "number",
        "textarea",
        "checkbox",
        "radio",
        "select",
        "date",
        "password",
    ]

    value: str | bool | None
    reason: str

class FormFillPlan(BaseModel):
    """Complete proposed form-filling plan."""

    model_config = ConfigDict(extra="forbid")

    mappings: list[FieldMapping]

    requires_human_approval: bool = True
