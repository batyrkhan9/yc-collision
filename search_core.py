"""Shared semantic-search logic used by both the CLI and the web app.

Loading the model and the index is slow, so we do it once and cache it. Every
later search reuses the same in-memory model and vectors.
"""

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent
VECTORS_PATH = PROJECT_ROOT / "data" / "embeddings.npy"
META_PATH = PROJECT_ROOT / "data" / "embeddings_meta.jsonl"

# Must match the model used in scripts/build_embeddings.py.
MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load():
    """Load vectors, metadata, and the model once, then keep them in memory."""
    if not VECTORS_PATH.exists():
        raise SystemExit(
            "No embeddings found. Run: python scripts/build_embeddings.py"
        )
    vectors = np.load(VECTORS_PATH)
    with META_PATH.open(encoding="utf-8") as f:
        meta = [json.loads(line) for line in f if line.strip()]
    model = SentenceTransformer(MODEL_NAME)
    return vectors, meta, model


def warm_up() -> None:
    """Trigger the one-time load ahead of the first search (used at startup)."""
    _load()


def search(query: str, top: int = 10) -> list[dict]:
    """Return the `top` most similar companies, each with a `score` field."""
    vectors, meta, model = _load()
    query_vec = model.encode([query], normalize_embeddings=True)[0].astype("float32")
    scores = vectors @ query_vec
    top_idx = np.argsort(scores)[::-1][:top]
    return [{**meta[i], "score": float(scores[i])} for i in top_idx]
