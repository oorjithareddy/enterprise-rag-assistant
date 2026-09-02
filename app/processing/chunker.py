def chunk_text(text, chunk_size=400, overlap=80):
    if not text:
        return []

    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks