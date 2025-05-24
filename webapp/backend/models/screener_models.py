from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date

from webapp.backend.database import Base

# SQLAlchemy Models
class ScreenerRun(Base):
    __tablename__ = "screener_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    screener_type = Column(String, nullable=False)
    watchlist_name = Column(String)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    results = relationship("ScreenerResult", back_populates="screener_run")
    
class ScreenerResult(Base):
    __tablename__ = "screener_results"
    
    id = Column(Integer, primary_key=True, index=True)
    screener_run_id = Column(Integer, ForeignKey("screener_runs.id"))
    symbol = Column(String, nullable=False)
    data = Column(JSON)  # Speichert screener-spezifische Daten
    created_at = Column(DateTime, default=datetime.utcnow)
    
    screener_run = relationship("ScreenerRun", back_populates="results")

class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String, nullable=False)
    parameters = Column(JSON)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    results = relationship("BacktestResult", back_populates="backtest_run")

class BacktestResult(Base):
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_run_id = Column(Integer, ForeignKey("backtest_runs.id"))
    symbol = Column(String, nullable=False)
    total_trades = Column(Integer)
    win_rate = Column(Float)
    avg_return = Column(Float)
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)
    trades = Column(JSON)  # Speichert detaillierte Trade-Informationen
    created_at = Column(DateTime, default=datetime.utcnow)
    
    backtest_run = relationship("BacktestRun", back_populates="results")

# Pydantic Models für API Request/Response
class ScreenerRequest(BaseModel):
    screener_type: str
    watchlist_name: str
    parameters: Dict[str, Any]
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ScreenerResultData(BaseModel):
    symbol: str
    data: Dict[str, Any]
    created_at: datetime

class ScreenerResponse(BaseModel):
    id: int
    screener_type: str
    watchlist_name: str
    parameters: Dict[str, Any]
    results: List[ScreenerResultData]
    created_at: datetime
    
    class Config:
        from_attributes = True