from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from rag.indexer import FAISSIndexer
from rag.llm import create_llm
from rag.self_rag import SelfRAG
from rag.web_search import WebSearchService

load_dotenv(override=True)
ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evals" / "evaluation_dataset.json"


def load_cases() -> list[dict[str, Any]]:
    return json.loads(DATASET.read_text(encoding="utf-8"))


def expected_source_match(case: dict[str, Any], sources: list[str]) -> bool:
    expected = case.get("expected_source_contains", [])
    if not expected:
        return True
    joined = " ".join(sources).lower()
    return any(item.lower() in joined for item in expected)


def retrieval_evaluation(vector_store, cases: list[dict[str, Any]], k: int):
    results = []
    passed = 0
    for case in cases:
        docs = vector_store.similarity_search(case["question"], k=k)
        sources = []
        for doc in docs:
            source = str(doc.metadata.get("source_file", "unknown.pdf"))
            page = doc.metadata.get("page")
            label = f"{source} page {page}" if page else source
            if label not in sources:
                sources.append(label)

        if case["expected_scope"] == "OUT_OF_SCOPE":
            ok = True
        else:
            ok = bool(docs) and expected_source_match(case, sources)

        passed += int(ok)
        results.append({
            "question": case["question"],
            "expected_scope": case["expected_scope"],
            "retrieved": bool(docs),
            "sources": sources,
            "pass": ok,
            "expected_behavior": case.get("expected_behavior", ""),
        })
    return results, passed


def run_answer_evaluation(rag: SelfRAG, cases: list[dict[str, Any]]):
    results = []
    passed = 0

    for case in cases:
        final_state: dict[str, Any] = {}
        answer_parts: list[str] = []

        for event in rag.stream(case["question"], history=[]):
            if event["type"] == "messages":
                message, metadata = event["data"]
                if metadata.get("langgraph_node") == "generate":
                    content = getattr(message, "content", "")
                    if content:
                        answer_parts.append(content)
            elif event["type"] == "updates":
                for update in event["data"].values():
                    final_state.update(update)

        answer = final_state.get("answer") or "".join(answer_parts)
        source_labels = [s.get("label", "") for s in final_state.get("sources", [])]

        if case["expected_scope"] == "OUT_OF_SCOPE":
            answer_ok = any(word in answer.lower() for word in ("agriculture", "farmer", "farming"))
        else:
            answer_ok = bool(answer.strip())
            if case.get("expected_source_contains"):
                answer_ok = answer_ok and expected_source_match(case, source_labels)

        passed += int(answer_ok)
        results.append({
            "question": case["question"],
            "pass": answer_ok,
            "answer": answer,
            "source_mode": final_state.get("source_mode", ""),
            "sources": final_state.get("sources", []),
            "expected_behavior": case.get("expected_behavior", ""),
        })

    return results, passed


def main():
    parser = argparse.ArgumentParser(description="Evaluate Vikaspedia RAG retrieval and answers.")
    parser.add_argument("--retrieval-only", action="store_true", help="No LLM calls; test FAISS retrieval only.")
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--model", default="gpt-4.1-mini")
    args = parser.parse_args()

    cases = load_cases()
    vector_store = FAISSIndexer().load()

    if args.retrieval_only:
        results, passed = retrieval_evaluation(vector_store, cases, args.k)
        output = ROOT / "evals" / "retrieval_results.json"
    else:
        llm = create_llm(args.model, 0.0)
        rag = SelfRAG(vector_store, llm, WebSearchService(max_results=3), k=args.k)
        results, passed = run_answer_evaluation(rag, cases)
        output = ROOT / "evals" / "answer_results.json"

    total = len(results)
    summary = {
        "passed": passed,
        "total": total,
        "pass_rate": round((passed / total) * 100, 1) if total else 0.0,
        "results": results,
    }
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 70)
    print(" VIKASPEDIA RAG EVALUATION")
    print("=" * 70)
    print(f"Passed    : {passed}/{total}")
    print(f"Pass rate : {summary['pass_rate']}%")
    print(f"Results   : {output}")

    for i, item in enumerate(results, 1):
        print(f"[{i}] {'PASS' if item['pass'] else 'FAIL'} - {item['question']}")


if __name__ == "__main__":
    main()
