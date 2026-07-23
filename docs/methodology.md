# Methodology

Samples use one original 960×600 fictional card template, procedural avatars, and seeded fictional fields. Tampering occurs before blur/noise/JPEG degradation. Evaluation splits are balanced 50/50 genuine/tampered. `digit_edit` is held out of train and validation and evaluated separately in `eval_unseen`.

Extraction metrics compare visible (`displayed_fields`) values with predicted values. Tamper detection, type, and localization compare injected label metadata. Missing boxes remain missing. Parser failures remain failures. Seen/unseen metrics are never merged into one headline score.

## Hard-negative genuine set

The hard-negative set contains only genuine documents. Each receives one suspicious but legitimate rendering condition: subtle font rendering, kerning variation, a two-pixel alignment shift, uneven JPEG blocks, scan shadow, low contrast, printer noise, or local text compression. The primary metric is false-positive rate overall and per condition. Tamper F1 is reported before and after appending these negatives.

## Counterfactual pairs

Each pair begins with one rendered identity card. The tampered branch receives exactly one intervention; the genuine branch does not. Both branches replay an independent degradation RNG with the same seed. Pair metrics include verdict-flip rate, correct verdict flips, tamper-probability change, extraction stability outside the affected field, and localization IoU.

## Calibration and review

Confidence is evaluated with Expected Calibration Error, Brier score, reliability bins, and a risk–coverage curve. Selective operating points report accuracy and errors avoided at 10%, 20%, and 30% simulated manual-review rates. The prediction schema also supports explicit abstention with `tampered=null` and `abstain=true`.
