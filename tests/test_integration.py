import pytest

from niriksha_bench.generator.validator import validate_dataset


@pytest.mark.local_artifacts
def test_full_generated_dataset_integrity():
    report = validate_dataset()
    assert report["valid"]
    assert report["documents"] >= 500
