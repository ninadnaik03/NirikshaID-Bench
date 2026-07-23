# Model adapters

The label-derived Demo Stub exists only to exercise gallery UI state. It reads labels and therefore cannot be selected by the evaluator or included in benchmark discovery.

The first genuine VLM baseline is Qwen2.5-VL-3B-Instruct through the local Ollama image API. It receives only image bytes and the versioned common prompt. Temperature is zero; raw responses, parse failures, latency, model tag, and quantization metadata are saved.

The classical comparison is Template-Aware Tesseract OCR + Visual RF. OCR is performed on fixed template regions. The tamper classifier uses grayscale, variance, and edge features and is fit only on train images/labels. OCR is not described as a forgery detector.

QLoRA is optional. Any future training runner must call `allowed_training_examples` and preserve the `digit_edit` exclusion.
