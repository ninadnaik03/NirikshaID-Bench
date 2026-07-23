"""Run the publication diagnostic sequence without the label-derived Demo Stub."""

from niriksha_bench.evaluation.evaluator import combined_summary, evaluate


def main() -> None:
    evaluate("eval_seen", "qwen", limit=20)
    evaluate("eval_unseen", "qwen", limit=20)
    combined_summary()


if __name__ == "__main__":
    main()
