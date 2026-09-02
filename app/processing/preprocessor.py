import re

from app.ingestion.pdf_loader import extract_text_from_pdf
from app.processing.text_cleaner import clean_text
from app.processing.chunker import chunk_text


def remove_reference_section(text):
    if not text:
        return text, False

    lines = text.splitlines()

    for index, line in enumerate(lines):
        if re.match(r"^\s*References\s*$", line, re.IGNORECASE):
            return "\n".join(lines[:index]), True

    return text, False


def preprocess_pdf(file_path, document_id, filename):
    pages = extract_text_from_pdf(file_path)

    all_chunks = []
    chunk_id = 1
    references_started = False

    for page in pages:
        page_number = page["page_number"]
        raw_text = page["text"]

        if references_started:
            continue

        raw_text, found_references = remove_reference_section(raw_text)

        if found_references:
            references_started = True

        cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            continue

        page_chunks = chunk_text(cleaned_text)

        for chunk in page_chunks:
            all_chunks.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "text": chunk
            })

            chunk_id += 1

    return all_chunks