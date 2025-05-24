"""Modelle für den Screener-Status"""
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ScreenerStatus(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    status: str
    progress: Dict[str, Any]
    is_running: bool
