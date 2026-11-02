"""Run the curated synthetic skill-phrase regression check."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from resume_analyzer.evaluation import evaluate, write_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = write_report(args.output) if args.output else evaluate()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
