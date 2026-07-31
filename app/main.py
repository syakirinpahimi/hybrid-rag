from contextlib import asynccontextmanager

from fastapi import FastAPI
from neo4j import GraphDatabase
from qdrant_client import QdrantClient

from app.config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER, QDRANT_URL, init_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_settings()
    yield


app = FastAPI(title="Hybrid Graph-RAG", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    status = {}
    try:
        QdrantClient(url=QDRANT_URL).get_collections()
        status["qdrant"] = "ok"
    except Exception as exc:
        status["qdrant"] = f"error: {exc}"
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            driver.verify_connectivity()
        status["neo4j"] = "ok"
    except Exception as exc:
        status["neo4j"] = f"error: {exc}"
    return status
