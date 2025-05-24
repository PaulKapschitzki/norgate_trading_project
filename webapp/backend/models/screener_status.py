"""Response models für den Screener-Status"""
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ScreenerStatus(BaseModel):
    status: str
    progress: Dict[str, Any]
    is_running: bool

    class Config:
        from_attributes = True
