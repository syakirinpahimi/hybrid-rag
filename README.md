# Hybrid Graph-RAG Search & Extraction Pipeline

Enterprise-style RAG that combines **vector similarity (Qdrant)** with a
**knowledge graph (Neo4j)** in a single hybrid retrieval prompt. Built with
FastAPI + LlamaIndex.

## Architecture

```
                      ┌────────────► embed ──► Qdrant (vector search)
PDF ──► parse ──► chunk (shared chunk_id)
                      └────────────► LLM triple extraction ──► Neo4j (knowledge graph)

query ──► Qdrant top-k ──┐
                         ├─► merge into one prompt ──► LLM ──► answer
chunk_ids ──► Neo4j ─────┘   (triples + 1-hop expansion)
```

The same chunked text feeds both stores; every Neo4j relationship records the
`chunk_id` it came from. That ID is the join key for hybrid retrieval.

## Setup

```bash
docker compose up -d
python -m venv .venv && .venv\Scripts\activate   # or: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set LLM_PROVIDER + OPENAI_API_KEY (or install Ollama)
uvicorn app.main:app --reload
curl localhost:8000/health   # -> {"qdrant": "ok", "neo4j": "ok"}
```

For `LLM_PROVIDER=ollama`, install Ollama on the host
(`ollama pull llama3.1 && ollama pull nomic-embed-text`) - no API key needed.

## Usage (phases 2-4, in progress)

- `python -m app.ingest <file.pdf>` - ingest a PDF into both stores
- `python -m app.retrieve "<question>"` - hybrid query from the CLI
- `POST /ingest` / `POST /query` - same over the API

## Deliberately out of scope (next steps)

Auth, streaming responses, frontend, reranker, eval harness, app
containerization, CI. The interesting parts (hybrid merge, graph extraction)
are hand-rolled and easy to walk through in an interview.
