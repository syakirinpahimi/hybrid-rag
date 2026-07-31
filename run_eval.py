import json
import sys
from pathlib import Path

from app.retrieve import retrieve

GOLDEN_PATH = Path(__file__).parent / "golden_qa.json"


def hit(texts: list[str], keywords: list[str]) -> bool:
    lowered = [t.lower() for t in texts]
    return any(kw.lower() in t for t in lowered for kw in keywords)


def main() -> None:
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    rows = []
    for item in golden:
        try:
            result = retrieve(item["question"])
        except Exception:
            sys.exit(
                "eval failed: is Qdrant/Neo4j up, the stores populated (run "
                "`python -m app.ingest sample/*.pdf`), and the "
                "LLM provider reachable?"
            )
        chunk_hit = hit([c["text"] for c in result["chunks"]], item["expected"])
        graph_hit = hit(result["triples"], item["expected"])
        answer_hit = hit([result["answer"]], item["expected"])
        rows.append((chunk_hit, graph_hit, answer_hit, item.get("cross_doc", False)))
        print(
            f"{'PASS' if answer_hit else 'FAIL'}  hit={chunk_hit} graph={graph_hit} "
            f"answer={answer_hit}  {item['question']}"
        )

    n = len(rows)
    pct = lambda i: f"{sum(r[i] for r in rows) * 100 / n:.0f}%"
    print(
        f"\nretrieval hit-rate: {pct(0)} | graph coverage: {pct(1)} | "
        f"answer accuracy: {pct(2)} (n={n})"
    )
    for label, subset in (("single-doc", [r for r in rows if not r[3]]),
                          ("cross-doc", [r for r in rows if r[3]])):
        m = len(subset)
        if not m:
            continue
        pct_s = lambda i: f"{sum(r[i] for r in subset) * 100 / m:.0f}%"
        print(
            f"{label}: retrieval {pct_s(0)} | graph {pct_s(1)} | "
            f"answer {pct_s(2)} (n={m})"
        )


if __name__ == "__main__":
    main()
