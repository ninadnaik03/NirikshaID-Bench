import pytest

from niriksha_bench.evaluation.calibration_metrics import (
    brier_score,
    expected_calibration_error,
    risk_coverage_curve,
    tamper_probability,
)


def test_tamper_probability_respects_verdict():
    assert tamper_probability(True, 0.8) == 0.8
    assert tamper_probability(False, 0.8) == pytest.approx(0.2)
    assert tamper_probability(None, 0.9, abstain=True) == 0.5


def test_perfect_calibration_scores():
    assert brier_score([True, False], [1.0, 0.0]) == 0
    result = expected_calibration_error([True, False], [True, False], [1.0, 1.0])
    assert result["ece"] == 0


def test_risk_coverage_orders_confidence():
    curve = risk_coverage_curve([True, False], [True, True], [0.9, 0.5])
    assert curve[0]["selective_accuracy"] == 1
    assert curve[-1]["selective_accuracy"] == 0.5
