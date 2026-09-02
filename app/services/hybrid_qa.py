import os
import json

from dotenv import load_dotenv
from google import genai

from app.services.sql_qa import answer_with_sql
from app.services.retriever import retrieve_chunks

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=API_KEY)
GENERATION_MODEL = "gemini-3.6-flash"


def answer_with_hybrid(question):
    """
    Answer a hybrid question using both structured database
    results and unstructured document evidence.
    """

    sql_result = answer_with_sql(question)

    retrieved_chunks = retrieve_chunks(
        query=question,
        top_k=3
    )

    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"Document: {chunk['filename']}\n"
            f"Page: {chunk['page_number']}\n"
            f"Content:\n{chunk['text']}"
        )

    document_context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using BOTH sources of information:

1. STRUCTURED DATABASE RESULT
2. UNSTRUCTURED DOCUMENT CONTEXT

Do not invent information.

If a piece of information is not supported by either source,
say that it is not available.

USER QUESTION:
{question}

STRUCTURED DATABASE RESULT:
SQL:
{sql_result["sql"]}

DATABASE RESULTS:
{json.dumps(sql_result["results"], indent=2)}

UNSTRUCTURED DOCUMENT CONTEXT:
{document_context}

Instructions:

- Combine the database result and document evidence into one
  clear natural-language answer.
- Do not mention internal implementation details.
- Do not expose the SQL unless specifically asked.
- Clearly distinguish facts coming from the database from facts
  coming from the documents when useful.
- Use concise bullet points when they improve readability.
"""

    interaction = client.interactions.create(
        model=GENERATION_MODEL,
        input=prompt
    )

    answer = interaction.output_text.strip()

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
        "answer": answer,
        "sql": sql_result["sql"],
        "sql_results": sql_result["results"],
        "sources": sources
    }