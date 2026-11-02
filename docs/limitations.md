# Limitations and intended use

- **Not a hiring tool:** Do not use the output to rank candidates, screen applications, decide interviews, or make any employment decision. No decision outcome, predictive validity, or fairness study has been performed.
- **Limited vocabulary:** The skill dictionary is manually curated, English-language, and incomplete. Synonyms, emerging tools, languages, domain-specific skills, and formatting can be missed. Acronyms can be ambiguous.
- **Text extraction:** PDF extraction requires selectable text; scanned documents and image-based layouts are not OCR processed. Multi-column layouts may produce odd reading order. DOCX support includes paragraphs and tables but not embedded-image OCR.
- **Skill evidence is not proficiency:** A phrase may not demonstrate practical skill, recency, expertise, or a verified credential. Absence from extracted text is not proof that a person lacks a skill.
- **Heuristic importance:** Required/preferred weighting uses nearby wording and can misclassify when a long sentence or layout places labels far from requirements.
- **Text similarity is lexical:** TF-IDF misses semantic equivalence and may reward generic shared wording. It is only 10% of the defined score.
- **No real-world benchmark:** The only provided evaluation is hand-authored synthetic fixture data. It says nothing about population performance, validity, or disparate impact.
- **Prototype security:** The local API has no authentication, authorization, or request-rate controls. Keep it bound to `127.0.0.1`; do not deploy as-is on a public network. No security audit has been performed.
- **Privacy context:** Application code does not intentionally retain or externally transmit text after a request. FastAPI/Starlette multipart handling may temporarily spool larger uploads to the host's temporary directory before cleanup. Temporary-directory permissions/retention, browser extensions, operating-system telemetry, reverse proxies, and backups remain part of the deployment's privacy boundary.
