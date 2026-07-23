import math


def tamper_probability(tampered: bool | None, confidence: float, abstain: bool = False) -> float:
    if abstain or tampered is None:
        return 0.5
    return confidence if tampered else 1 - confidence


def brier_score(truth: list[bool], probabilities: list[float]) -> float:
    if not truth:
        return 0.0
    return sum((probability - int(label)) ** 2 for label, probability in zip(truth, probabilities)) / len(truth)


def expected_calibration_error(
    truth: list[bool], predictions: list[bool], confidences: list[float], bins: int = 10
) -> dict:
    if not truth:
        return {"ece": 0.0, "bins": []}
    output = []
    ece = 0.0
    for index in range(bins):
        low, high = index / bins, (index + 1) / bins
        members = [
            position for position, confidence in enumerate(confidences)
            if low <= confidence < high or (index == bins - 1 and confidence == 1)
        ]
        if not members:
            continue
        accuracy = sum(predictions[position] == truth[position] for position in members) / len(members)
        mean_confidence = sum(confidences[position] for position in members) / len(members)
        ece += len(members) / len(truth) * abs(accuracy - mean_confidence)
        output.append(
            {
                "lower": low,
                "upper": high,
                "support": len(members),
                "accuracy": accuracy,
                "mean_confidence": mean_confidence,
            }
        )
    return {"ece": ece, "bins": output}


def risk_coverage_curve(
    truth: list[bool], predictions: list[bool], confidences: list[float]
) -> list[dict]:
    ranked = sorted(zip(confidences, predictions, truth), reverse=True)
    points = []
    for covered in range(1, len(ranked) + 1):
        subset = ranked[:covered]
        errors = sum(prediction != label for _, prediction, label in subset)
        points.append(
            {
                "coverage": covered / len(ranked),
                "risk": errors / covered,
                "selective_accuracy": 1 - errors / covered,
                "confidence_threshold": subset[-1][0],
                "review_rate": 1 - covered / len(ranked),
                "errors_avoided": sum(p != t for _, p, t in ranked[covered:]),
            }
        )
    return points


def selective_operating_points(curve: list[dict], review_rates: tuple[float, ...] = (0.1, 0.2, 0.3)) -> list[dict]:
    if not curve:
        return []
    result = []
    for target in review_rates:
        point = min(curve, key=lambda item: math.fabs(item["review_rate"] - target))
        result.append({"target_review_rate": target, **point})
    return result
