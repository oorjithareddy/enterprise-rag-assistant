import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")


client = genai.Client(api_key=API_KEY)

GENERATION_MODEL = "gemini-3.6-flash"


def generate_answer(question, retrieved_chunks):
    if not retrieved_chunks:
        return {
            "answer": "I could not find relevant information in the provided documents.",
            "sources": []
        }

    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"[Source: {chunk['filename']}, Page {chunk['page_number']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the information provided
in the context below.

Do not use outside knowledge.

If the context does not contain enough information to answer the
question, say that the information is not available in the provided
documents.

Do not invent facts, sources, page numbers, or citations.

Context:
{context}

User question:
{question}

Provide a concise, accurate answer.
"""

    interaction = client.interactions.create(
        model=GENERATION_MODEL,
        input=prompt
    )

    sources = [
        {
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "chunk_id": chunk["chunk_id"],
            "distance": chunk["distance"]
        }
        for chunk in retrieved_chunks
    ]

    return {
        "answer": interaction.output_text,
        "sources": sources
    }