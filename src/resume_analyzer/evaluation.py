"""Tiny curated regression check, not a representative resume benchmark."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from resume_analyzer.taxonomy import find_skills

CASES = [
    {
        "id": "programming-data",
        "text": "Python and SQL; reporting with pandas.",
        "expected": ["Pandas", "Python", "SQL"],
    },
    {
        "id": "ml-frameworks",
        "text": "Machine learning prototypes in scikit-learn and PyTorch.",
        "expected": ["Machine Learning", "PyTorch", "scikit-learn"],
    },
    {
        "id": "language-boundaries",
        "text": "Java and JavaScript are different tools.",
        "expected": ["Java", "JavaScript"],
    },
    {"id": "systems-languages", "text": "Coursework in C++ and C#.", "expected": ["C#", "C++"]},
    {
        "id": "genai",
        "text": "Built retrieval augmented generation tools for large language models.",
        "expected": ["Large Language Models", "Retrieval-Augmented Generation"],
    },
    {
        "id": "cloud-stack",
        "text": "Deployed with Docker, Kubernetes, and AWS.",
        "expected": ["AWS", "Docker", "Kubernetes"],
    },
    {
        "id": "data-methods",
        "text": "Data analysis, A/B testing, and time-series forecasting.",
        "expected": ["A/B Testing", "Data Analysis", "Time Series Forecasting"],
    },
    {
        "id": "false-positive-phrases",
        "text": "Ongoing work in HTML for a ragtime history blog; no listed tooling.",
        "expected": [],
    },
    {
        "id": "api-stack",
        "text": "Developed FastAPI services and REST APIs.",
        "expected": ["FastAPI", "REST APIs"],
    },
    {
        "id": "working-methods",
        "text": "Research skills, written communication, and Agile delivery.",
        "expected": ["Agile", "Communication", "Research"],
    },
]


def evaluate() -> dict[str, Any]:
    tp = fp = fn = 0
    rows = []
    for case in CASES:
        expected = set(case["expected"])
        predicted = {row["name"] for row in find_skills(case["text"])}
        case_tp = expected & predicted
        case_fp = predicted - expected
        case_fn = expected - predicted
        tp += len(case_tp)
        fp += len(case_fp)
        fn += len(case_fn)
        rows.append(
            {
                "id": case["id"],
                "expected": sorted(expected),
                "predicted": sorted(predicted),
                "true_positive": sorted(case_tp),
                "false_positive": sorted(case_fp),
                "false_negative": sorted(case_fn),
            }
        )
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "evaluation": "hand-authored synthetic skill-phrase regression check",
        "cases": len(CASES),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "warning": "Curated synthetic snippets only; not a representative resume or job-description benchmark and not evidence of hiring validity or fairness.",
        "case_results": rows,
    }


def write_report(output: Path) -> dict[str, Any]:
    result = evaluate()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
