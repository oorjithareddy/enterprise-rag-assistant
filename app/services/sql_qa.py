from app.services.sql_generator import generate_sql
from app.services.sql_service import execute_read_only_query
from app.services.sql_answer import generate_sql_answer
from app.services.sql_validator import validate_sql

def answer_with_sql(question):
    sql = generate_sql(question)

    sql = validate_sql(sql)

    results = execute_read_only_query(sql)

    answer = generate_sql_answer(
        question=question,
        sql=sql,
        results=results
    )

    return {
        "answer": answer,
        "sql": sql,
        "results": results
    }