import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")


client = genai.Client(api_key=API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"


def generate_embedding(text):
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values