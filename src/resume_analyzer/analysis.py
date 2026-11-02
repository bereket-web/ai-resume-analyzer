"""Deterministic resume/JD analysis with explicit evidence and a transparent rubric."""

from __future__ import annotations

import re
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_analyzer.parser import extract_sections
from resume_analyzer.taxonomy import PATTERNS, find_skills

_REQUIRED = re.compile(
    r"\b(required|required skill|required qualification|must[- ]have|must possess|essential|minimum requirement|minimum qualification|you need to|we require)\b",
    re.IGNORECASE,
)
_PREFERRED = re.compile(
    r"\b(preferred|preferably|nice[- ]to[- ]have|bonus|desirable|a plus|plus if|ideally|advantageous)\b",
    re.IGNORECASE,
)
_WEIGHT = {"required": 3, "unspecified": 2, "preferred": 1}


def _text_similarity(resume: str, job_description: str) -> float:
    """Compute a bounded TF-IDF cosine overlap diagnostic; no model is trained."""
    if not resume.strip() or not job_description.strip():
        return 0.0
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=20_000).fit_transform(
            [resume, job_description]
        )
    except ValueError:
        return 0.0
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0])


def _classify_importance(name: str, job_description: str) -> str:
    """Infer only explicit nearby requirement wording; otherwise retain uncertainty."""
    skill_patterns = next(patterns for skill, patterns in PATTERNS if skill.name == name)
    contexts: list[str] = []
    for pattern in skill_patterns:
        for match in pattern.finditer(job_description):
            start = (
                max(job_description.rfind(mark, 0, match.start()) for mark in (".", "!", "?", ";", "\n")) + 1
            )
            ends = [job_description.find(mark, match.end()) for mark in (".", "!", "?", ";", "\n")]
            end = min((position for position in ends if position >= 0), default=len(job_description))
            context = job_description[start:end]
            line_start = job_description.rfind("\n", 0, start) + 1
            line_prefix = job_description[line_start : match.start()].strip()
            current_line_end = job_description.find("\n", match.end())
            if current_line_end < 0:
                current_line_end = len(job_description)
            current_line = job_description[line_start:current_line_end]
            is_bullet_line = re.match(r"^\s*[-•*]\s+", current_line) is not None
            if line_prefix in {"", "-", "•", "*"} or is_bullet_line:
                prior_end = line_start - 1
                prior_start = job_description.rfind("\n", 0, max(0, prior_end)) + 1
                previous = job_description[prior_start:prior_end].strip()
                if re.fullmatch(
                    r"[-•* ]*(?:required|minimum|essential|must[- ]have|preferred|nice[- ]to[- ]have|bonus|desirable)(?:\s+qualifications?)?\s*:?",
                    previous,
                    re.IGNORECASE,
                ):
                    context = previous + " " + context
            contexts.append(context)
    combined = "\n".join(contexts)
    if _REQUIRED.search(combined):
        return "required"
    if _PREFERRED.search(combined):
        return "preferred"
    return "unspecified"


def _label(score: float) -> str:
    if score >= 80:
        return "Strong stated-skill alignment"
    if score >= 60:
        return "Moderate stated-skill alignment"
    if score >= 40:
        return "Partial stated-skill alignment"
    return "Limited stated-skill alignment"


def analyze_resume(resume_text: str, job_description: str) -> dict[str, Any]:
    """Analyze supplied text. Callers are responsible for input-size validation."""
    resume_text = resume_text.strip()
    job_description = job_description.strip()
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_description)
    resume_by_name = {row["name"]: row for row in resume_skills}

    matched: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    weights_total = 0
    weights_matched = 0
    for job_skill in job_skills:
        importance = _classify_importance(job_skill["name"], job_description)
        weight = _WEIGHT[importance]
        weights_total += weight
        in_resume = resume_by_name.get(job_skill["name"])
        row = {
            "name": job_skill["name"],
            "category": job_skill["category"],
            "importance": importance,
            "weight": weight,
            "job_evidence": job_skill["evidence"],
            "resume_evidence": in_resume["evidence"] if in_resume else None,
        }
        if in_resume:
            weights_matched += weight
            matched.append(row)
        else:
            missing.append(row)

    similarity = _text_similarity(resume_text, job_description)
    coverage = weights_matched / weights_total if weights_total else None
    # A score is withheld if no skills can be identified; a prose-only cosine
    # overlap is not enough evidence to imply meaningful compatibility.
    score = round(90 * coverage + 10 * similarity, 1) if coverage is not None else None
    if score is not None:
        score = min(100.0, max(0.0, score))

    importance_order = {"required": 0, "unspecified": 1, "preferred": 2}
    missing.sort(key=lambda row: (importance_order[row["importance"]], row["name"].casefold()))
    matched.sort(key=lambda row: (importance_order[row["importance"]], row["name"].casefold()))

    recommendations: list[str] = []
    required_missing = [row["name"] for row in missing if row["importance"] == "required"]
    other_missing = [row["name"] for row in missing if row["importance"] != "required"]
    if required_missing:
        names = ", ".join(required_missing[:5])
        recommendations.append(
            f"Review the explicitly required skill(s) {names}. If you have relevant experience, add a truthful, specific example; otherwise do not list them as skills."
        )
    if other_missing:
        names = ", ".join(other_missing[:5])
        recommendations.append(
            f"Consider whether you can substantiate {names} with project, coursework, or work examples; the job description did not clearly mark every one as required."
        )
    if matched:
        recommendations.append(
            "Make the strongest evidence easy to find: place relevant skills near the top and connect them to specific work or project outcomes already supported by your experience."
        )
    if not job_skills:
        recommendations.append(
            "No supported skills were recognized in the job description, so no match score is shown. Add clearer responsibilities or skill requirements before comparing."
        )
    recommendations.append(
        "Do not add a skill, credential, responsibility, or result unless it accurately reflects your experience."
    )

    sections = extract_sections(resume_text)
    return {
        "score": score,
        "score_label": _label(score) if score is not None else "Not scored: no recognizable job skills",
        "score_type": "resume-to-description alignment indicator; not a probability, ranking, or hiring decision",
        "score_components": {
            "skill_coverage_percent": round(coverage * 100, 1) if coverage is not None else None,
            "skill_coverage_weighting": "required=3, unspecified=2, preferred=1; importance is inferred only from nearby job-description wording",
            "text_similarity_percent": round(similarity * 100, 1),
            "formula": "90% weighted explicit skill coverage + 10% TF-IDF cosine text overlap",
            "recognized_job_skill_count": len(job_skills),
        },
        "resume_skills": resume_skills,
        "job_skills": [
            {
                **skill,
                "importance": _classify_importance(skill["name"], job_description),
            }
            for skill in job_skills
        ],
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": recommendations,
        "resume_sections": {name: len(lines) for name, lines in sections.items()},
        "resume_word_count": len(resume_text.split()),
        "privacy": "Input text is processed locally and not intentionally retained after this request. Multipart uploads may be temporarily spooled by the framework to the host temporary directory before cleanup.",
    }
