from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from .database import get_db
from .models import screener_models, watchlist_models
from .schemas import screener_schemas, watchlist_schemas
from .services import screener_service, watchlist_service
from .config import settings

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TraderMind API",
    description="Backend API für die TraderMind Trading-Plattform",
    version="1.0.0"
)

# CORS-Middleware für Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Watchlist Routes
@app.get("/api/watchlists", response_model=List[watchlist_schemas.WatchlistBase])
async def get_watchlists(db: Session = Depends(get_db)):
    """Alle verfügbaren Norgate Watchlists abrufen"""
    try:
        return await watchlist_service.get_watchlists()
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Watchlists: {str(e)}")
        raise HTTPException(status_code=500, detail="Interner Serverfehler")

# Screener Routes
@app.post("/api/screener/run", response_model=screener_schemas.ScreenerResult)
async def run_screener(
    request: screener_schemas.ScreenerRequest,
    db: Session = Depends(get_db)
):
    """Screener für eine bestimmte Watchlist ausführen"""
    try:
        return await screener_service.run_screener(
            db=db,
            watchlist_name=request.watchlist_name,
            screener_type=request.screener_type,
            parameters=request.parameters
        )
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Screeners: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler bei der Screener-Ausführung")

@app.get("/api/screener/results/{screener_id}", response_model=screener_schemas.ScreenerResult)
async def get_screener_results(screener_id: int, db: Session = Depends(get_db)):
    """Ergebnisse eines spezifischen Screener-Laufs abrufen"""
    try:
        return await screener_service.get_screener_results(db, screener_id)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Screener-Ergebnisse: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Ergebnisse")