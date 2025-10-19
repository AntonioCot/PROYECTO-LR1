from pydantic import BaseModel
from typing import List, Optional


class ParseRequest(BaseModel):
    grammar: str
    tokens: Optional[List[str]] = None
