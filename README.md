# Resume Optimization Engine

An end-to-end toolkit for comparing a resume against a job description, surfacing gaps, computing an ATS-style score, and generating STAR-format bullet suggestions.

## Features

- Parse resumes from PDF, DOCX, or TXT files with light section detection.
- Fetch job descriptions from URLs or local text files and extract responsibilities and qualifications.
- Extract and rank keywords using spaCy noun chunks with optional embedding centrality.
- Compute local sentence-transformer embeddings (with OpenAI fallback) and cosine similarity for robust keyword matching.
- Produce ATS-inspired scoring, missing/weak keyword analysis, and optional STAR bullet rewrites.
- CLI interface for full analysis or STAR-only generation.

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

## Privacy

- External calls are limited to optional OpenAI usage and job description URL fetches.
- Logs avoid storing PII and redact secrets by default.

## Examples

Sample resumes and job descriptions are located in `examples/`. Use them to validate end-to-end behavior or extend with your own data.
