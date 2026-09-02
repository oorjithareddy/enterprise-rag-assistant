from app.services.embeddings import generate_embedding


def embed_chunks(chunks):
    embedded_chunks = []

    for chunk in chunks:
        vector = generate_embedding(chunk["text"])

        embedded_chunks.append({
            **chunk,
            "embedding": vector
        })

    return embedded_chunks