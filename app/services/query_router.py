import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")


client = genai.Client(api_key=API_KEY)

GENERATION_MODEL = "gemini-3.6-flash"


def classify_question(question):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    prompt = f"""
Classify the user's question into exactly one category:

SQL
RAG
HYBRID

SQL:
Use this when the question requires structured business
data, calculations, counts, aggregations, filtering, sorting,
or information stored in the enterprise database.

RAG:
Use this when the question requires information from
unstructured enterprise documents.

HYBRID:
Use this when answering the question requires both structured
database information and information from enterprise documents.

Examples:

"How many orders were delivered?"
SQL

"How many customers are there?"
SQL

"What is the company's return policy?"
RAG

"What does the shipping policy say?"
RAG

"Which product category has the most orders?"
SQL

"Which product category has the most complaints and what does
the company's customer policy say about complaints?"
HYBRID

Return ONLY one word:
SQL
RAG
or
HYBRID

User question:
{question}
"""

    interaction = client.interactions.create(
        model=GENERATION_MODEL,
        input=prompt
    )

    classification = interaction.output_text.strip().upper()

    if classification not in {"SQL", "RAG", "HYBRID"}:
        raise ValueError(
            f"Invalid question classification: {classification}"
        )

    return classification