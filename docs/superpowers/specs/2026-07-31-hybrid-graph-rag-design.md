# Design: Hybrid Graph-RAG Search & Extraction Pipeline

Date: 2026-07-31
Status: Approved

## Goal

Lightweight, portfolio-ready enterprise Graph-RAG pipeline demonstrating AI software
engineering fundamentals: PDF ingestion, vector search (Qdrant), knowledge-graph
extraction (Neo4j), hybrid retrieval, FastAPI service. Stack: Python 3.11+, FastAPI,
LlamaIndex, Qdrant, Neo4j, Docker Compose.

## Architecture

### Ingestion (offline script)

```
PDF -> SimpleDirectoryReader (pypdf)
    -> chunk (SentenceSplitter, 512 tokens; every chunk gets a chunk_id)
    -> branch A: embed chunks -> Qdrant collection "docs"
    -> branch B: LLM extracts (subject, relation, object) triples per chunk
              -> Neo4j: (:Entity)-[:REL {chunk_id}]->(:Entity)
```

Key design trick: both branches consume the SAME chunks, and every Neo4j
relationship carries the `chunk_id` it was extracted from. `chunk_id` is the join
key between the vector store and the graph store - no fuzzy entity matching, no
second embedding index on graph nodes.

### Hybrid retrieval (query time)

```
query -> embed -> Qdrant top-k (k=5) vector hits  --+
                                                    +-> merge_context() -> prompt -> LLM -> answer
hit chunk_ids -> Cypher: triples WHERE chunk_id IN hits,
                + 1-hop neighbor expansion ---------+
```

Merging = top-k chunk texts (with similarity scores) plus graph triples rendered as
`subject -relation-> object` lines in one prompt template. The LLM performs the
fusion; no score-fusion math. Hand-rolled merge (~40 lines) is deliberate:
LlamaIndex PropertyGraphIndex would hide exactly the mechanics this project
exists to demonstrate.

## Repository structure (4 core Python files)

```
hybrid-rag/
├── docker-compose.yml      # Qdrant + Neo4j only
├── requirements.txt
├── .env.example
├── README.md
└── app/
    ├── config.py           # dotenv loading + LLM_PROVIDER factory (openai|ollama)
    ├── ingest.py           # python -m app.ingest file.pdf
    ├── retrieve.py         # hybrid retriever + prompt assembly; CLI entrypoint
    └── main.py             # FastAPI: POST /ingest, POST /query, GET /health
```

## Dependencies

```
llama-index-core
llama-index-vector-stores-qdrant
llama-index-graph-stores-neo4j
llama-index-llms-openai
llama-index-embeddings-openai
llama-index-llms-ollama
llama-index-embeddings-ollama
fastapi
uvicorn
python-dotenv
pypdf
python-multipart
```

qdrant-client / neo4j drivers arrive transitively via the store packages.

## Infrastructure

docker-compose.yml, 2 services:

- `qdrant/qdrant` - ports 6333/6334, named volume
- `neo4j:5-community` - ports 7474/7687, `NEO4J_AUTH=neo4j/password`, named volume

Ollama runs on the host (not containerized); OpenAI path needs only
`OPENAI_API_KEY` in `.env`. `LLM_PROVIDER=openai|ollama` selects the provider
via a ~15-line factory in `config.py` that sets LlamaIndex `Settings.llm` /
`Settings.embed_model`.

## Execution phases

| Phase | Deliverable | Test |
|---|---|---|
| 1. Setup | compose, .env.example, requirements, config.py, main.py (/health) | curl /health -> both DBs "ok" |
| 2. Ingestion | ingest.py + sample PDF | point count in Qdrant; `MATCH ()-[r]->() RETURN count(r)` in Neo4j |
| 3. Hybrid retriever | retrieve.py | CLI query answers citing chunk scores + graph triples |
| 4. API | /ingest, /query in main.py | curl both endpoints |

## Trade-offs / key choices

1. Hand-rolled merge over PropertyGraphIndex - demonstrability; costs ~40 lines.
2. `chunk_id` join key; naive entity resolution (no "Apple" vs "Apple Inc." dedup).
   Upgrade path: canonicalization pass, only if needed.
3. Out of scope (YAGNI): auth, streaming, frontend, reranker, eval harness,
   app containerization, CI. Each is a named "next step" in the README.
4. Graph extraction is the slow/expensive branch (one LLM call per chunk).
   Mitigated by 512-token chunks + small demo PDF, not by batching infra.
5. Ollama on host, not in compose - simpler compose; README documents install.
