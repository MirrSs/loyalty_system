from pydantic import BaseModel
from typing import Optional


class BasicResponse(BaseModel):
    success: bool
    error: Optional[str] = None
