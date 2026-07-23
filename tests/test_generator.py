import random

from niriksha_bench.generator.fields import generate_fields, identity_number
from niriksha_bench.generator.generate import tamper_for
from niriksha_bench.generator.renderer import render
from niriksha_bench.generator.schemas import DocumentLabel


def test_identity_number_format():
    import re
    assert re.fullmatch(r"[A-Z]{3}\d{6}[A-Z]", identity_number(random.Random(1)))


def test_generation_is_reproducible():
    assert generate_fields(7, random.Random(42)) == generate_fields(7, random.Random(42))


def test_render_bboxes_inside_image():
    fields = generate_fields(1, random.Random(5))
    image, bboxes = render(fields, 5)
    for bbox in bboxes.values():
        assert 0 <= bbox[0] < bbox[2] <= image.width
        assert 0 <= bbox[1] < bbox[3] <= image.height


def test_digit_edit_only_in_unseen():
    for split in ("train", "validation", "eval_seen", "demo_gallery"):
        assert all(tamper_for(split, i, random.Random(i)) != "digit_edit" for i in range(20))
    assert any(tamper_for("eval_unseen", i, random.Random(i)) == "digit_edit" for i in range(20))


def test_schema_rejects_held_out_leakage():
    fields = generate_fields(1, random.Random(5))
    _, bboxes = render(fields, 5)
    try:
        DocumentLabel(
            doc_id="nid_000001", image_path="images/nid_000001.jpg",
            fields=fields, displayed_fields=fields, field_bboxes=bboxes,
            tampered=True, tamper_type="digit_edit", tampered_field="identity_number",
            tamper_bbox=bboxes["identity_number"], split="train", seed=5, generator_version="1.0.0",
        )
        assert False, "schema accepted leakage"
    except ValueError:
        pass

