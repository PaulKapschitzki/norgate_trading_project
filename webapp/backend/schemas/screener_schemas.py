from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class ScreenerRequest(BaseModel):
    watchlist_name: str
    screener_type: str
    parameters: Optional[Dict] = None

class ScreenerResultBase(BaseModel):
    symbol: str
    data: Dict

    class Config:
        from_attributes = True

class ScreenerRunBase(BaseModel):
    screener_type: str
    watchlist_name: str
    parameters: Optional[Dict] = None
    created_at: datetime
    results: List[ScreenerResultBase]

    class Config:
        from_attributes = True

class ScreenerResult(ScreenerRunBase):
    id: int