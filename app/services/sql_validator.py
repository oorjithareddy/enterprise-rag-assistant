import re

from app.services.sql_service import get_database_schema


FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE
)

TABLE_PATTERN = re.compile(
    r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.IGNORECASE
)

CTE_PATTERN = re.compile(
    r"(?:WITH|,)\s*([A-Za-z_][A-Za-z0-9_]*)\s+AS\s*\(",
    re.IGNORECASE
)


def validate_sql(query):
    """
    Validate model-generated SQL before execution.

    Allows:
    - SELECT queries
    - WITH/CTE queries
    - Joins between known database tables
    - References to locally defined CTEs

    Rejects:
    - Write operations
    - Multiple SQL statements
    - Unknown physical database tables
    """

    if not query or not query.strip():
        raise ValueError("SQL query cannot be empty")

    normalized_query = query.strip()

    if not re.match(
        r"^(SELECT|WITH)\b",
        normalized_query,
        re.IGNORECASE
    ):
        raise ValueError("Only SELECT/WITH queries are allowed")

    if FORBIDDEN_SQL.search(normalized_query):
        raise ValueError("Unsafe SQL operation detected")

    if ";" in normalized_query.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed")

    schema = get_database_schema()
    allowed_tables = set(schema.keys())

    cte_names = {
        name.lower()
        for name in CTE_PATTERN.findall(normalized_query)
    }

    referenced_tables = TABLE_PATTERN.findall(normalized_query)

    for table_name in referenced_tables:
        normalized_name = table_name.lower()

        if normalized_name in cte_names:
            continue

        if table_name not in allowed_tables:
            raise ValueError(
                f"Unknown table referenced in SQL: {table_name}"
            )

    # Return the original query exactly as supplied.
    return query