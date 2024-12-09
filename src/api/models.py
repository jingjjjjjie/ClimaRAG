from pydantic import BaseModel
from typing import List, Optional

class Query(BaseModel):
    text: str

class Response(BaseModel):
    answer: str
    # sources: List[str]
    # context: Optional[str] = None 