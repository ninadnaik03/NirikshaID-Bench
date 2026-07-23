import pytest

from niriksha_bench.evaluation.extraction_metrics import character_error_rate, field_scores
from niriksha_bench.evaluation.localization_metrics import bbox_iou
from niriksha_bench.evaluation.tamper_metrics import binary_metrics


def test_extraction_metrics():
    scores = field_scores("RAHUL SHARMA", "rahul  sharma")
    assert scores["exact_match"] == 0
    assert scores["normalized_exact_match"] == 1
    assert character_error_rate("ABC", "ADC") == pytest.approx(1 / 3)


def test_iou():
    assert bbox_iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1
    assert bbox_iou([0, 0, 10, 10], [10, 10, 20, 20]) == 0
    assert bbox_iou(None, [0, 0, 1, 1]) is None


def test_tamper_metrics():
    metrics = binary_metrics([True, True, False, False], [True, False, True, False])
    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5

