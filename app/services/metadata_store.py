import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_DIR = BASE_DIR / "data" / "index"

METADATA_PATH = INDEX_DIR / "metadata.json"


def save_metadata(chunks):
    if not chunks:
        raise ValueError("No metadata provided")

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as file:
            metadata = json.load(file)
    else:
        metadata = []

    metadata.extend(
        {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "text": chunk["text"]
        }
        for chunk in chunks
    )

    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)


def load_metadata():
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_PATH}"
        )

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)