import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

import json

from app.services.retriever import retrieve_chunks


QUESTIONS_PATH = BASE_DIR / "tests" / "evaluation" / "test_questions.json"


def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_question(question_data, top_k=5):
    results = retrieve_chunks(
        query=question_data["question"],
        top_k=top_k
    )

    expected_document = question_data["relevant_document"]
    expected_pages = set(question_data["relevant_pages"])

    return results, expected_document, expected_pages


def is_hit(results, expected_document, expected_pages, k):
    return any(
        result["filename"] == expected_document
        and result["page_number"] in expected_pages
        for result in results[:k]
    )


def main():
    questions = load_questions()

    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    results_by_question = []

    for question in questions:
        results, expected_document, expected_pages = evaluate_question(question)

        results_by_question.append({
            "question": question["question"],
            "results": results,
            "expected_document": expected_document,
            "expected_pages": expected_pages
        })

    for k in [1, 3, 5]:
        hits = 0

        print(f"\nRecall@{k}")

        for evaluation in results_by_question:
            results = evaluation["results"]
            expected_document = evaluation["expected_document"]
            expected_pages = evaluation["expected_pages"]

            hit = is_hit(
                results,
                expected_document,
                expected_pages,
                k
            )

            if hit:
                hits += 1

            print(
                f"[{'HIT' if hit else 'MISS'}] "
                f"{evaluation['question']}"
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