"""Semantic search over YC companies (command line).

Usage:
    python scripts/search.py "an app that delivers groceries by drone"
    python scripts/search.py "peer-to-peer file sharing" --top 15
"""

import argparse
import sys
from pathlib import Path

# Make the project root importable so we can use the shared search module
# even when running this file directly from the scripts/ folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from search_core import search  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Find similar YC companies.")
    parser.add_argument("query", help="one-sentence startup idea")
    parser.add_argument("--top", type=int, default=10, help="how many results")
    args = parser.parse_args()

    results = search(args.query, args.top)

    print(f'\nTop {len(results)} matches for: "{args.query}"\n')
    for rank, company in enumerate(results, start=1):
        print(f"{rank:2}. {company['name']}  [{company['score']:.3f}]")
        print(f"    {company['batch']} | {company['status']} | {company['industry']}")
        one_liner = company.get("one_liner", "")
        if one_liner:
            print(f"    {one_liner}")
        print(f"    {company['url']}")
        print()


if __name__ == "__main__":
    main()
