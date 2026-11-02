from resume_analyzer.evaluation import CASES, evaluate
from resume_analyzer.taxonomy import find_skills


def test_aliases_return_canonical_skill_and_verbatim_evidence():
    found = find_skills("Experience with PyTorch for deep learning.")
    by_name = {row["name"]: row for row in found}
    assert "PyTorch" in by_name
    assert by_name["PyTorch"]["evidence"] == "Experience with PyTorch for deep learning"
    assert "Deep Learning" in by_name


def test_aliases_do_not_match_inside_unrelated_words():
    found = find_skills("ongoing work in HTML and ragtime history")
    assert found == []


def test_java_and_javascript_are_separate_terms():
    found = {row["name"] for row in find_skills("Java and JavaScript are both listed.")}
    assert found == {"Java", "JavaScript"}


def test_curated_synthetic_fixture_runs():
    result = evaluate()
    assert result["cases"] == len(CASES)
    assert result["false_positive"] == 0
    assert result["false_negative"] == 0
    assert "not a representative" in result["warning"]
