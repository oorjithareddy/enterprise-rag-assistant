import pytest

from app.services.sql_validator import validate_sql


def test_valid_select_query():
    query = "SELECT COUNT(*) FROM olist_orders"

    result = validate_sql(query)

    assert result == query


def test_valid_with_query():
    query = """
    WITH delivered AS (
        SELECT order_id
        FROM olist_orders
        WHERE order_status = 'delivered'
    )
    SELECT COUNT(*) AS order_count
    FROM delivered
    """

    result = validate_sql(query)

    assert result == query


def test_rejects_delete():
    with pytest.raises(ValueError, match="Only SELECT/WITH queries"):
        validate_sql("DELETE FROM olist_orders")


def test_rejects_unknown_table():
    with pytest.raises(
        ValueError,
        match="Unknown table referenced in SQL"
    ):
        validate_sql("SELECT * FROM fake_table")


def test_rejects_multiple_statements():
    with pytest.raises(
        ValueError,
        match="Multiple SQL statements"
    ):
        validate_sql("SELECT 1; SELECT 2")


def test_rejects_update():
    with pytest.raises(ValueError, match="Only SELECT/WITH queries"):
        validate_sql("UPDATE olist_orders SET order_status = 'x'")