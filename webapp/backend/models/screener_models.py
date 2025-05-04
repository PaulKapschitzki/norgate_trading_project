from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class ScreenerRun(Base):
    __tablename__ = "screener_runs"

    id = Column(Integer, primary_key=True, index=True)
    screener_type = Column(String, nullable=False)  # z.B. "ROC130"
    watchlist_name = Column(String, nullable=False)
    parameters = Column(JSON)  # Screener-spezifische Parameter
    created_at = Column(DateTime, default=datetime.utcnow)
    results = relationship("ScreenerResult", back_populates="screener_run")

class ScreenerResult(Base):
    __tablename__ = "screener_results"

    id = Column(Integer, primary_key=True, index=True)
    screener_run_id = Column(Integer, ForeignKey("screener_runs.id"))
    symbol = Column(String, nullable=False)
    data = Column(JSON)  # Symbol-spezifische Ergebnisse
    created_at = Column(DateTime, default=datetime.utcnow)
    
    screener_run = relationship("ScreenerRun", back_populates="results")