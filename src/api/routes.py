from fastapi import APIRouter, Depends, HTTPException
from ..services.system_manager import SystemManager
from .models import Query, Response
import logging
from uuid import uuid4

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

@router.post('/chats')
async def create_new_chat():
    chat_id = str(uuid4())[:8]
    # created = int(time())
    
    return {'id': chat_id}

@router.post("/chats/{chatId}/query", response_model=Response)
async def process_query(query: Query, rag_system = Depends(get_rag_system)):
    try:
        logger.info(f"Processing query: {query.text}")
        print(query.text)
        result = rag_system.process_query(query.text)
        return Response(
            answer=result['answer'],
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/query", response_model=Response)
async def process_query(query: Query, rag_system = Depends(get_rag_system)):
    try:
        logger.info(f"Processing query: {query.text}")
        print(query.text)
        result = rag_system.process_query(query.text)
        return Response(
            answer=result['answer'],
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/evaluate", response_model=Response)
async def process_evaluation(query: Query, rag_system = Depends(get_rag_system)):
    try:
        logger.info(f"Processing evaluation query: {query.text}")
        print(query.text)
        result = rag_system.process_evaluation(query.text)
    
        return Response(
            answer=result,
        )
    except Exception as e:
        logger.error(f"Error processing evaluation query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))