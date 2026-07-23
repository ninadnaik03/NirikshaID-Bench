import json

from niriksha_bench.generator.fields import generate_fields
from niriksha_bench.models.output_parser import parse_prediction


def test_parser_strips_fences():
    import random
    payload = {
        "fields": generate_fields(1, random.Random(2)).model_dump(),
        "tampered": False, "tamper_type": "none", "tampered_field": None,
        "tamper_bbox": None, "confidence": 0.8, "reason": "No visible inconsistency",
    }
    parsed, repaired, error = parse_prediction(f"```json\n{json.dumps(payload)}\n```")
    assert parsed is not None and repaired and error is None


def test_parser_does_not_fabricate():
    parsed, _, error = parse_prediction("not valid")
    assert parsed is None and error

