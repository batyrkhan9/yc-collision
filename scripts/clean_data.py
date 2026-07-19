"""Flatten the raw YC dataset into a clean JSONL file.

Reads data/yc_all.json and writes data/companies_clean.jsonl with one JSON
object per line, keeping only the fields the search tool needs.

No company is dropped: inactive/acquired/public companies are kept on purpose,
since finding "dead" companies is a goal of this tool.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "yc_all.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "companies_clean.jsonl"

# The only fields we carry forward, in a stable order.
KEEP_FIELDS = [
    "name",
    "one_liner",
    "long_description",
    "industry",
    "subindustry",
    "tags",
    "batch",
    "status",
    "url",
]

# Fields that should be lists; everything else defaults to an empty string.
LIST_FIELDS = {"tags"}


def clean(company: dict) -> dict:
    """Pull out just the fields we keep, with safe defaults for missing ones."""
    result = {}
    for field in KEEP_FIELDS:
        value = company.get(field)
        if field in LIST_FIELDS:
            result[field] = value if isinstance(value, list) else []
        else:
            # Normalize None / missing to an empty string so every record
            # has the same shape.
            result[field] = value if isinstance(value, str) else ""
    return result


def main() -> None:
    companies = json.loads(INPUT_PATH.read_text())

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for company in companies:
            record = clean(company)
            # ensure_ascii=False keeps accents/emoji readable instead of \uXXXX.
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {len(companies)} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
