from typing import Literal

from pydantic import BaseModel, Field, model_validator

Split = Literal["train", "validation", "eval_seen", "eval_unseen", "demo_gallery"]
TamperType = Literal["none", "font_swap", "copy_paste_splice", "digit_edit"]


class DocumentFields(BaseModel):
    full_name: str
    guardian_name: str
    date_of_birth: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    identity_number: str = Field(pattern=r"^[A-Z]{3}\d{6}[A-Z]$")
    document_id: str = Field(pattern=r"^SYN-\d{6}$")


class Degradation(BaseModel):
    type: Literal["jpeg", "blur", "noise", "brightness", "perspective"]
    severity: float = Field(ge=0, le=1)


class DocumentLabel(BaseModel):
    doc_id: str = Field(pattern=r"^nid_\d{6}$")
    image_path: str
    fields: DocumentFields
    displayed_fields: DocumentFields
    field_bboxes: dict[str, list[int]]
    tampered: bool
    tamper_type: TamperType
    tampered_field: str | None = None
    tamper_bbox: list[int] | None = None
    degradations: list[Degradation] = []
    split: Split
    seed: int
    generator_version: str

    @model_validator(mode="after")
    def validate_tamper_state(self) -> "DocumentLabel":
        if self.tampered and (
            self.tamper_type == "none" or not self.tampered_field or not self.tamper_bbox
        ):
            raise ValueError("Tampered documents require type, field, and bbox")
        if not self.tampered and (
            self.tamper_type != "none"
            or self.tampered_field is not None
            or self.tamper_bbox is not None
        ):
            raise ValueError("Genuine documents cannot have tamper metadata")
        if self.split in {"train", "validation"} and self.tamper_type == "digit_edit":
            raise ValueError("Held-out digit_edit leaked into a tuning split")
        return self
