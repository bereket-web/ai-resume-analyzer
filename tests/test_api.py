from fastapi.testclient import TestClient

from resume_analyzer.api import app

client = TestClient(app)


def test_health_endpoint_identifies_local_mode():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "local-only"


def test_browser_homepage_loads_locally():
    response = client.get("/")
    assert response.status_code == 200
    assert "ClearFit" in response.text
    assert "does not retain analysis after the request" in response.text


def test_json_analysis_returns_structured_evidence():
    response = client.post(
        "/api/analyze",
        json={
            "resume_text": "Python developer with SQL experience.",
            "job_description": "Required: Python and SQL.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] is not None
    assert {row["name"] for row in data["matched_skills"]} == {"Python", "SQL"}


def test_file_analysis_accepts_utf8_text_and_does_not_return_resume_text():
    response = client.post(
        "/api/analyze-file",
        data={"job_description": "Required: Python."},
        files={"resume": ("resume.txt", b"Python developer", "text/plain")},
    )
    assert response.status_code == 200
    assert "resume_text" not in response.json()


def test_upload_rejects_unknown_file_type():
    response = client.post(
        "/api/analyze-file",
        data={"job_description": "Required: Python."},
        files={"resume": ("resume.rtf", b"Python", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]


def test_blank_inputs_are_rejected():
    response = client.post("/api/analyze", json={"resume_text": " ", "job_description": "Python"})
    assert response.status_code == 422
