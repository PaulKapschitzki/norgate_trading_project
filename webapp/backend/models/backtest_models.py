from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class BacktestRequest(BaseModel):
    strategy_type: str
    parameters: Dict[str, Any]
    symbols: List[str] = []
    watchlist_name: str = ""
    start_date: datetime
    end_date: datetime

class BacktestResult(BaseModel):
    symbol: str
    data: Dict[str, Any]

class BacktestResponse(BaseModel):
    strategy_type: str
    parameters: Dict[str, Any]
    results: List[BacktestResult]
    start_date: datetime
    end_date: datetime
    created_at: datetime = datetime.utcnow()
