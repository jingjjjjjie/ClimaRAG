from pydantic import BaseModel
from typing import List

class UserQuery(BaseModel):
    text: str

class Response(BaseModel):
    answer: str

class ChatHistory(BaseModel):
    session_id: str
    role: str
    content: str

    class Config:
        orm_mode = True  # This allows Pydantic to work with SQLAlchemy models

class Message(BaseModel):
    role: str
    content: str

class ConversationResponse(BaseModel):
    id: str
    chat_name: str