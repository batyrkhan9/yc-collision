"""Download the Y Combinator companies dataset.

Fetches the full YC company list from the public yc-oss API and saves it
to data/yc_all.json. Safe to re-run: it overwrites the existing file.
"""

from pathlib import Path

import requests

# Public, community-maintained mirror of YC's company directory.
URL = "https://yc-oss.github.io/api/companies/all.json"

# Resolve paths relative to the project root (the parent of this script's
# folder), so the script works no matter which directory you run it from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "yc_all.json"


def main() -> None:
    print(f"Downloading {URL} ...")
    response = requests.get(URL, timeout=60)
    response.raise_for_status()  # raise an error if the download failed

    # Make sure the data/ folder exists, then write the raw bytes as-is.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(response.content)

    size_mb = OUTPUT_PATH.stat().st_size / 1_000_000
    print(f"Saved to {OUTPUT_PATH} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
