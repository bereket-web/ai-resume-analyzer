# Scoring and safe-use notes

## What the indicator means

The 0–100 alignment indicator is a compact comparison of the supplied texts, not a probability or a measure of a person. It is computed as:

- **90% weighted skill coverage:** matched job-description skills divided by all recognized job-description skills, weighted 3 for explicitly required, 2 for unspecified, and 1 for explicitly preferred phrases.
- **10% text overlap:** TF-IDF unigram/bigram cosine similarity between the full resume and job-description text.

Required/preferred labels are inferred from wording within 100 characters of a skill mention. Where that wording is unclear, the skill is left unspecified. The weights and formula are included in every API response. If no job-description skills are recognized, the tool withholds the score rather than implying meaningful comparison from prose overlap alone.

The score bands (“limited,” “partial,” “moderate,” and “strong stated-skill alignment”) are fixed descriptive labels only. They do not imply job fit, interview likelihood, candidate quality, or a hiring outcome.

## Evidence boundaries

A skill is reported only when one of its known aliases appears in the input. Excerpts preserve the nearby phrase so people can review a potential false positive. A missing skill may be present under an unrecognized synonym, acronym, language, or formatting style. Extraction does not establish proficiency, duration, recency, or truth of a claim.

Suggestions are limited to reviewing and clearly presenting existing evidence. ClearFit never recommends a hiring decision and must not be used to automatically filter, rank, accept, or reject candidates.

## Evaluation

`reports/synthetic_skill_extraction.json` is generated from hand-authored, synthetic text cases with expected labels. It is useful for detecting regressions in the current dictionary, but is tiny, curated, and unrepresentative. It does not establish validity, fairness, or performance on real resumes/job descriptions. There is no trained model and no measured employment outcome.
