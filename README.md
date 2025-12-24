# Resume Tailoring API

A FastAPI-based backend for uploading resumes, extracting content, and tailoring them to specific job descriptions using NLP and embeddings.

## Project Structure

```
app/
├── api/               # FastAPI routers and dependencies
├── core/              # Application settings and constants
├── db/                # Database session and Base declaration
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic request/response models
├── services/          # Business logic for auth, resumes, and job analysis
└── main.py            # FastAPI application entrypoint
```

## Setup

1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn[standard] sqlalchemy passlib[bcrypt] python-jose
   pip install python-multipart pdfplumber python-docx spacy sentence-transformers scikit-learn
   ```

3. **Run database migrations** (SQLite is used by default, tables are created on startup)

4. **Start the API server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration

Environment variables can override defaults in `app/core/config.py`:
- `DATABASE_URL` – database connection string (defaults to SQLite file)
- `SECRET_KEY` – JWT signing key
- `UPLOAD_DIR` – path for uploaded resumes
- `EMBEDDING_MODEL` – SentenceTransformer model name

## API Overview

- `POST /auth/register` – create a new user
- `POST /auth/login` – obtain a JWT access token
- `POST /resumes/upload` – upload and parse a resume file (PDF or DOCX)
- `POST /jobs/analyze` – analyze a job description against the latest or specified resume

Use the token from `/auth/login` as a Bearer token for protected endpoints.
