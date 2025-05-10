from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

# Screener-Schemas
class ScreenerRequest(BaseModel):
    watchlist_name: str
    screener_type: str
    parameters: Dict[str, Any]
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ScreenerResultItem(BaseModel):
    symbol: str
    data: Dict[str, Any]
    
class ScreenerResponse(BaseModel):
    status: str
    run_id: Optional[int] = None
    results: Optional[List[ScreenerResultItem]] = None
    message: Optional[str] = None

# Backtest-Schemas
class BacktestRequest(BaseModel):
    strategy_type: str
    parameters: Dict[str, Any]
    symbols: Optional[List[str]] = None
    watchlist_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class BacktestTradeItem(BaseModel):
    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    profit_loss: float
    profit_loss_percent: float

class BacktestResultItem(BaseModel):
    symbol: str
    total_trades: int
    win_rate: float
    avg_return: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    trades: List[BacktestTradeItem]

class BacktestResponse(BaseModel):
    status: str
    run_id: Optional[int] = None
    results: Optional[List[BacktestResultItem]] = None
    message: Optional[str] = None

# Watchlist-Schemas
class WatchlistsResponse(BaseModel):
    watchlists: List[str]