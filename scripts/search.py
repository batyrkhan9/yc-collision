"""Semantic search over YC companies.

Usage:
    python scripts/search.py "an app that delivers groceries by drone"
    python scripts/search.py "peer-to-peer file sharing" --top 15

Embeds your query with the same model used to build the index, compares it
against every company vector, and prints the most similar companies -- alive
or dead -- ranked by cosine similarity.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTORS_PATH = PROJECT_ROOT / "data" / "embeddings.npy"
META_PATH = PROJECT_ROOT / "data" / "embeddings_meta.jsonl"

# Must match the model used in build_embeddings.py, or the vectors won't
# live in the same "meaning space" and results will be nonsense.
MODEL_NAME = "all-MiniLM-L6-v2"


def load_index():
    """Load the precomputed vectors and their aligned company metadata."""
    if not VECTORS_PATH.exists():
        raise SystemExit(
            "No embeddings found. Run: python scripts/build_embeddings.py"
        )
    vectors = np.load(VECTORS_PATH)
    with META_PATH.open(encoding="utf-8") as f:
        meta = [json.loads(line) for line in f if line.strip()]
    return vectors, meta


def search(query: str, top: int):
    vectors, meta = load_index()

    model = SentenceTransformer(MODEL_NAME)
    # Normalize the query the same way we normalized the index, so the dot
    # product below is a true cosine similarity in [-1, 1].
    query_vec = model.encode([query], normalize_embeddings=True)[0].astype("float32")

    # One matrix-vector product scores all companies at once.
    scores = vectors @ query_vec

    # argsort is ascending; take the last `top` and reverse for descending.
    top_idx = np.argsort(scores)[::-1][:top]
    return [(meta[i], float(scores[i])) for i in top_idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Find similar YC companies.")
    parser.add_argument("query", help="one-sentence startup idea")
    parser.add_argument("--top", type=int, default=10, help="how many results")
    args = parser.parse_args()

    results = search(args.query, args.top)

    print(f'\nTop {len(results)} matches for: "{args.query}"\n')
    for rank, (company, score) in enumerate(results, start=1):
        print(f"{rank:2}. {company['name']}  [{score:.3f}]")
        print(f"    {company['batch']} | {company['status']} | {company['industry']}")
        one_liner = company.get("one_liner", "")
        if one_liner:
            print(f"    {one_liner}")
        print(f"    {company['url']}")
        print()


if __name__ == "__main__":
    main()
