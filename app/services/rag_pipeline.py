from app.processing.preprocessor import preprocess_pdf
from app.services.index_builder import embed_chunks
from app.services.vector_store import add_embeddings_to_index
from app.services.metadata_store import save_metadata


def process_document(file_path, document_id, filename):
    # Step 1: Extract, clean, and chunk the document
    chunks = preprocess_pdf(
        file_path=file_path,
        document_id=document_id,
        filename=filename
    )

    if not chunks:
        raise ValueError("No text could be extracted from the document")

    # Step 2: Generate embeddings
    embedded_chunks = embed_chunks(chunks)

    # Step 3: Add embeddings to the FAISS index
    add_embeddings_to_index(embedded_chunks)

    # Step 4: Save metadata corresponding to the new chunks
    save_metadata(embedded_chunks)

    return {
        "chunk_count": len(embedded_chunks)
    }