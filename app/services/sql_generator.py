import os
import json

from dotenv import load_dotenv
from google import genai

from app.services.sql_service import get_database_schema
from app.services.database_schema import (
    TABLE_DESCRIPTIONS,
    TABLE_RELATIONSHIPS,
    BUSINESS_RULES,
)


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")


client = genai.Client(api_key=API_KEY)

GENERATION_MODEL = "gemini-3.6-flash"


def build_schema_text(schema):
    parts = []

    for table_name, columns in schema.items():
        column_text = ", ".join(
            f"{column['name']} ({column['type']})"
            for column in columns
        )

        parts.append(
            f"Table: {table_name}\n"
            f"Columns: {column_text}"
        )

    return "\n\n".join(parts)


def generate_sql(question):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    schema = get_database_schema()
    schema_text = build_schema_text(schema)

    prompt = f"""
You are a SQL query generator for an enterprise analytics
application.

Your task is to generate one SQLite-compatible SQL query that
directly answers the user's question.

Use ONLY the database schema, table descriptions,
relationships, and business rules provided below.

DATABASE SCHEMA:
{schema_text}

TABLE DESCRIPTIONS:
{json.dumps(TABLE_DESCRIPTIONS, indent=2)}

KNOWN TABLE RELATIONSHIPS:
{TABLE_RELATIONSHIPS}

BUSINESS RULES:
{BUSINESS_RULES}

USER QUESTION:
{question}

Rules:

1. Generate only a single read-only SQL query.

2. The query must begin with SELECT or WITH.

3. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, REPLACE, ATTACH, DETACH, or PRAGMA statements.

4. Use only tables and columns that exist in the database schema.

5. Never invent table names or column names.

6. Use the known table relationships when joins are required.

7. Use SQLite-compatible SQL syntax.

8. Generate a query that directly answers the user's question.

9. Do not return unnecessary columns or rows.

10. For questions asking for the highest, lowest, most, least,
    top, bottom, maximum, or minimum, use an appropriate
    ORDER BY and LIMIT clause.

11. For questions asking how many orders exist after joining
    olist_order_items or another one-to-many table, use
    COUNT(DISTINCT order_id) unless the user explicitly asks
    for the number of order items.

12. When returning product category names, join
    olist_category_translation and prefer the English category
    name when an English translation is available.

13. For questions about revenue or sales value, use the
    appropriate monetary column based on the business rules.

14. For questions involving customer reviews, use
    olist_order_reviews.

15. For questions involving payment amounts, use
    olist_order_payments.payment_value.

16. For questions involving order status, use
    olist_orders.order_status.

17. Do not assume information that is not represented in the
    database.

18. Return ONLY valid JSON.

19. The JSON must contain exactly one field named "sql".

20. Do not include markdown code fences.

Example:

{{"sql": "SELECT COUNT(*) AS order_count FROM olist_orders"}}
"""

    interaction = client.interactions.create(
        model=GENERATION_MODEL,
        input=prompt
    )

    output = interaction.output_text.strip()

    try:
        result = json.loads(output)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Model returned invalid JSON: {output}"
        ) from error

    if not isinstance(result, dict):
        raise ValueError(
            "Model response must be a JSON object"
        )

    sql = result.get("sql")

    if not sql:
        raise ValueError(
            "Model response did not contain SQL"
        )

    if not isinstance(sql, str):
        raise ValueError(
            "Generated SQL must be a string"
        )

    return sql.strip()