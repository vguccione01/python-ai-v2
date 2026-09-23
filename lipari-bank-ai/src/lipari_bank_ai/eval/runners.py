import asyncio
import json
from pathlib import Path
from typing import Any

from lipari_bank_ai.db.session import AsyncSessionLocal
from lipari_bank_ai.llm.embedding_client import EmbeddingClient
from lipari_bank_ai.services.categorize_service import CategorizeService
from lipari_bank_ai.services.retrieval_service import RetrievalService
from lipari_bank_ai.types.categorize import CategorizeRequest


async def eval_categorize(dataset_path: Path) -> dict[str, Any]:
    """Run categorize on dataset, return metrics."""
    raw = await asyncio.to_thread(dataset_path.read_text)
    examples = [json.loads(line) for line in raw.splitlines() if line.strip()]

    correct = 0
    failures = []
    total_cost = 0.0
    total_latency = 0.0

    import time

    categorize_service = CategorizeService()

    for ex in examples:
        print(f"\n\nex: {ex}")

        start = time.time()
        req = CategorizeRequest(**ex["input"])
        result = await categorize_service.categorize(req)


        latency = time.time() - start

        is_correct = result.category == ex["expected"]["category"]
        if is_correct:
            correct += 1
        else:
            failures.append({
                "input": ex["input"],
                "expected": ex["expected"],
                "actual": result.model_dump(),
            })

        total_latency += latency
        # cost calcolato dall'API call internally; qui semplificato

    n = len(examples)
    return {
        "accuracy": correct / n,
        "n_examples": n,
        "n_failures": len(failures),
        "avg_latency_s": total_latency / n,
        "failures": failures[:10],  # top 10 failures
    }


if __name__ == "__main__":
    result = asyncio.run(eval_categorize(Path("datasets/categorize_golden.jsonl")))
    print(json.dumps(result, indent=2))

    # Gate: fail if accuracy < threshold
    THRESHOLD = 0.80
    if result["accuracy"] < THRESHOLD:
        print(f"❌ Accuracy {result['accuracy']:.1%} < threshold {THRESHOLD:.0%}")
        exit(1)
    print(f"✅ Accuracy {result['accuracy']:.1%}")


async def eval_rag(dataset_path: Path) -> dict[str, Any]:
    """Eval retrieval recall@5."""
    raw = await asyncio.to_thread(dataset_path.read_text)
    examples = [json.loads(line) for line in raw.splitlines() if line.strip()]

    async with AsyncSessionLocal() as session:
        retrieval = RetrievalService(session, EmbeddingClient())

        correct_at_5 = 0
        correct_at_1 = 0

        print(f"\n\nEXAMPLES: {examples}\n\n")

        for ex in examples:
            chunks = await retrieval.retrieve(ex["query"], top_k=5)
            doc_ids = [c.document_id for c in chunks]

            print(f"\n\nCHUNKS: {chunks}\n\n")
            expected_doc = ex["expected_doc_id"]
            if expected_doc in doc_ids:
                correct_at_5 += 1
            if doc_ids and doc_ids[0] == expected_doc:
                correct_at_1 += 1

        n = len(examples)
        return {
            "recall_at_5": correct_at_5 / n,
            "recall_at_1": correct_at_1 / n,
            "n_examples": n,
        }
