# Resume Optimization Engine

An end-to-end toolkit for comparing a resume against a job description, surfacing gaps, computing an ATS-style score, and generating STAR-format bullet suggestions.

## Features

- Parse resumes from PDF, DOCX, or TXT files with light section detection.
- Fetch job descriptions from URLs or local text files and extract responsibilities and qualifications.
- Extract and rank keywords using spaCy noun chunks with optional embedding centrality.
- Compute local sentence-transformer embeddings (with OpenAI fallback) and cosine similarity for robust keyword matching.
- Produce ATS-inspired scoring, missing/weak keyword analysis, and optional STAR bullet rewrites.
- CLI interface for full analysis or STAR-only generation.
- FastAPI microservice for the AI Email Networking Copilot, including CSV import, outreach drafting, follow-up planning, and reply classification endpoints.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm  # optional but recommended
```

Copy `.env.example` to `.env` and populate secrets if you plan to use OpenAI features.

## Usage

Run the CLI end-to-end:

```bash
python app.py analyze --resume examples/ml_resume.pdf --job examples/ml_job.txt --out report.json --star
```

Generate STAR bullets only:

```bash
python app.py star --resume examples/backend_resume.txt --job examples/backend_job.txt --n 3
```

The CLI writes structured JSON following the schemas in `src/io_models.py`.

### Networking Copilot API

Spin up the FastAPI service to access the networking workflows:

```bash
uvicorn src.networking.app:app --reload
```

Available endpoints under the `/networking` prefix include:

- `POST /contacts/import` — Upload CSV content (name, email, company, role, relationship, notes, plus optional scoring columns) and receive scored contacts ranked by priority.
- `POST /drafts` — Provide contact context and a voice profile to receive up to three personalized draft variants and recommended follow-up window.
- `POST /followups` — Translate an interaction + reply intent into a follow-up schedule.
- `POST /replies/classify` — Classify raw reply text into positive/neutral/deferral/rejection and receive next-action guidance.

The service keeps prompts and template variants co-located in `src/networking/drafting.py` so you can swap in an LLM or custom templates without touching the API layer. CSV parsing lives in `src/networking/importers.py`, while scoring, follow-up heuristics, and reply classifiers each have dedicated modules with unit tests for rapid iteration.

## Configuration

- Embedding model defaults to `sentence-transformers/all-MiniLM-L6-v2`. Override with the `MODEL_NAME` environment variable if desired.
- Enable OpenAI-backed features by passing `--use-openai`. Requires `OPENAI_API_KEY`.
- Similarity thresholds: `>=0.75` considered present, `0.60-0.75` weak, `<0.60` missing.

## Scoring Heuristics

The ATS score (0-100) weights:

- Hard skills: 45%
- Soft skills: 15%
- Seniority alignment: 10%
- Domain terminology overlap: 10%
- Keyword breadth: 10%
- Formatting hygiene: 10%

Each category returns actionable tips to improve the score.

## Tests

Run the test suite:

```bash
pytest
```

Golden tests cover keyword gaps, STAR formatting constraints, and ATS score improvements after applying suggestions.

## Local AI Resume Tailoring API (FastAPI)

This repository also includes a self-contained FastAPI service for local-only resume tailoring. It relies exclusively on free, local models for embeddings and NLP while storing data in SQLite.

### Run the API locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# The spaCy model is downloaded on first run if missing.
uvicorn app.main:app --reload
```

Key endpoints are available in the Swagger UI at http://127.0.0.1:8000/docs:

- `POST /auth/register` — Create an account with email/password.
- `POST /auth/login` — Obtain a bearer token (OAuth2 password flow).
- `POST /resumes/upload` — Upload a PDF or DOCX resume; the text is parsed and stored.
- `POST /jobs/analyze` — Provide a job description (and optional `resume_id`). Returns similarity score, rewritten resume bullets, and extracted keywords.

Uploads are stored in `./uploads`, and the SQLite database lives at `./resume_tailor.db` by default.

## Privacy

- External calls are limited to optional OpenAI usage and job description URL fetches.
- Logs avoid storing PII and redact secrets by default.

## Examples

Sample resumes and job descriptions are located in `examples/`. Use them to validate end-to-end behavior or extend with your own data.
