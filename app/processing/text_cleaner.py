import re


def clean_text(text):
    if not text:
        return ""

    # Replace non-breaking spaces with normal spaces
    text = text.replace("\xa0", " ")

    # Remove excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces at the beginning/end of lines
    text = "\n".join(line.strip() for line in text.splitlines())

    return text.strip()