from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..models.history_models import ChatSession, ChatMessage, SessionLocal
from ..services.system_manager import SystemManager
from .models import UserQuery, Response, ChatHistory, ConversationResponse
import logging
from uuid import uuid4
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    
@router.put("/chats/{chatId}/changename")
async def update_chat_name(chatId: str, chat_name: str = Query(...), db: Session = Depends(get_db)):
    chat_session = db.query(ChatSession).filter(ChatSession.id == chatId).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    chat_session.chat_name = chat_name  # Update the chat name
    db.commit()
    db.refresh(chat_session)  # Refresh the instance to get the updated data
    return chat_session

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    conversations = db.query(ChatSession).all()
    return [{"id": conv.id, "chat_name": conv.chat_name} for conv in conversations]

@router.get("/chats/{chatId}/messages", response_model=List[ChatHistory])
def get_chat_messages(chatId: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == chatId).all()
    return messages

@router.post('/chats')
async def create_new_chat(db: Session = Depends(get_db)):
    chat_id = str(uuid4())[:8]
    timestamp_cur = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the timestamp
    new_session = ChatSession(id=chat_id, chat_name=timestamp_cur)  # Default name
    db.add(new_session)
    db.commit()
    return {'id': chat_id}

@router.post("/chats/{chatId}/query", response_model=Response)
async def process_query(chatId: str, query: UserQuery, db: Session = Depends(get_db), rag_system = Depends(get_rag_system)):
    try:
        logger.info(f"Processing query: {query.text}")
        result = rag_system.process_query(query.text)
        
        # Save the message to the database
        new_message = ChatMessage(session_id=chatId, role='user', content=query.text)
        db.add(new_message)
        db.commit()

        # Save the response to the database
        response_message = ChatMessage(session_id=chatId, role='assistant', content=result['answer'])
        db.add(response_message)
        db.commit()

        return Response(answer=result['answer'])
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/query", response_model=Response)
async def process_query(query: UserQuery, rag_system = Depends(get_rag_system)):
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