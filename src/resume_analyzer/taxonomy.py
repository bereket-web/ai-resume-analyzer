"""Transparent skill dictionary and phrase-level evidence extraction.

This deliberately avoids opaque embeddings or a model that silently infers skills.
Every match is anchored to an explicit phrase in the supplied text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    aliases: tuple[str, ...]


# A deliberately compact, hand-curated starter vocabulary; it is not exhaustive.
SKILLS: tuple[Skill, ...] = (
    Skill("Python", "Programming", ("python",)),
    Skill("Java", "Programming", ("java",)),
    Skill("JavaScript", "Programming", ("javascript", "js")),
    Skill("TypeScript", "Programming", ("typescript",)),
    Skill("C++", "Programming", ("c++", "cpp")),
    Skill("C#", "Programming", ("c#", "c sharp")),
    Skill("Go", "Programming", ("golang", "go language")),
    Skill("R", "Programming", ("r programming", "r language")),
    Skill("SQL", "Data", ("sql",)),
    Skill("Bash", "Programming", ("bash", "shell scripting")),
    Skill("Machine Learning", "AI/ML", ("machine learning", "ml")),
    Skill("Deep Learning", "AI/ML", ("deep learning",)),
    Skill("Natural Language Processing", "AI/ML", ("natural language processing", "nlp")),
    Skill("Computer Vision", "AI/ML", ("computer vision",)),
    Skill("Generative AI", "AI/ML", ("generative ai", "genai", "generative artificial intelligence")),
    Skill("Large Language Models", "AI/ML", ("large language models", "large language model", "llms", "llm")),
    Skill(
        "Retrieval-Augmented Generation",
        "AI/ML",
        ("retrieval-augmented generation", "retrieval augmented generation", "rag"),
    ),
    Skill("Transformers", "AI/ML", ("transformers", "transformer models")),
    Skill("PyTorch", "AI/ML", ("pytorch", "torch")),
    Skill("TensorFlow", "AI/ML", ("tensorflow",)),
    Skill("scikit-learn", "AI/ML", ("scikit-learn", "scikit learn", "sklearn")),
    Skill("Hugging Face", "AI/ML", ("hugging face", "huggingface")),
    Skill("MLOps", "AI/ML", ("mlops", "machine learning operations")),
    Skill("Feature Engineering", "AI/ML", ("feature engineering",)),
    Skill("Model Evaluation", "AI/ML", ("model evaluation", "model validation")),
    Skill("Statistics", "Data", ("statistics", "statistical analysis")),
    Skill("Data Analysis", "Data", ("data analysis", "data analytics")),
    Skill("Data Visualization", "Data", ("data visualization", "data visualisation")),
    Skill("Pandas", "Data", ("pandas",)),
    Skill("NumPy", "Data", ("numpy",)),
    Skill("Spark", "Data", ("apache spark", "pyspark", "spark")),
    Skill("ETL", "Data", ("etl", "extract transform load")),
    Skill("PostgreSQL", "Data", ("postgresql", "postgres")),
    Skill("MySQL", "Data", ("mysql",)),
    Skill("MongoDB", "Data", ("mongodb",)),
    Skill("Redis", "Data", ("redis",)),
    Skill("FastAPI", "Backend", ("fastapi",)),
    Skill("Flask", "Backend", ("flask",)),
    Skill("Django", "Backend", ("django",)),
    Skill("REST APIs", "Backend", ("rest api", "rest apis", "restful api", "restful apis")),
    Skill("GraphQL", "Backend", ("graphql",)),
    Skill("Docker", "Cloud/DevOps", ("docker", "containerization", "containerisation")),
    Skill("Kubernetes", "Cloud/DevOps", ("kubernetes", "k8s")),
    Skill("AWS", "Cloud/DevOps", ("amazon web services", "aws")),
    Skill("Google Cloud", "Cloud/DevOps", ("google cloud platform", "google cloud", "gcp")),
    Skill("Microsoft Azure", "Cloud/DevOps", ("microsoft azure", "azure")),
    Skill("Git", "Tools", ("git", "version control")),
    Skill("Linux", "Tools", ("linux",)),
    Skill("CI/CD", "Cloud/DevOps", ("ci/cd", "continuous integration", "continuous delivery")),
    Skill("Airflow", "Data", ("apache airflow", "airflow")),
    Skill("Spark Streaming", "Data", ("spark streaming", "structured streaming")),
    Skill(
        "Time Series Forecasting",
        "AI/ML",
        ("time series forecasting", "time-series forecasting", "forecasting"),
    ),
    Skill("Recommendation Systems", "AI/ML", ("recommendation systems", "recommender systems")),
    Skill("A/B Testing", "Data", ("a/b testing", "ab testing", "controlled experiments")),
    Skill("Agile", "Ways of working", ("agile", "scrum")),
    Skill(
        "Communication",
        "Ways of working",
        ("communication skills", "written communication", "verbal communication"),
    ),
    Skill("Leadership", "Ways of working", ("leadership", "team leadership")),
    Skill("Project Management", "Ways of working", ("project management",)),
    Skill("Research", "Ways of working", ("research skills", "applied research")),
)


def _pattern_for(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias)
    # Word boundaries avoid matching e.g. "go" inside "ongoing". Punctuation
    # such as C++, C#, and CI/CD remains literal and case-insensitive.
    return re.compile(rf"(?<![\w]){escaped}(?![\w])", re.IGNORECASE)


PATTERNS: tuple[tuple[Skill, tuple[re.Pattern[str], ...]], ...] = tuple(
    (skill, tuple(_pattern_for(alias) for alias in skill.aliases)) for skill in SKILLS
)


def _evidence_span(text: str, start: int, end: int, limit: int = 180) -> str:
    """Return a short, unmodified sentence/line fragment containing the match."""
    left_candidates = [text.rfind(mark, 0, start) for mark in (".", "!", "?", "\n", ";", "•")]
    left = max(left_candidates) + 1
    right_candidates = [pos for mark in (".", "!", "?", "\n", ";", "•") if (pos := text.find(mark, end)) >= 0]
    right = min(right_candidates) if right_candidates else len(text)
    fragment = " ".join(text[left:right].split()).strip(" -\t")
    if len(fragment) > limit:
        offset = max(0, start - left - limit // 3)
        fragment = fragment[offset : offset + limit].strip()
    return fragment


def find_skills(text: str) -> list[dict[str, str]]:
    """Find unique canonical skills and retain a text excerpt for each match."""
    found: list[dict[str, str]] = []
    if not text:
        return found
    for skill, patterns in PATTERNS:
        best: tuple[int, int] | None = None
        for pattern in patterns:
            match = pattern.search(text)
            if match and (best is None or match.start() < best[0]):
                best = (match.start(), match.end())
        if best is not None:
            found.append(
                {
                    "name": skill.name,
                    "category": skill.category,
                    "evidence": _evidence_span(text, best[0], best[1]),
                }
            )
    return sorted(found, key=lambda row: (row["category"].casefold(), row["name"].casefold()))


def skill_names() -> tuple[str, ...]:
    """Return the supported canonical skill names in stable taxonomy order."""
    return tuple(skill.name for skill in SKILLS)
