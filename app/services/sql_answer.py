import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=API_KEY)
GENERATION_MODEL = "gemini-3.6-flash"


def generate_sql_answer(question, sql, results):
    """
    Convert structured SQL results into a concise
    natural-language answer.
    """

    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the database results
provided below.

USER QUESTION:
{question}

SQL QUERY:
{sql}

DATABASE RESULTS:
{json.dumps(results, indent=2)}

Rules:

1. Do not invent facts.
2. Do not perform calculations that are unsupported by the
   database results.
3. Answer directly and concisely.
4. Use natural language rather than exposing SQL.
5. If the result contains a count, clearly state the count.
6. If there are multiple rows, summarize them clearly.
7. If the results are empty, say that no matching data was found.
"""

    interaction = client.interactions.create(
        model=GENERATION_MODEL,
        input=prompt
    )

    return interaction.output_text.strip()