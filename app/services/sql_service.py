import re

from app.database import get_db_connection


FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE
)


def execute_read_only_query(query, parameters=()):
    """
    Execute a read-only SQL query against the enterprise database.

    Only SELECT/WITH queries are allowed.
    """

    if not query or not query.strip():
        raise ValueError("SQL query cannot be empty")

    query = query.strip()

    if not re.match(r"^(SELECT|WITH)\b", query, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed")

    if FORBIDDEN_SQL.search(query):
        raise ValueError("Unsafe SQL operation detected")

    if ";" in query.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed")

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            query,
            parameters
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_database_schema():
    """
    Return the schema of the Olist enterprise database.
    """

    connection = get_db_connection()

    try:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name LIKE 'olist_%'
            ORDER BY name
            """
        ).fetchall()

        schema = {}

        for row in tables:
            table_name = row["name"]

            columns = connection.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()

            schema[table_name] = [
                {
                    "name": column["name"],
                    "type": column["type"]
                }
                for column in columns
            ]

        return schema

    finally:
        connection.close()