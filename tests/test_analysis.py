from resume_analyzer.analysis import analyze_resume


def test_job_match_exposes_evidence_missing_skills_and_formula():
    result = analyze_resume(
        "Python developer with experience shipping data services.",
        "Required: Python and SQL. Preferred: Docker.",
    )
    assert result["score"] is not None
    assert result["score_components"]["recognized_job_skill_count"] == 3
    assert [row["name"] for row in result["matched_skills"]] == ["Python"]
    assert {row["name"] for row in result["missing_skills"]} == {"SQL", "Docker"}
    assert {row["name"]: row["importance"] for row in result["job_skills"]} == {
        "Python": "required",
        "SQL": "required",
        "Docker": "preferred",
    }
    assert result["matched_skills"][0]["resume_evidence"]
    assert "not a probability" in result["score_type"]
    components = result["score_components"]
    expected = round(
        0.9 * components["skill_coverage_percent"] + 0.1 * components["text_similarity_percent"],
        1,
    )
    assert result["score"] == expected


def test_short_role_heading_does_not_bleed_into_unrelated_importance_labels():
    result = analyze_resume(
        "Python, SQL, Docker, and communication skills.",
        "Required qualifications:\n- Python and SQL.\nPreferred qualifications:\n- Docker.\nCommunication skills are useful.",
    )
    importance = {row["name"]: row["importance"] for row in result["job_skills"]}
    assert importance == {
        "Python": "required",
        "SQL": "required",
        "Docker": "preferred",
        "Communication": "unspecified",
    }


def test_score_is_withheld_when_no_supported_job_skills_are_found():
    result = analyze_resume(
        "A collaborative professional with a varied background.", "Join our friendly team."
    )
    assert result["score"] is None
    assert result["score_components"]["skill_coverage_percent"] is None
    assert result["score_label"].startswith("Not scored")
    assert any("no match score" in line for line in result["recommendations"])


def test_resume_parsing_returns_section_counts_without_copying_full_text():
    result = analyze_resume("SKILLS\nPython\nEXPERIENCE\nUsed Python.", "Required: Python.")
    assert result["resume_sections"]["skills"] == 1
    assert result["resume_sections"]["experience"] == 1
    assert "resume_text" not in result
    assert "privacy" in result


def test_score_is_bounded_and_missing_skill_means_not_found_in_text():
    result = analyze_resume("Python SQL Docker", "Required Python SQL Docker")
    assert 0 <= result["score"] <= 100
    assert "not found" in result["score_type"] or "not a probability" in result["score_type"]
