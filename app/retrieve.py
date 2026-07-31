import sys

from llama_index.core import Settings, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from neo4j import GraphDatabase
from qdrant_client import QdrantClient

from app.config import (
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
    QDRANT_URL,
    init_settings,
)
from app.ingest import COLLECTION

TOP_K = 5

GRAPH_CYPHER = """
MATCH (a)-[r:REL]->(b) WHERE any(cid IN r.chunk_ids WHERE cid IN $ids)
WITH collect(DISTINCT a.name) + collect(DISTINCT b.name) AS names
MATCH (x)-[r2:REL]->(y)
WHERE x.name IN names OR y.name IN names
RETURN DISTINCT x.name AS s, r2.type AS t, y.name AS o
"""

ANSWER_PROMPT = """Answer the question using ONLY the retrieved context below.

RETRIEVED CHUNKS (similarity score in parentheses):
{chunks}

KNOWLEDGE GRAPH FACTS:
{triples}

Question: {query}
Answer concisely. If the context does not contain the answer, say so.
"""


def retrieve(query: str) -> dict:
    init_settings()
    qdrant = QdrantClient(url=QDRANT_URL)
    vector_store = QdrantVectorStore(client=qdrant, collection_name=COLLECTION)
    index = VectorStoreIndex.from_vector_store(vector_store)
    hits = index.as_retriever(similarity_top_k=TOP_K).retrieve(query)
    chunks = [(n.node.node_id, n.node.text, n.score) for n in hits]
    ids = [chunk_id for chunk_id, _, _ in chunks]

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        rows = driver.execute_query(GRAPH_CYPHER, ids=ids).records
    # ponytail: drop extraction noise ("..." placeholders) before it pollutes the prompt
    triples = [
        f"{r['s']} -- {r['t']} --> {r['o']}"
        for r in rows
        if "..." not in r["s"] and "..." not in r["t"] and "..." not in r["o"]
    ]

    chunk_text = "\n".join(f"[{score:.3f}] {text[:500]}" for _, text, score in chunks)
    answer = Settings.llm.complete(
        ANSWER_PROMPT.format(
            chunks=chunk_text,
            triples="\n".join(triples) or "(none)",
            query=query,
        )
    ).text.strip()

    return {
        "answer": answer,
        "chunks": [{"score": score, "text": text} for _, text, score in chunks],
        "triples": triples,
    }


if __name__ == "__main__":
    result = retrieve(sys.argv[1])
    print("ANSWER:", result["answer"])
    print("\nCONTEXT:")
    for c in result["chunks"]:
        print(f"  chunk (score {c['score']:.3f}): {c['text'][:120]}...")
    for t in result["triples"]:
        print(f"  triple: {t}")
