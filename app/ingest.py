import json
import sys
import uuid

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.config import (
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
    QDRANT_URL,
    init_settings,
)

COLLECTION = "docs"

EXTRACT_PROMPT = """Extract factual relationships from the text below as a JSON list.
Each item: {{"subject": "...", "relation": "...", "object": "..."}}
Use short entity names (no quotes or prefixes). Only facts present in the text.
Text: {text}
JSON:"""


def extract_triples(text: str) -> list[dict]:
    resp = Settings.llm.complete(EXTRACT_PROMPT.format(text=text))
    raw = resp.text.strip()
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON list in LLM response: {raw[:200]!r}")
    try:
        triples = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        # qwen occasionally emits raw newlines inside string values
        triples = json.loads(raw[start : end + 1].replace("\n", "").replace("\r", ""))
    return [
        t
        for t in triples
        if isinstance(t, dict) and {"subject", "relation", "object"} <= set(t)
    ]

def main(pdf_path: str) -> dict:
    init_settings()
    qdrant = QdrantClient(url=QDRANT_URL)
    dim = len(Settings.embed_model.get_text_embedding("probe"))
    if COLLECTION not in {c.name for c in qdrant.get_collections().collections}:
        qdrant.create_collection(
            COLLECTION, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )
    vector_store = QdrantVectorStore(client=qdrant, collection_name=COLLECTION)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    docs = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
    # splitter feeds node.get_content() (metadata included) into splitting, so strip
    # path/name/timestamps or chunk boundaries change per ingest path and chunk IDs diverge
    for doc in docs:
        doc.metadata = {}
    nodes = SentenceSplitter(chunk_size=512, chunk_overlap=40, include_metadata=False).get_nodes_from_documents(docs)
    for node in nodes:
        # deterministic id: re-ingesting the same PDF upserts instead of duplicating
        node.node_id = str(uuid.uuid5(uuid.NAMESPACE_URL, node.text))
    print(f"chunks: {len(nodes)}")
    VectorStoreIndex(nodes, storage_context=storage_context)  # embeds + upserts to Qdrant

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        driver.verify_connectivity()
        triple_count = 0
        for node in nodes:
            try:
                triples = extract_triples(node.text)
            except (ValueError, json.JSONDecodeError) as exc:
                print(f"warning: chunk {node.node_id[:8]} failed: {exc}")
                continue
            for t in triples:
                driver.execute_query(
                    """
                    MERGE (s:Entity {name: $s})
                    MERGE (o:Entity {name: $o})
                    MERGE (s)-[r:REL]->(o)
                    ON CREATE SET r.type = $rel, r.chunk_ids = [$chunk_id]
                    ON MATCH SET r.chunk_ids = CASE WHEN $chunk_id IN r.chunk_ids
                                      THEN r.chunk_ids ELSE r.chunk_ids + $chunk_id END
                    """,
                    s=t["subject"],
                    o=t["object"],
                    rel=t["relation"],
                    chunk_id=node.node_id,
                )
                triple_count += 1
        entity_count = driver.execute_query("MATCH (e:Entity) RETURN count(e) AS c").records[0]["c"]
        rel_count = driver.execute_query("MATCH ()-[r:REL]->() RETURN count(r) AS c").records[0]["c"]

    points = qdrant.get_collection(COLLECTION).points_count
    print(f"qdrant points: {points}")
    print(f"entities: {entity_count}, relationships: {rel_count} (new: {triple_count})")
    return {
        "chunks": len(nodes),
        "qdrant_points": points,
        "entities": entity_count,
        "relationships": rel_count,
        "new_triples": triple_count,
    }


if __name__ == "__main__":
    for path in sys.argv[1:]:
        main(path)
