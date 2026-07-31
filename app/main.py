import hashlib
import os
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, UploadFile
from neo4j import GraphDatabase
from pydantic import BaseModel
from qdrant_client import QdrantClient

from app.config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER, QDRANT_URL
from app.ingest import main as run_ingestion
from app.retrieve import retrieve

app = FastAPI(title="Hybrid Graph-RAG")


class QueryRequest(BaseModel):
    query: str


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


@app.post("/ingest")
def ingest_pdf(file: UploadFile = File(...)) -> dict:
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        path = tmp.name
    try:
        return run_ingestion(path)
    finally:
        os.unlink(path)


@app.post("/query")
def query_api(req: QueryRequest) -> dict:
    return retrieve(req.query)
