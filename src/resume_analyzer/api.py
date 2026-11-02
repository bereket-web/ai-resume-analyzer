"""Local-first FastAPI interface. Request content is not persisted or logged."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from resume_analyzer.analysis import analyze_resume
from resume_analyzer.parser import MAX_FILE_BYTES, ResumeParseError, extract_text

STATIC = Path(__file__).parent / "static"
MAX_TEXT_CHARS = 100_000
MAX_JOB_CHARS = 50_000

app = FastAPI(
    title="ClearFit Resume Analyzer",
    description="Explainable, local-only comparison of supplied resume text and job-description text.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)
    job_description: str = Field(min_length=1, max_length=MAX_JOB_CHARS)


def _validate_job_description(job_description: str) -> None:
    if not job_description.strip():
        raise HTTPException(status_code=422, detail="Job description cannot be blank.")


def _validate_text(resume_text: str, job_description: str) -> None:
    if not resume_text.strip():
        raise HTTPException(status_code=422, detail="Resume text cannot be blank.")
    _validate_job_description(job_description)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-only", "version": "0.1.0"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    _validate_text(request.resume_text, request.job_description)
    return analyze_resume(request.resume_text, request.job_description)


@app.post("/api/analyze-file")
async def analyze_file(
    resume: Annotated[UploadFile, File(description="PDF, DOCX, or UTF-8 TXT; up to 5 MB")],
    job_description: Annotated[str, Form(max_length=MAX_JOB_CHARS)],
) -> dict:
    _validate_job_description(job_description)
    filename = resume.filename or "resume"
    payload = await resume.read(MAX_FILE_BYTES + 1)
    await resume.close()
    if len(payload) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="The resume exceeds the 5 MB upload limit.")
    try:
        resume_text = extract_text(filename, payload)
    except ResumeParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _validate_text(resume_text, job_description)
    if len(resume_text) > MAX_TEXT_CHARS:
        raise HTTPException(
            status_code=413, detail="Extracted resume text exceeds the 100,000 character limit."
        )
    return analyze_resume(resume_text, job_description)


@app.get("/robots.txt", include_in_schema=False)
def robots() -> dict[str, str]:
    return {"content": "User-agent: *\nDisallow: /"}
