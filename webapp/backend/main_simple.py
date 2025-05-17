from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
import norgatedata

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS-Middleware für Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to NorgateTrader API"}

@app.get("/api/watchlists", response_model=List[str])
def get_watchlists():
    """Holt alle verfügbaren Watchlists von Norgate"""
    try:
        logger.info("Versuche Watchlists abzurufen...")
        if not norgatedata.status():
            raise HTTPException(status_code=503, detail="Norgate Data Utility ist nicht aktiv")
        
        watchlists = norgatedata.watchlists()
        logger.info(f"Erfolgreich {len(watchlists)} Watchlists abgerufen")
        return watchlists

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Watchlists: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
