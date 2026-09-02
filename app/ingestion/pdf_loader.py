import pymupdf


def extract_text_from_pdf(file_path):
    document = pymupdf.open(file_path)

    pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text()

            pages.append({
                "page_number": page_number,
                "text": text
            })

    finally:
        document.close()

    return pages