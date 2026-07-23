import io
import random

import numpy as np
from PIL import Image, ImageFilter

from .schemas import Degradation


def apply_degradations(
    image: Image.Image, rng: random.Random, config: dict
) -> tuple[Image.Image, list[Degradation]]:
    result = image
    applied: list[Degradation] = []
    if rng.random() < config["blur_probability"]:
        severity = round(rng.uniform(0.12, 0.72), 2)
        result = result.filter(ImageFilter.GaussianBlur(radius=severity * 2.2))
        applied.append(Degradation(type="blur", severity=severity))
    if rng.random() < config["noise_probability"]:
        severity = round(rng.uniform(0.08, 0.45), 2)
        arr = np.asarray(result).astype(np.float32)
        noise_rng = np.random.default_rng(rng.randrange(2**32))
        arr = np.clip(arr + noise_rng.normal(0, 22 * severity, arr.shape), 0, 255).astype(np.uint8)
        result = Image.fromarray(arr)
        applied.append(Degradation(type="noise", severity=severity))
    if rng.random() < config["jpeg_probability"]:
        severity = round(rng.uniform(0.15, 0.78), 2)
        buffer = io.BytesIO()
        result.save(buffer, format="JPEG", quality=max(28, int(96 - severity * 65)))
        buffer.seek(0)
        result = Image.open(buffer).convert("RGB")
        applied.append(Degradation(type="jpeg", severity=severity))
    return result, applied
