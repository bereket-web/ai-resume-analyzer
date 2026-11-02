# Model and data statement

**System:** ClearFit Resume Analyzer 0.1.0

**Model:** No trained model is included. The system uses a hand-curated skill alias dictionary and scikit-learn TF-IDF/cosine similarity for one small text-overlap feature.

**Training data:** None. There is no fitting on resumes, candidate records, or hiring outcomes. The TF-IDF vocabulary is fitted on the two texts in each individual request only; it is not retained.

**Test material:** Fictional, hand-authored examples and tests in this repository. They are not a representative benchmark.

**Intended use:** Personal resume editing and learning how a document explicitly overlaps with a role description.

**Out-of-scope use:** Candidate screening, applicant ranking, hiring, rejection, promotion, or other consequential employment decisions.

**Limitations:** See [`limitations.md`](limitations.md) and [`scoring_and_safety.md`](scoring_and_safety.md).

**Distribution:** No user resume, external resume dataset, trained checkpoint, or Hugging Face model artifact is distributed.
