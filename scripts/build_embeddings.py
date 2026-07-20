"""Build semantic-search embeddings for the YC companies.

Reads data/companies_clean.jsonl, turns each company into one combined text,
embeds them all with a local sentence-transformers model, and saves:

  data/embeddings.npy         float32 matrix, shape (num_companies, dim)
  data/embeddings_meta.jsonl  the company records, in the SAME row order

Keeping the vectors and metadata in the same order means row i of the matrix
describes company i in the metadata file.
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "companies_clean.jsonl"
VECTORS_PATH = PROJECT_ROOT / "data" / "embeddings.npy"
META_PATH = PROJECT_ROOT / "data" / "embeddings_meta.jsonl"

# Small, fast, widely-used general-purpose embedding model (~90 MB).
MODEL_NAME = "all-MiniLM-L6-v2"


def build_text(company: dict) -> str:
    """Combine the meaningful fields into one string to embed.

    We lead with the name and one-liner (the crispest signal), then the long
    description, then tags. Empty fields are skipped so we don't embed blanks.
    """
    parts = [
        company.get("name", ""),
        company.get("one_liner", ""),
        company.get("long_description", ""),
        " ".join(company.get("tags", [])),
    ]
    return "\n".join(p for p in parts if p.strip())


def main() -> None:
    # Iterate the file handle (splits only on real newlines). Do NOT use
    # str.splitlines(), which also splits on Unicode separators like
    # that can legitimately appear inside a description.
    with INPUT_PATH.open(encoding="utf-8") as f:
        companies = [json.loads(line) for line in f if line.strip()]
    texts = [build_text(c) for c in companies]
    print(f"Loaded {len(companies)} companies.")

    print(f"Loading model '{MODEL_NAME}' (first run downloads it)...")
    model = SentenceTransformer(MODEL_NAME)

    print("Encoding... (this takes a minute or two on CPU)")
    # normalize_embeddings=True makes vectors unit-length, so a plain dot
    # product equals cosine similarity later during search.
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    ).astype("float32")

    np.save(VECTORS_PATH, embeddings)
    with META_PATH.open("w", encoding="utf-8") as f:
        for company in companies:
            f.write(json.dumps(company, ensure_ascii=False) + "\n")

    print(f"\nSaved vectors {embeddings.shape} to {VECTORS_PATH}")
    print(f"Saved metadata to {META_PATH}")


if __name__ == "__main__":
    main()
