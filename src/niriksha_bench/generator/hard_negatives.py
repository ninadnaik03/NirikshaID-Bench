import io
import random

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

from .renderer import _font


def _local_jpeg(image: Image.Image, bbox: list[int], quality: int) -> Image.Image:
    result = image.copy()
    crop = result.crop(tuple(bbox))
    buffer = io.BytesIO()
    crop.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    result.paste(Image.open(buffer).convert("RGB"), (bbox[0], bbox[1]))
    return result


def apply_hard_negative(
    image: Image.Image,
    kind: str,
    fields: dict[str, str],
    bboxes: dict[str, list[int]],
    rng: random.Random,
) -> tuple[Image.Image, list[int] | None]:
    result = image.copy()
    field = rng.choice(["full_name", "guardian_name", "identity_number"])
    bbox = bboxes[field]
    if kind == "slight_font_variation":
        draw = ImageDraw.Draw(result)
        draw.rectangle(tuple(bbox), fill="#F5F7F8")
        draw.text((bbox[0] + 4, bbox[1] + 2), fields[field], font=_font(24, field == "full_name"), fill="#102A43")
    elif kind == "uneven_jpeg_blocks":
        stripe = [260, 155, 760, 475]
        result = _local_jpeg(result, stripe, 43)
        bbox = stripe
    elif kind == "alignment_shift":
        crop = result.crop(tuple(bbox))
        ImageDraw.Draw(result).rectangle(tuple(bbox), fill="#F5F7F8")
        result.paste(crop, (bbox[0] + 2, bbox[1] + 1))
    elif kind == "scan_shadow":
        array = np.asarray(result).astype(np.float32)
        gradient = np.linspace(0.72, 1.0, array.shape[1], dtype=np.float32)[None, :, None]
        result = Image.fromarray(np.clip(array * gradient, 0, 255).astype(np.uint8))
        bbox = [0, 0, 260, result.height]
    elif kind == "low_contrast":
        result = ImageEnhance.Contrast(result).enhance(0.63)
        bbox = None
    elif kind == "printer_noise":
        draw = ImageDraw.Draw(result)
        for _ in range(1250):
            x, y = rng.randrange(result.width), rng.randrange(result.height)
            shade = rng.randrange(95, 190)
            draw.point((x, y), fill=(shade, shade, shade))
        bbox = None
    elif kind == "text_compression":
        result = _local_jpeg(result, bbox, 25)
    elif kind == "kerning_variation":
        draw = ImageDraw.Draw(result)
        draw.rectangle(tuple(bbox), fill="#F5F7F8")
        x = bbox[0] + 4
        font = _font(25, field in {"full_name", "identity_number"})
        for character in fields[field]:
            draw.text((x, bbox[1] + 2), character, font=font, fill="#102A43")
            char_box = draw.textbbox((0, 0), character, font=font)
            x += max(8, char_box[2] - char_box[0] + rng.choice([-1, 0, 1]))
    else:
        raise ValueError(f"Unknown hard-negative type: {kind}")
    return result, bbox
