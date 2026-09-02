import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

import json

from app.services.retriever import retrieve_chunks

BASE_DIR = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = BASE_DIR / "tests" / "evaluation" / "test_questions.json"


def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_question(question_data, top_k):
    results = retrieve_chunks(
        query=question_data["question"],
        top_k=top_k
    )

    expected_document = question_data["relevant_document"]
    expected_pages = set(question_data["relevant_pages"])

    for result in results:
        if (
            result["filename"] == expected_document
            and result["page_number"] in expected_pages
        ):
            return True

    return False


def calculate_recall_at_k(questions, k):
    hits = 0

    for question in questions:
        if evaluate_question(question, k):
            hits += 1

    return hits / len(questions)


def main():
    questions = load_questions()

    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    for k in [1, 3, 5]:
        hits = 0

        print(f"\nRecall@{k}")

        for question in questions:
            results = retrieve_chunks(
                query=question["question"],
                top_k=k
            )

            expected_document = question["relevant_document"]
            expected_pages = set(question["relevant_pages"])

            hit = any(
                result["filename"] == expected_document
                and result["page_number"] in expected_pages
                for result in results
            )

            if hit:
                hits += 1

            print(
                f"[{'HIT' if hit else 'MISS'}] "
                f"{question['question']}"
            )

            if results:
                top = results[0]

                print(
                    f"     Top result: "
                    f"{top['filename']} | "
                    f"Page {top['page_number']} | "
                    f"Chunk {top['chunk_id']} | "
                    f"Distance {top['distance']:.4f}"
                )

        recall = hits / len(questions)

        print(
            f"\nRecall@{k}: "
            f"{recall:.2%} "
            f"({hits}/{len(questions)})"
        )


if __name__ == "__main__":
    main()