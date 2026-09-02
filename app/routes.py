from pathlib import Path
from uuid import uuid4

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.database import get_db_connection

from app.services.langchain_orchestrator import answer_with_langchain


main = Blueprint("main", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "data" / "documents"

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@main.route("/")
def home():
    return jsonify({
        "message": "Enterprise RAG Knowledge Assistant is running",
        "status": "ok"
    })


@main.route("/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({
            "error": "No file provided"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Only PDF files are allowed"
        }), 400

    original_filename = secure_filename(file.filename)

    if not original_filename:
        return jsonify({
            "error": "Invalid filename"
        }), 400

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid4().hex}_{original_filename}"
    file_path = UPLOAD_FOLDER / unique_filename

    file.save(file_path)

    file_size = file_path.stat().st_size

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO documents (
                filename,
                file_path,
                file_type,
                file_size,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                original_filename,
                str(file_path.relative_to(BASE_DIR)),
                "application/pdf",
                file_size,
                "processing"
            )
        )

        connection.commit()
        document_id = cursor.lastrowid

    except Exception:
        connection.rollback()

        if file_path.exists():
            file_path.unlink()

        connection.close()
        raise

    connection.close()

    try:
        result = process_document(
            file_path=file_path,
            document_id=document_id,
            filename=original_filename
        )

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE documents
            SET status = ?
            WHERE id = ?
            """,
            ("ready", document_id)
        )

        connection.commit()
        connection.close()

    except Exception as error:
        connection = get_db_connection()

        connection.execute(
            """
            UPDATE documents
            SET status = ?
            WHERE id = ?
            """,
            ("failed", document_id)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "error": "Document processing failed",
            "document_id": document_id,
            "details": str(error)
        }), 500

    return jsonify({
        "message": "Document uploaded and indexed successfully",
        "document": {
            "id": document_id,
            "filename": original_filename,
            "file_size": file_size,
            "status": "ready",
            "chunk_count": result["chunk_count"]
        }
    }), 201


@main.route("/documents", methods=["GET"])
def get_documents():
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                filename,
                file_type,
                file_size,
                uploaded_at,
                status
            FROM documents
            ORDER BY uploaded_at DESC
            """
        ).fetchall()

        documents = [dict(row) for row in rows]

    finally:
        connection.close()

    return jsonify({
        "documents": documents,
        "count": len(documents)
    }), 200

@main.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON"
        }), 400

    question = data.get("question")

    if not question or not question.strip():
        return jsonify({
            "error": "Question is required"
        }), 400

    question = question.strip()

    try:
        result = answer_with_langchain(question)

        response = {
            "question": question,
            "route": result["route"],
            "answer": result["answer"]
        }

        if result["route"] == "SQL":
            response["sql"] = result["sql"]
            response["results"] = result["results"]

        elif result["route"] == "RAG":
            response["sources"] = result["sources"]

        elif result["route"] == "HYBRID":
            response["sql"] = result["sql"]
            response["results"] = result["results"]
            response["sources"] = result["sources"]

        return jsonify(response), 200

    except Exception as error:
        error_message = str(error)

        if "429" in error_message or "quota" in error_message.lower():
            return jsonify({
                "error": "AI service rate limit exceeded",
                "details": "Please retry after the Gemini API quota resets."
            }), 429

        return jsonify({
            "error": "Failed to answer question",
            "details": error_message
        }), 500