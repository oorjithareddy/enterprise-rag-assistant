import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.sql_qa import answer_with_sql
from app.services.retriever import retrieve_chunks
from app.services.generator import generate_answer
from app.services.hybrid_qa import answer_with_hybrid

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=API_KEY,
    temperature=0
)


def build_route_prompt():
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an enterprise knowledge assistant router.

Classify the user's question into exactly one category:

SQL
RAG
HYBRID

SQL:
Questions requiring structured database information,
counts, calculations, filtering, aggregation, sorting,
or business analytics.

RAG:
Questions requiring information from unstructured
enterprise documents.

HYBRID:
Questions requiring both structured database information
and unstructured enterprise documents.

Return ONLY:
SQL
RAG
or
HYBRID
"""
        ),
        (
            "human",
            "{question}"
        )
    ])


route_prompt = build_route_prompt()


def classify_with_langchain(question):
    """
    Classify a question using a LangChain prompt + Gemini model.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    response = llm.invoke(
        route_prompt.format_messages(
            question=question.strip()
        )
    )

    route = response.content.strip().upper()

    if route not in {"SQL", "RAG", "HYBRID"}:
        raise ValueError(
            f"Invalid LangChain classification: {route}"
        )

    return route


def answer_with_langchain(question):
    """
    Orchestrate SQL, RAG, and HYBRID question handling.

    LangChain provides the orchestration layer while the
    existing services perform the actual retrieval and
    database operations.
    """

    route = classify_with_langchain(question)

    if route == "SQL":
        result = answer_with_sql(question)

        return {
            "route": "SQL",
            "answer": result["answer"],
            "sql": result["sql"],
            "results": result["results"]
        }

    if route == "RAG":
        retrieved_chunks = retrieve_chunks(
            query=question,
            top_k=3
        )

        result = generate_answer(
            question=question,
            retrieved_chunks=retrieved_chunks
        )

        return {
            "route": "RAG",
            "answer": result["answer"],
            "sources": result["sources"]
        }

    if route == "HYBRID":
        result = answer_with_hybrid(question)

        return {
            "route": "HYBRID",
            "answer": result["answer"],
            "sql": result["sql"],
            "results": result["sql_results"],
            "sources": result["sources"]
        }

    raise ValueError(f"Unsupported route: {route}")