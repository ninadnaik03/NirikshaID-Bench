"""Optional QLoRA entry point.

The critical path does not import torch/transformers. Install `.[models]` and PEFT/bitsandbytes
on a compatible CUDA system before extending this module into a training run.
"""


def main() -> None:
    raise SystemExit(
        "QLoRA is compute-dependent and intentionally disabled by default. "
        "See configs/training.yaml and docs/model_card.md."
    )


if __name__ == "__main__":
    main()

