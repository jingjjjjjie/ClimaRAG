from fastapi import APIRouter, Depends, HTTPException
from ..services.system_manager import SystemManager
from .models import Query, Response
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_rag_system():
    """Dependency to get the RAG system instance."""
    try:
        return SystemManager.get_instance()
    except Exception as e:
        logger.error(f"Error getting RAG system: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Please wait for initialization to complete."
        )

@router.post("/query", response_model=Response)
async def process_query(query: Query, rag_system = Depends(get_rag_system)):
    try:
        logger.info(f"Processing query: {query.text}")
        result = rag_system.process_query(query.text)
        return Response(
            answer=result['answer'],
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))