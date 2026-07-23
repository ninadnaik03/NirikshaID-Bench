import random

from PIL import Image, ImageDraw

from .renderer import _font
from .schemas import DocumentFields


def _changed_character(value: str, rng: random.Random) -> str:
    positions = [i for i, char in enumerate(value) if char.isdigit()]
    pos = rng.choice(positions)
    replacement = rng.choice([d for d in "0123456789" if d != value[pos]])
    return value[:pos] + replacement + value[pos + 1 :]


def apply_tamper(
    image: Image.Image,
    fields: DocumentFields,
    bboxes: dict[str, list[int]],
    tamper_type: str,
    rng: random.Random,
) -> tuple[Image.Image, DocumentFields, str, list[int]]:
    result = image.copy()
    displayed = fields.model_copy(deep=True)
    if tamper_type == "digit_edit":
        field = rng.choice(["identity_number", "date_of_birth"])
        changed = _changed_character(getattr(fields, field), rng)
        setattr(displayed, field, changed)
        bbox = bboxes[field]
        draw = ImageDraw.Draw(result)
        draw.rectangle(tuple(bbox), fill="#F5F7F8")
        draw.text((bbox[0] + 4, bbox[1] + 2), changed, font=_font(25, field == "identity_number"), fill="#102A43")
    elif tamper_type == "font_swap":
        field = rng.choice(["full_name", "guardian_name", "identity_number"])
        bbox = bboxes[field]
        draw = ImageDraw.Draw(result)
        draw.rectangle(tuple(bbox), fill="#F5F7F8")
        draw.text((bbox[0] + 4, bbox[1] + 1), getattr(fields, field), font=_font(22, False), fill="#263238")
    else:
        field = rng.choice(["full_name", "guardian_name", "identity_number"])
        bbox = bboxes[field]
        crop = result.crop(tuple(bbox))
        shifted = crop.resize((crop.width + 8, crop.height))
        draw = ImageDraw.Draw(result)
        draw.rectangle(tuple(bbox), fill="#EEF1F2")
        result.paste(shifted.crop((0, 0, bbox[2] - bbox[0], bbox[3] - bbox[1])), (bbox[0], bbox[1]))
        draw.line((bbox[0], bbox[3] - 1, bbox[2], bbox[3] - 1), fill="#C5CED2", width=2)
    return result, displayed, field, bbox
