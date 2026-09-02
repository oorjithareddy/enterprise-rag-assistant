from pathlib import Path
from uuid import uuid4

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.database import get_db_connection


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
                "uploaded"
            )
        )

        connection.commit()

        document_id = cursor.lastrowid

    except Exception:
        connection.rollback()

        if file_path.exists():
            file_path.unlink()

        raise

    finally:
        connection.close()

    return jsonify({
        "message": "Document uploaded successfully",
        "document": {
            "id": document_id,
            "filename": original_filename,
            "file_size": file_size,
            "status": "uploaded"
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