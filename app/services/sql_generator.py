import os
import json

from dotenv import load_dotenv
from google import genai

from app.services.sql_service import get_database_schema


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

    relationships = """
KNOWN TABLE RELATIONSHIPS:

olist_orders.customer_id
    -> olist_customers.customer_id

olist_order_items.order_id
    -> olist_orders.order_id

olist_order_items.product_id
    -> olist_products.product_id

olist_order_items.seller_id
    -> olist_sellers.seller_id

olist_order_payments.order_id
    -> olist_orders.order_id

olist_order_reviews.order_id
    -> olist_orders.order_id

olist_products.product_category_name
    -> olist_category_translation.product_category_name
"""

    prompt = f"""
You are a SQL query generator for an enterprise analytics
application.

Generate a SQL query that answers the user's question using
ONLY the database schema provided below.

DATABASE SCHEMA:
{schema_text}

KNOWN TABLE RELATIONSHIPS:
{relationships}

USER QUESTION:
{question}

Rules:

1. Generate only a single read-only SQL query.

2. The query must begin with SELECT or WITH.

3. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, REPLACE, ATTACH, DETACH, or PRAGMA statements.

4. Use only tables and columns that exist in the schema.

5. Do not invent tables or columns.

6. Use the known table relationships when joins are required.

7. For questions asking for the highest, lowest, most, least,
   top, bottom, maximum, or minimum, use appropriate ORDER BY
   and LIMIT clauses.

8. For counts of orders, use COUNT(DISTINCT order_id) when the
   query joins order_items or other one-to-many tables, unless
   the question explicitly asks for order items.

9. When returning product category names to the user, prefer
   the English category name from
   olist_category_translation when available.

10. Generate a query that directly answers the user's question.
    Do not return unnecessary columns or rows.

11. Return the answer as JSON.

12. The JSON must contain exactly one field named "sql".

13. Do not include markdown code fences.

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

    sql = result.get("sql")

    if not sql:
        raise ValueError(
            "Model response did not contain SQL"
        )

    return sql