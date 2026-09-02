from pathlib import Path

import faiss
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_DIR = BASE_DIR / "data" / "index"

INDEX_PATH = INDEX_DIR / "documents.faiss"


def build_faiss_index(embedded_chunks):
    if not embedded_chunks:
        raise ValueError("No embedded chunks provided")

    vectors = np.array(
        [chunk["embedding"] for chunk in embedded_chunks],
        dtype="float32"
    )

    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(vectors)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_PATH))

    return index