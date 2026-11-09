# ClearFit — AI Resume Analyzer

ClearFit is a local-first tool for comparing resume text with a job description. It extracts explicit skill phrases, shows the exact text evidence for each match, distinguishes required, preferred, and unclassified job skills when nearby wording supports that distinction, and produces a small, transparent alignment indicator with practical resume-editing prompts.

**It is not a hiring or candidate-screening system.** The score is not a probability, employability assessment, or recommendation to hire or reject. A “missing” skill only means the phrase was not recognized in the provided resume text.

## What works

- Parse text from PDF, DOCX, and UTF-8 TXT. DOCX tables are included. Scanned PDFs are rejected with a clear message; OCR is not included.
- Extract skills using an auditable, hand-curated alias dictionary. Every extracted skill includes a source-text excerpt.
- Compare recognized skills in the resume and job description. Nearby job-description phrases such as “required” and “preferred” affect transparent skill weights; ambiguous wording remains “unspecified.”
- Calculate weighted explicit-skill coverage and lexical context similarity. The displayed indicator is **90% weighted skill coverage + 10% TF-IDF cosine text overlap**. Skill weights are required=3, unspecified=2, preferred=1.
- Suggest truthful ways to surface relevant experience, prioritize clearly stated requirements, and avoid inventing credentials or skills.
- Use a responsive browser UI, JSON API, or CLI. No external model service, account, API key, training data, or GPU is needed.

The phrase taxonomy is intentionally visible in [`taxonomy.py`](src/resume_analyzer/taxonomy.py). It is a limited starter vocabulary, not a comprehensive skills ontology. TF-IDF is used only as a lightweight text-overlap feature; no model is trained or fine-tuned. See the [architecture diagram](docs/architecture.png) and its [Mermaid source](docs/architecture.mmd).

## Run locally

Python 3.10+ and `uv` are recommended.

```bash
uv sync --extra test
uv run clearfit serve
```

Then open <http://127.0.0.1:8000>. API documentation is at <http://127.0.0.1:8000/docs>, and the health check is `/health`. The server binds to loopback by default; do not expose the unauthenticated prototype to a public network.

The CLI accepts a resume in PDF, DOCX, or TXT format and a UTF-8 job-description text file:

```bash
uv run clearfit examples/synthetic_resume.txt examples/synthetic_job_description.txt
uv run clearfit examples/synthetic_resume.txt examples/synthetic_job_description.txt --output analysis.json
```

Both example files are fictional and exist solely for demonstration. You can also load them with the browser UI’s sample button.

## Checks and synthetic evaluation

```bash
uv run pytest
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run python scripts/evaluate_synthetic.py --output reports/synthetic_skill_extraction.json
uv build
```

The evaluation fixture checks the explicit skill matcher against hand-authored synthetic snippets and expected labels. On this ten-case fixture, 23 expected skill mentions were detected with no extra or missed matches. This is a regression sanity check only, **not** a representative resume corpus, a hiring benchmark, or evidence of real-world recall/precision. No personal resumes or third-party resume dataset were collected or redistributed.

## Privacy and safe use

Analysis runs locally in the current process. The application does not intentionally retain files, extracted text, or analysis after a request, and it does not send resume/job-description content to an external service. **The multipart framework may temporarily spool larger uploads to the operating system's temporary directory before cleanup.** Review temporary-directory permissions and retention on the host, especially before using sensitive documents. The browser page does not use analytics, third-party fonts, or remote JavaScript. This is a local prototype, not a security-reviewed hosted service; keep it on a trusted device and account for any reverse proxy or infrastructure logs you add.

ClearFit does not infer protected characteristics, assess personality, predict job performance, rank candidates, or make hiring recommendations. It can miss skills, misinterpret abbreviations, and produce misleading text similarity. Users should review the cited excerpts and make their own decisions. Never add a skill, credential, or achievement that is not true.

## Repository layout

```text
src/resume_analyzer/    parsing, skill taxonomy, analysis, API, CLI, browser UI
examples/               fictional resume and job-description text
scripts/                small synthetic extraction evaluation
reports/                reproducible fixture evaluation output
docs/                   architecture, data provenance, limitations
tests/                  offline parser, matching, and API tests
```

## Release status

Public source repository: [bereket-web/ai-resume-analyzer](https://github.com/bereket-web/ai-resume-analyzer). This version includes source, tests, documentation, and fictional synthetic examples only; no real resumes or private records are bundled. No project-specific Hugging Face model, dataset, or Space was created. The package uses no trained model, so a project model artifact is not applicable to this version.
