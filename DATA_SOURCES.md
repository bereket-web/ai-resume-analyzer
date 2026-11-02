# Data and provenance

This release does not use a resume dataset, scrape candidate profiles, or train a model. No private resume or job-application record is bundled.

The skill aliases in `src/resume_analyzer/taxonomy.py` are a small hand-authored software vocabulary maintained in this repository. The only example resume and job description are fictional synthetic text written for demonstration and tests; they do not represent a real person or employer. The synthetic evaluation fixtures and their expected skill labels are likewise hand-authored. They are not a public benchmark and should not be used to claim real-world performance.

Uploaded documents are processed locally. Application code does not intentionally retain the original file, extracted text, or analysis output after a request. Starlette/FastAPI's multipart parser may temporarily spool larger uploads to the operating system's temporary directory before cleanup; host permissions and temporary-storage policies therefore matter. If you run the service behind a proxy or deploy a modified version, independently inspect its logging, retention, and access-control settings.
