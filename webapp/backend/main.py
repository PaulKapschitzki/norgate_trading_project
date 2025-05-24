import sys
from contextlib import asynccontextmanager

from config.config import Config

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import logging
import norgatedata

# Relative imports aus dem backend-Paket
from webapp.backend.database import get_db
from webapp.backend.models.screener_status_new import ScreenerStatus
from webapp.backend.models.screener_models import ScreenerRequest, ScreenerResponse
from webapp.backend.models.backtest_models import BacktestRequest, BacktestResponse
from webapp.backend.services.screener_process import ScreenerProcess
from webapp.backend.services import screener_service

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler für FastAPI.
    Wird beim Start und beim Herunterfahren der Anwendung ausgeführt.
    """
    # Startup
    logger.info("Starting up TraderMind API...")
    ScreenerProcess()  # Initialisiere den ScreenerProcess Singleton
    
    yield  # Server läuft
    
    # Shutdown
    logger.info("Shutting down TraderMind API...")
    await ScreenerProcess().cleanup()  # Cleanup des ScreenerProcess

# FastAPI App erstellen
app = FastAPI(
    title="TraderMind API",
    description="Backend API für die TraderMind Trading-Plattform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS-Middleware für Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to NorgateTrader API"}

@app.get("/api/watchlists", response_model=List[Dict[str, str]])
async def get_watchlists():
    """Holt die verfügbaren Watchlists von Norgate Data."""
    try:
        logger.info("Versuche Watchlists von Norgate Data zu laden...")
        if not norgatedata.status():
            logger.error("Norgate Data Utility ist nicht verfügbar")
            raise HTTPException(
                status_code=503,
                detail="Norgate Data Utility ist nicht verfügbar"
            )
        
        watchlists = norgatedata.watchlists()
        logger.info(f"Erhaltene Watchlists: {watchlists}")
        
        if not watchlists:
            logger.warning("Keine Watchlists gefunden")
            return []
        
        # Konvertiere String-Watchlists in das Dictionary-Format für das Frontend
        result = [{"id": watchlist, "name": watchlist} for watchlist in watchlists]
        logger.info(f"Sende {len(result)} Watchlists ans Frontend")
        return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Laden der Watchlists: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Laden der Watchlists: {str(e)}"
        )

# Screener Routes
@app.post("/api/screener/run", response_model=ScreenerResponse)
async def execute_screener(request: ScreenerRequest, db: Session = Depends(get_db)):
    """Führt einen Screener auf den angegebenen Daten aus"""
    try:
        result = await screener_service.run_screener(
            db=db,
            watchlist_name=request.watchlist_name,
            screener_type=request.screener_type,
            parameters=request.parameters,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return result
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Screeners: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screener/{screener_id}", response_model=ScreenerResponse)
def get_screener_results(screener_id: int, db: Session = Depends(get_db)):
    """Holt Screener-Ergebnisse anhand der ID"""
    try:
        result = screener_service.get_screener_by_id(db, screener_id)
        if not result:
            raise HTTPException(status_code=404, detail="Screener nicht gefunden")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screener/status")
def get_screener_status():
    """Liefert den aktuellen Status des Screeners zurück"""
    try:
        process_manager = ScreenerProcess()
        return process_manager.get_status_response()
    except Exception as e:
        logger.error(f"Error in get_screener_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/screener/stop")
def stop_screener():
    """Stoppt den aktuellen Screening-Prozess"""
    process_manager = ScreenerProcess()
    if process_manager.stop_process():
        return {"message": "Screening-Prozess wird gestoppt"}
    return {"message": "Kein aktiver Screening-Prozess gefunden"}

@app.post("/api/backtest/run", response_model=BacktestResponse)
def execute_backtest(request: BacktestRequest, db: Session = Depends(get_db)):
    """Führt einen Backtest für die angegebene Strategie aus"""
    try:
        from services.backtest_service import run_backtest
        result = run_backtest(
            db=db,
            strategy_type=request.strategy_type,
            parameters=request.parameters,
            symbols=request.symbols,
            watchlist_name=request.watchlist_name,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest/{backtest_id}", response_model=BacktestResponse)
def get_backtest_results(backtest_id: int, db: Session = Depends(get_db)):
    """Holt Backtest-Ergebnisse anhand der ID"""
    try:
        from services.backtest_service import get_backtest_by_id
        result = get_backtest_by_id(db, backtest_id)
        if not result:
            raise HTTPException(status_code=404, detail="Backtest nicht gefunden")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))