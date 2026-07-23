import json

from niriksha_bench.evaluation.diagnostic_evaluator import evaluate_diagnostics

print(json.dumps(evaluate_diagnostics(), indent=2))
