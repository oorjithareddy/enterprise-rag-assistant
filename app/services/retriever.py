import faiss
import numpy as np

from app.services.embeddings import generate_embedding
from app.services.metadata_store import load_metadata
from app.services.vector_store import INDEX_PATH


def retrieve_chunks(query, top_k=3):
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    index = faiss.read_index(str(INDEX_PATH))

    metadata = load_metadata()

    top_k = min(top_k, len(metadata))

    query_vector = generate_embedding(query)

    query_vector = np.array(
        [query_vector],
        dtype="float32"
    )

    distances, indices = index.search(
        query_vector,
        top_k
    )

    results = []

    for rank, (distance, index_position) in enumerate(
        zip(distances[0], indices[0]),
        start=1
    ):
        if index_position == -1:
            continue

        chunk = metadata[index_position]

        results.append({
            "rank": rank,
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "text": chunk["text"],
            "distance": float(distance)
        })

    return results