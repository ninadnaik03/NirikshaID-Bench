import json

from niriksha_bench.generator.validate_diagnostics import validate_diagnostics

report = validate_diagnostics()
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["valid"] else 1)
