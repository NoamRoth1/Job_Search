"""Job posting ingestion utilities."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:  # pragma: no cover - optional dependency path
    import requests
except ModuleNotFoundError:  # pragma: no cover - fallback path
    requests = None

try:  # pragma: no cover - optional dependency path
    from bs4 import BeautifulSoup
except ModuleNotFoundError:  # pragma: no cover - fallback path
    BeautifulSoup = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Normalized job posting content."""

    role: str | None
    company: str | None
    text: str
    sections: dict[str, str]


def _fetch_url(url: str) -> str:
    logger.info("Fetching job posting from %s", url)
    if requests is not None:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text = response.text
    else:  # pragma: no cover - fallback
        from urllib.request import urlopen

        with urlopen(url) as handle:
            text = handle.read().decode("utf-8", errors="ignore")

    if BeautifulSoup is not None:
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator="\n")

    import re

    cleaned = re.sub(r"<[^>]+>", " ", text)
    return cleaned


def _read_text(path_or_text: str) -> str:
    path = Path(path_or_text)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return path_or_text


def _extract_sections(lines: Iterable[str]) -> dict[str, str]:
    headers = {
        "responsibilities",
        "requirements",
        "qualifications",
        "about",
        "skills",
    }
    pattern = re.compile(r"^(?P<header>[A-Za-z ]{3,}):$", re.IGNORECASE)
    sections: dict[str, str] = {}
    current = "general"
    buffer: list[str] = []
    for line in lines:
        match = pattern.match(line.strip())
        if match and match.group("header").lower() in headers:
            if buffer:
                sections[current] = "\n".join(buffer).strip()
                buffer = []
            current = match.group("header").lower()
        else:
            buffer.append(line)
    if buffer:
        sections[current] = "\n".join(buffer).strip()
    return sections


def read_job(path_or_url_or_text: str | Path) -> JobPosting:
    """Read a job posting from disk, a URL, or raw text."""

    source = str(path_or_url_or_text)
    if source.startswith("http://") or source.startswith("https://"):
        raw = _fetch_url(source)
    else:
        raw = _read_text(source)

    lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines() if line.strip()]
    sections = _extract_sections(lines)
    text = "\n".join(lines)
    role = None
    company = None
    if lines:
        role = lines[0]
    if len(lines) > 1:
        company = lines[1]
    return JobPosting(role=role, company=company, text=text, sections=sections)
