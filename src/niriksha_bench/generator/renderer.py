import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .schemas import DocumentFields

WIDTH, HEIGHT = 960, 600


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def avatar(seed: int, size: tuple[int, int] = (190, 220)) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGB", size, rng.choice(["#DCEEF2", "#E7E3F2", "#F4E5D3"]))
    draw = ImageDraw.Draw(image)
    cx = size[0] // 2
    tone = rng.choice(["#8B5E3C", "#A56F4F", "#6E4932", "#C08A67"])
    shirt = rng.choice(["#1E5B6E", "#694A7A", "#345995", "#6A7B42"])
    draw.ellipse((cx - 47, 32, cx + 47, 126), fill=tone)
    draw.polygon([(25, size[1]), (45, 142), (cx, 118), (size[0] - 45, 142), (size[0] - 25, size[1])], fill=shirt)
    draw.arc((cx - 18, 80, cx + 18, 108), 15, 165, fill="#4A2E22", width=2)
    draw.ellipse((cx - 25, 66, cx - 19, 72), fill="#1A1A1A")
    draw.ellipse((cx + 19, 66, cx + 25, 72), fill="#1A1A1A")
    return image


def render(fields: DocumentFields, seed: int) -> tuple[Image.Image, dict[str, list[int]]]:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#F5F7F8")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, WIDTH - 8, HEIGHT - 8), radius=30, outline="#123B4A", width=5)
    draw.rectangle((0, 0, 22, HEIGHT), fill="#00A6A6")
    draw.polygon([(680, 0), (960, 0), (960, 185)], fill="#DDEFF0")
    draw.polygon([(760, 600), (960, 430), (960, 600)], fill="#FFB703")
    draw.text((55, 42), "NIRIKSHA CIVIC RECORDS", font=_font(28, True), fill="#102A43")
    draw.text((55, 84), "RESIDENT IDENTITY RECORD", font=_font(17), fill="#46616E")
    draw.text((730, 48), "NID", font=_font(48, True), fill="#00A6A6")
    photo = avatar(seed)
    image.paste(photo, (56, 168))
    draw.rounded_rectangle((54, 166, 248, 390), radius=12, outline="#7996A3", width=3)
    draw.text((74, 410), "PROCEDURAL AVATAR", font=_font(12, True), fill="#6B7C85")
    values = fields.model_dump()
    labels = [
        ("full_name", "FULL NAME", 300, 166),
        ("guardian_name", "GUARDIAN NAME", 300, 246),
        ("date_of_birth", "DATE OF BIRTH", 300, 326),
        ("identity_number", "IDENTITY NUMBER", 300, 406),
        ("document_id", "DOCUMENT ID", 300, 486),
    ]
    bboxes: dict[str, list[int]] = {}
    for key, label, x, y in labels:
        draw.text((x, y), label, font=_font(13, True), fill="#67808B")
        value = values[key]
        font = _font(25, key in {"full_name", "identity_number"})
        value_y = y + 23
        box = draw.textbbox((x, value_y), value, font=font)
        draw.text((x, value_y), value, font=font, fill="#102A43")
        bboxes[key] = [box[0] - 4, box[1] - 3, box[2] + 5, box[3] + 4]
    draw.text((56, 545), "SYNTHETIC SAMPLE • NOT VALID FOR IDENTIFICATION", font=_font(15, True), fill="#A24B3A")
    for i in range(6):
        x = 845 + i * 13
        height = 25 + int(12 * math.sin(i))
        draw.rectangle((x, 515 - height, x + 5, 515), fill="#8AA5AE")
    return image, bboxes


def draw_bbox_overlay(image: Image.Image, bbox: list[int] | None, color: str = "#E23D28") -> Image.Image:
    result = image.copy()
    if bbox:
        ImageDraw.Draw(result).rectangle(tuple(bbox), outline=color, width=5)
    return result

