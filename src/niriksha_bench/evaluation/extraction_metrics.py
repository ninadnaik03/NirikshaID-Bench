import re
import unicodedata

from rapidfuzz.fuzz import ratio


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).upper().strip()
    return re.sub(r"[\s\W_]+", "", value)


def character_error_rate(reference: str, prediction: str) -> float:
    reference, prediction = normalize(reference), normalize(prediction)
    if not reference:
        return 0.0 if not prediction else 1.0
    previous = list(range(len(prediction) + 1))
    for i, ref_char in enumerate(reference, 1):
        current = [i]
        for j, pred_char in enumerate(prediction, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ref_char != pred_char)))
        previous = current
    return previous[-1] / len(reference)


def field_scores(reference: str, prediction: str) -> dict[str, float]:
    return {
        "exact_match": float(reference == prediction),
        "normalized_exact_match": float(normalize(reference) == normalize(prediction)),
        "cer": character_error_rate(reference, prediction),
        "fuzzy_score": ratio(normalize(reference), normalize(prediction)) / 100,
    }

