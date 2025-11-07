"""CSV import helpers."""
from __future__ import annotations

import csv
import io
from typing import List

from .models import Contact

EXPECTED_HEADERS = {"name", "email", "company", "role", "relationship", "notes"}
OPTIONAL_HEADERS = {
    "relationship_strength",
    "overlap_skills",
    "mutuals_count",
    "recent_activity",
    "cold_days_since_last_touch",
}


class CSVImportError(ValueError):
    """Raised when a CSV payload cannot be parsed."""


def _normalise_header(header: str) -> str:
    return header.strip().lower().replace(" ", "_")


def parse_contacts_csv(csv_text: str) -> List[Contact]:
    """Parse CSV text into :class:`Contact` objects with validation."""

    if not csv_text.strip():
        raise CSVImportError("CSV payload is empty")

    buffer = io.StringIO(csv_text)
    reader = csv.DictReader(buffer)

    normalised_fieldnames = {field: _normalise_header(field) for field in reader.fieldnames or []}

    missing = EXPECTED_HEADERS - set(normalised_fieldnames.values())
    if missing:
        raise CSVImportError(f"Missing required columns: {', '.join(sorted(missing))}")

    contacts: list[Contact] = []

    for row in reader:
        normalised_row = {normalised_fieldnames.get(k, k): v.strip() for k, v in row.items() if v is not None}

        kwargs: dict[str, object] = {key: normalised_row.get(key) or None for key in EXPECTED_HEADERS}

        for score_key in OPTIONAL_HEADERS:
            raw = normalised_row.get(score_key)
            if raw:
                try:
                    kwargs[score_key] = int(raw)
                except ValueError as exc:
                    raise CSVImportError(f"Invalid integer for {score_key}: {raw}") from exc

        contacts.append(Contact(**kwargs))

    return contacts
