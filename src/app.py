"""
FastAPI Application Entry Point for the RAG Summarization System
---------------------------------------------------------------

This module defines the main web application for the Retrieval-Augmented Generation (RAG) system.
It exposes RESTful API endpoints that handle document retrieval, summarization, and knowledge-based
question answering.

When the server starts, it initializes the RAG pipeline (vector stores, models, etc.)
through the `SystemManager` class. The API routes are organized under `/api/v1`.

Typical usage:
---------------
$ python -m src.app
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .services.system_manager import SystemManager
from .api.routes import router

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG System API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    # Initialize the RAG system through the manager
    SystemManager.initialize()
    logger.info("Application startup complete")

# Include API routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)