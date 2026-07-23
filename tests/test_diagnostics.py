import pytest

from niriksha_bench.generator.validate_diagnostics import validate_diagnostics


@pytest.mark.local_artifacts
def test_diagnostic_integrity():
    report = validate_diagnostics()
    assert report["valid"]
    assert report["pairs"] == 30
    assert report["hard_negatives"] == 40
