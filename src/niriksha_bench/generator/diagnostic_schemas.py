from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .schemas import Degradation, DocumentFields, TamperType


class CounterfactualPair(BaseModel):
    pair_id: str = Field(pattern=r"^pair_\d{4}$")
    genuine_doc_id: str
    tampered_doc_id: str
    genuine_image_path: str
    tampered_image_path: str
    source_fields: DocumentFields
    tampered_displayed_fields: DocumentFields
    tamper_type: TamperType
    tampered_field: str
    tamper_bbox: list[int]
    degradations: list[Degradation]
    intervention_seed: int
    degradation_seed: int
    generator_version: str

    @model_validator(mode="after")
    def require_real_intervention(self) -> "CounterfactualPair":
        if self.tamper_type == "none":
            raise ValueError("Counterfactual pairs require a tamper intervention")
        if self.genuine_image_path == self.tampered_image_path:
            raise ValueError("Pair paths must be distinct")
        return self


HardNegativeType = Literal[
    "slight_font_variation",
    "uneven_jpeg_blocks",
    "alignment_shift",
    "scan_shadow",
    "low_contrast",
    "printer_noise",
    "text_compression",
    "kerning_variation",
]


class HardNegativeRecord(BaseModel):
    doc_id: str = Field(pattern=r"^hardneg_\d{4}$")
    image_path: str
    fields: DocumentFields
    hard_negative_type: HardNegativeType
    suspicious_bbox: list[int] | None
    tampered: Literal[False] = False
    seed: int
    generator_version: str
