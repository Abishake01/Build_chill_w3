import logging
import sys
import json
import uvicorn
import argparse

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from alith.lazai import Client
from alith.lazai.node.middleware import HeaderValidationMiddleware
from alith.lazai.node.validator import decrypt_file_url
from alith import MilvusStore, chunk_text
from alith.query.types import QueryRequest
from alith.query.settlement import QueryBillingMiddleware

import os
from dotenv import load_dotenv

load_dotenv()
# Get OpenAI API key from environment variable
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
# LLM_API_KEY = os.getenv("LLM_API_KEY")
# LLM_BASE_URL = os.getenv("LLM_BASE_URL")
# DSTACK_API_KEY = os.getenv("DSTACK_API_KEY")


# Set the API key for OpenAI
os.environ["PRIVATE_KEY"] = PRIVATE_KEY
os.environ["LLM_BASE_URL"] = LLM_BASE_URL
# os.environ["LLM_API_KEY"] = LLM_API_KEY
# os.environ["LLM_BASE_URL"] = LLM_BASE_URL
# os.environ["DSTACK_API_KEY"] = DSTACK_API_KEY


# Logging configuration
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
client = Client()
app = FastAPI(title="Alith LazAI Privacy Data Query Node", version="1.0.0")

# Fallback in-memory store compatible with MilvusStore API used below
class SimpleStore:
    def __init__(self):
        self._collections = {}

    def has_collection(self, collection_name: str) -> bool:
        return collection_name in self._collections

    def create_collection(self, collection_name: str):
        self._collections.setdefault(collection_name, [])
        return self

    def save_docs(self, docs, collection_name: str):
        self._collections.setdefault(collection_name, [])
        self._collections[collection_name].extend(docs)
        return self

    def search_in(self, query: str, limit: int = 3, score_threshold: float = 0.0, collection_name: str = None):
        docs = self._collections.get(collection_name or "", [])
        # naive ranking: prioritize docs containing the query, then truncate
        contains = [d for d in docs if query.lower() in d.lower()]
        others = [d for d in docs if d not in contains]
        return (contains + others)[:limit]


store = None
collection_prefix = "query_"

def init_store():
    global store
    if store is not None:
        return store
    try:
        logger.info("Initializing MilvusStore (local DB)...")
        store = MilvusStore()
        logger.info("MilvusStore initialized.")
    except Exception as e:
        logger.warning(f"MilvusStore unavailable, using SimpleStore fallback. Reason: {e}")
        store = SimpleStore()
    return store

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}

@app.get("/")
async def root():
    return {"message": "Alith LazAI Privacy Data Query Node", "version": "1.0.0"}


@app.post("/query/rag")
async def query_rag(req: QueryRequest):
    try:
        s = init_store()
        file_id = req.file_id
        if req.file_url:
            file_id = client.get_file_id_by_url(req.file_url)
        if file_id:
            file = client.get_file(file_id)
        else:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=json.dumps(
                    {
                        "error": {
                            "message": "File ID or URL is required",
                            "type": "invalid_request_error",
                        }
                    }
                ),
            )
        owner, file_url, file_hash = file[1], file[2], file[3]
        collection_name = collection_prefix + file_hash
        # Cache data in the vector database
        if not s.has_collection(collection_name):
            encryption_key = client.get_file_permission(
                file_id, client.contract_config.data_registry_address
            )
            data = decrypt_file_url(file_url, encryption_key).decode("utf-8")
            s.create_collection(collection_name=collection_name)
            s.save_docs(chunk_text(data), collection_name=collection_name)
        data = s.search_in(
            req.query, limit=req.limit, collection_name=collection_name
        )
        logger.info(f"Successfully processed request for file: {file}")
        return {
            "data": data,
            "owner": owner,
            "file_id": file_id,
            "file_url": file_url,
            "file_hash": file_hash,
        }
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps(
                {
                    "error": {
                        "message": f"Error processing request for req: {req}. Error: {str(e)}",
                        "type": "internal_error",
                    }
                }
            ),
        )


# Lightweight local testing endpoint that doesn't require LazAI file permissions
@app.post("/query/local")
async def query_local(payload: dict):
    """
    Body example:
    {
      "content": "your raw text to index and search",
      "query": "your question",
      "collection": "optional_collection_name"
    }
    """
    try:
        s = init_store()
        content = payload.get("content", "")
        query = payload.get("query", "")
        collection_name = payload.get("collection", "local_default")
        if not content or not query:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=json.dumps({
                    "error": {
                        "message": "Both 'content' and 'query' are required",
                        "type": "invalid_request_error",
                    }
                }),
            )
        if not s.has_collection(collection_name):
            s.create_collection(collection_name=collection_name)
        s.save_docs(chunk_text(content), collection_name=collection_name)
        data = s.search_in(query, limit=3, collection_name=collection_name)
        return {"data": data, "collection": collection_name}
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({
                "error": {
                    "message": f"Local query failed: {str(e)}",
                    "type": "internal_error",
                }
            }),
        )


def run(host: str = "0.0.0.0", port: int = 8000, *, settlement: bool = False):

    # FastAPI app and LazAI client initialization

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settlement:
        app.add_middleware(HeaderValidationMiddleware)
        app.add_middleware(QueryBillingMiddleware)

    # Ensure store is initialized before serving
    init_store()
    return uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    description = "Alith data query server. Host your own embedding models and support language query!"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--host",
        type=str,
        help="Server host",
        default="0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Server port",
        default=8000,
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model name or path",
        default="/root/models/qwen2.5-1.5b-instruct-q5_k_m.gguf",
    )
    args = parser.parse_args()

    run(host=args.host, port=args.port, settlement=False)
