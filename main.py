import logging
import sys
import json
import uvicorn
import argparse

from fastapi import FastAPI, Response, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from alith.lazai import Client
from alith.lazai.node.middleware import HeaderValidationMiddleware
from alith.lazai.node.validator import decrypt_file_url
from alith import MilvusStore, chunk_text
from alith.query.types import QueryRequest
from alith.query.settlement import QueryBillingMiddleware

import os
from dotenv import load_dotenv
from typing import Optional
import asyncio
import time

load_dotenv()
# Get OpenAI API key from environment variable
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
# LLM_BASE_URL = os.getenv("LLM_BASE_URL")
# DSTACK_API_KEY = os.getenv("DSTACK_API_KEY")


# Set the API key for OpenAI
os.environ["PRIVATE_KEY"] = PRIVATE_KEY
os.environ["LLM_BASE_URL"] = LLM_BASE_URL
os.environ["LLM_API_KEY"] = LLM_API_KEY
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
# Mount CORS early so it applies to all responses including preflight
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/ui")
async def serve_ui():
    return FileResponse("static/index.html")

@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} in {duration_ms}ms"
    )
    return response


@app.api_route("/query/rag", methods=["POST", "OPTIONS"])
async def query_rag(request: Request, req: Optional[QueryRequest] = None):
    # Handle CORS preflight without body parsing
    if request.method == "OPTIONS":
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type="application/json")
    try:
        s = init_store()
        file_id = req.file_id if req else None
        if req and req.file_url:
            file_id = client.get_file_id_by_url(req.file_url)
        # Validate query presence
        query_text = (req.query if req else "") or ""
        if not query_text:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=json.dumps({
                    "error": {
                        "message": "'query' is required",
                        "type": "invalid_request_error",
                    }
                }),
                media_type="application/json",
            )

        if file_id:
            try:
                file = await asyncio.wait_for(
                    asyncio.to_thread(client.get_file, file_id),
                    timeout=8.0,
                )
            except Exception as e:
                logger.exception(f"Failed to fetch file metadata for file_id={file_id}")
                return Response(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    content=json.dumps({
                        "error": {
                            "message": f"Failed to get file metadata: {str(e)}",
                            "type": "upstream_error",
                        }
                    }),
                    media_type="application/json",
                )
            if not file:
                return Response(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=json.dumps({
                        "error": {
                            "message": f"File not found for id {file_id}",
                            "type": "not_found",
                        }
                    }),
                    media_type="application/json",
                )
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
                media_type="application/json",
            )
        owner, file_url, file_hash = file[1], file[2], file[3]
        collection_name = collection_prefix + file_hash
        # Cache data in the vector database
        if not s.has_collection(collection_name):
            # Potentially long operations: permission retrieval + decryption
            try:
                encryption_key = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.get_file_permission,
                        file_id,
                        client.contract_config.data_registry_address,
                    ),
                    timeout=8.0,
                )
            except Exception as e:
                logger.exception(f"Failed to get encryption key for file_id={file_id}")
                # Check for RSA key format issues
                if "PEM" in str(e) or "RSA" in str(e) or "private key" in str(e).lower():
                    return Response(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        content=json.dumps({
                            "error": {
                                "message": "RSA key format error. Please check your PRIVATE_KEY environment variable format.",
                                "type": "configuration_error",
                                "details": str(e)
                            }
                        }),
                        media_type="application/json",
                    )
                else:
                    return Response(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        content=json.dumps({
                            "error": {
                                "message": f"Failed to get encryption key: {str(e)}",
                                "type": "upstream_error",
                            }
                        }),
                        media_type="application/json",
                    )

            try:
                decrypted_bytes = await asyncio.wait_for(
                    asyncio.to_thread(decrypt_file_url, file_url, encryption_key),
                    timeout=10.0,
                )
                data = decrypted_bytes.decode("utf-8")
            except Exception as e:
                logger.exception(
                    f"Decryption failed for file_id={file_id}, url={file_url}"
                )
                return Response(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    content=json.dumps({
                        "error": {
                            "message": f"Failed to decrypt file: {str(e)}",
                            "type": "upstream_error",
                        }
                    }),
                    media_type="application/json",
                )
            s.create_collection(collection_name=collection_name)
            s.save_docs(chunk_text(data), collection_name=collection_name)
        limit = (req.limit if req and getattr(req, 'limit', None) is not None else 3)
        data = s.search_in(query_text, limit=limit, collection_name=collection_name)
        logger.info(f"Successfully processed request for file: {file}")
        return {
            "data": data,
            "owner": owner,
            "file_id": file_id,
            "file_url": file_url,
            "file_hash": file_hash,
        }
    except Exception as e:
        logger.exception("/query/rag failed")
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
            media_type="application/json",
        )


# Lightweight local testing endpoint that doesn't require LazAI file permissions
@app.api_route("/query/local", methods=["POST", "OPTIONS"])
async def query_local(request: Request, payload: Optional[dict] = None):
    """
    Body example:
    {
      "content": "your raw text to index and search",
      "query": "your question",
      "collection": "optional_collection_name"
    }
    """
    # Handle CORS preflight without body parsing
    if request.method == "OPTIONS":
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type="application/json")
    try:
        s = init_store()
        payload = payload or {}
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
                media_type="application/json",
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
            media_type="application/json",
        )


@app.api_route("/analytics/insights", methods=["POST", "OPTIONS"])
async def get_analytics_insights(request: Request, payload: Optional[dict] = None):
    """
    Generate AI-powered insights from data
    Body example:
    {
      "file_id": 2346,
      "analysis_type": "summary|skills|technologies|interests"
    }
    """
    if request.method == "OPTIONS":
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type="application/json")
    
    try:
        payload = payload or {}
        file_id = payload.get("file_id")
        analysis_type = payload.get("analysis_type", "summary")
        
        if not file_id:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=json.dumps({
                    "error": {
                        "message": "File ID is required",
                        "type": "invalid_request_error",
                    }
                }),
                media_type="application/json",
            )
        
        # Get file data
        file = client.get_file(file_id)
        owner, file_url, file_hash = file[1], file[2], file[3]
        
        # Generate insights based on analysis type
        insights = generate_insights(file_id, analysis_type)
        
        return {
            "insights": insights,
            "analysis_type": analysis_type,
            "file_id": file_id,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({
                "error": {
                    "message": f"Analytics generation failed: {str(e)}",
                    "type": "internal_error",
                }
            }),
            media_type="application/json",
        )


@app.api_route("/analytics/trends", methods=["GET", "OPTIONS"])
async def get_analytics_trends(request: Request):
    """
    Get query trends and patterns
    """
    if request.method == "OPTIONS":
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type="application/json")
    
    try:
        # Simulate trend data (in real implementation, this would come from a database)
        trends = {
            "popular_queries": [
                {"query": "What are my main skills?", "count": 15},
                {"query": "Summarize my background", "count": 12},
                {"query": "What technologies do I work with?", "count": 10},
                {"query": "What are my interests?", "count": 8}
            ],
            "query_categories": {
                "skills": 0.4,
                "technologies": 0.3,
                "interests": 0.2,
                "general": 0.1
            },
            "response_times": {
                "average": 250,
                "min": 120,
                "max": 500
            },
            "usage_patterns": {
                "peak_hours": ["09:00", "14:00", "20:00"],
                "most_active_day": "Tuesday"
            }
        }
        
        return trends
        
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({
                "error": {
                    "message": f"Trends analysis failed: {str(e)}",
                    "type": "internal_error",
                }
            }),
            media_type="application/json",
        )


@app.api_route("/demo/query", methods=["POST", "OPTIONS"])
async def demo_query(request: Request, payload: Optional[dict] = None):
    """
    Demo endpoint that works without LazAI encryption
    Uses sample data to demonstrate the application functionality
    """
    if request.method == "OPTIONS":
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type="application/json")
    
    try:
        payload = payload or {}
        query = payload.get("query", "")
        
        if not query:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=json.dumps({
                    "error": {
                        "message": "Query is required",
                        "type": "invalid_request_error",
                    }
                }),
                media_type="application/json",
            )
        
        # Sample data for demonstration
        sample_data = """
        Hey! I'm Abishake, but everyone calls me Abi 👋. 
        I'm super passionate about AI, Web3, and Python — especially when it comes to building projects that mix creativity with tech. 
        I love working on AI agents, Web3 integrations, and smart apps using Django, React, and Tailwind CSS. 
        I mostly build everything solo — from the backend logic to the frontend UI — because I enjoy seeing an idea come alive end to end. 
        Apart from coding, I love teaching; every week, I take Python full-stack classes at my college to help juniors learn programming in a simple and fun way. 
        I always get excited exploring new tech, whether it's smart contracts, AI model integration, or voice-based AI systems. 
        I like keeping my projects clean, modern, and interactive — with smooth animations and a touch of my own style 😎. 
        For me, tech isn't just about code; it's about creating something people can actually feel and enjoy using.
        """
        
        # Simple keyword-based search for demo
        query_lower = query.lower()
        results = []
        
        if any(word in query_lower for word in ["skill", "expertise", "know", "can"]):
            results.append("Primary Skills: Python, Django, React, Tailwind CSS")
            results.append("AI/ML: Experience with AI agents and model integration")
            results.append("Web3: Smart contracts and blockchain development")
            results.append("Teaching: Python full-stack classes and mentoring")
        
        if any(word in query_lower for word in ["technology", "tech", "framework", "tool"]):
            results.append("Frontend: React, Tailwind CSS")
            results.append("Backend: Django, Python")
            results.append("AI/ML: AI agents, model integration")
            results.append("Web3: Smart contracts, blockchain")
            results.append("Tools: Voice-based AI systems")
        
        if any(word in query_lower for word in ["interest", "passion", "love", "enjoy"]):
            results.append("AI and Web3 technologies")
            results.append("Teaching and mentoring")
            results.append("Creative tech projects")
            results.append("Voice-based AI systems")
            results.append("Clean, modern, and interactive design")
        
        if any(word in query_lower for word in ["summarize", "background", "about", "who"]):
            results.append("I'm Abishake (Abi), a passionate developer focused on AI, Web3, and Python")
            results.append("I build full-stack applications using Django, React, and Tailwind CSS")
            results.append("I teach Python full-stack classes at my college")
            results.append("I love working on AI agents, Web3 integrations, and smart contracts")
            results.append("I enjoy creating clean, modern, and interactive projects")
        
        if not results:
            results.append("I'm a passionate developer with expertise in AI, Web3, and Python")
            results.append("I love building full-stack applications and teaching programming")
            results.append("My interests include smart contracts, AI model integration, and voice-based AI systems")
        
        return {
            "data": results[:3],  # Limit to 3 results
            "query": query,
            "source": "demo_data",
            "timestamp": time.time()
        }
        
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({
                "error": {
                    "message": f"Demo query failed: {str(e)}",
                    "type": "internal_error",
                }
            }),
            media_type="application/json",
        )


def generate_insights(file_id: int, analysis_type: str) -> dict:
    """Generate AI-powered insights from data"""
    
    # This is a simplified version - in production, you'd use actual AI models
    insights_map = {
        "summary": {
            "title": "Data Summary",
            "insights": [
                "Your data contains information about AI, Web3, and Python development",
                "Strong focus on full-stack development with modern technologies",
                "Passion for teaching and mentoring others in programming",
                "Interest in voice-based AI systems and smart contracts"
            ],
            "confidence": 0.85
        },
        "skills": {
            "title": "Skills Analysis",
            "insights": [
                "Primary Skills: Python, Django, React, Tailwind CSS",
                "AI/ML: Experience with AI agents and model integration",
                "Web3: Smart contracts and blockchain development",
                "Teaching: Python full-stack classes and mentoring"
            ],
            "confidence": 0.90
        },
        "technologies": {
            "title": "Technology Stack",
            "insights": [
                "Frontend: React, Tailwind CSS",
                "Backend: Django, Python",
                "AI/ML: AI agents, model integration",
                "Web3: Smart contracts, blockchain",
                "Tools: Voice-based AI systems"
            ],
            "confidence": 0.88
        },
        "interests": {
            "title": "Interests & Passions",
            "insights": [
                "AI and Web3 technologies",
                "Teaching and mentoring",
                "Creative tech projects",
                "Voice-based AI systems",
                "Clean, modern, and interactive design"
            ],
            "confidence": 0.82
        }
    }
    
    return insights_map.get(analysis_type, insights_map["summary"])


def run(host: str = "0.0.0.0", port: int = 8000, *, settlement: bool = False):

    # FastAPI app and LazAI client initialization

    # CORS is already mounted at app creation

    # Serve static assets for simple web UI
    app.mount("/static", StaticFiles(directory="static"), name="static")

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
