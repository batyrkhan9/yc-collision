"""Validate the downloaded YC dataset (data/yc_all.json).

Reports, so we can eyeball data quality before cleaning:
  (a) total company count
  (b) every unique `status` value and how many companies have each
  (c) percentage of companies with a non-empty `long_description`
  (d) one sample record each for Active / Inactive / Acquired
"""

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "yc_all.json"

# Fields we care about for the final tool (used when printing samples).
SAMPLE_FIELDS = ["name", "batch", "status", "industry", "one_liner", "long_description"]


def non_empty(value) -> bool:
    """True if the value is a string with actual (non-whitespace) content."""
    return isinstance(value, str) and value.strip() != ""


def print_sample(label: str, company: dict) -> None:
    print(f"\n--- Sample: {label} ---")
    if company is None:
        print("  (no company with this status found)")
        return
    for field in SAMPLE_FIELDS:
        value = company.get(field, "")
        text = str(value)
        # Keep long_description readable in the terminal.
        if len(text) > 200:
            text = text[:200] + "..."
        print(f"  {field}: {text}")


def main() -> None:
    companies = json.loads(DATA_PATH.read_text())

    # (a) total count
    total = len(companies)
    print(f"(a) Total companies: {total}")

    # (b) status breakdown
    print("\n(b) Status values and counts:")
    status_counts = Counter(c.get("status") for c in companies)
    for status, count in status_counts.most_common():
        pct = count / total * 100
        print(f"  {str(status):12} {count:5}  ({pct:5.1f}%)")

    # (c) long_description fill rate
    with_desc = sum(1 for c in companies if non_empty(c.get("long_description")))
    pct_desc = with_desc / total * 100
    print(f"\n(c) Non-empty long_description: {with_desc}/{total} ({pct_desc:.1f}%)")

    # (d) one sample per status of interest
    print("\n(d) Sample records:")
    for label in ["Active", "Inactive", "Acquired"]:
        sample = next((c for c in companies if c.get("status") == label), None)
        print_sample(label, sample)


if __name__ == "__main__":
    main()
