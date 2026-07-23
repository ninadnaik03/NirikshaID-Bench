import argparse
from pathlib import Path

from niriksha_bench.evaluation.report import export_markdown

parser = argparse.ArgumentParser()
parser.add_argument("metrics")
parser.add_argument("destination")
args = parser.parse_args()
export_markdown(Path(args.metrics), Path(args.destination))
