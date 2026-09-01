from flask import Blueprint, jsonify


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return jsonify({
        "message": "Enterprise RAG Knowledge Assistant is running",
        "status": "ok"
    })