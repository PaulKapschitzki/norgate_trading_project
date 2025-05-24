from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import importlib
import logging
import asyncio
from fastapi import HTTPException

from ..models.screener_models import ScreenerRun, ScreenerResult
from ..schemas.screener_schemas import ScreenerResponse, ScreenerResultItem
from utils.norgate_watchlist_symbols import get_watchlist_symbols
from utils.data_manager import EnhancedMarketDataManager
from screeners.run_screener import run_daily_screening
from .screener_process import ScreenerProcess

# Logger konfigurieren
logger = logging.getLogger(__name__)

async def run_screener(
    db: Session,
    watchlist_name: Optional[str],
    screener_type: str,
    parameters: Dict[str, Any],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> ScreenerResponse:
    """
    Führt einen Screener mit den angegebenen Parametern aus.
    
    Args:
        db: Datenbankverbindung
        watchlist_name: Optional, Name der zu scannenden Watchlist
        screener_type: Art des Screeners (z.B. 'roc130')
        parameters: Parameter für den Screener
        start_date: Optional, Startdatum für die Daten
        end_date: Optional, Enddatum für die Daten
        
    Returns:
        ScreenerResponse-Objekt mit den Ergebnissen
    """
    try:
        # Process Manager initialisieren
        process_manager = ScreenerProcess()
        process_manager.status = "initializing"
        process_manager.update_progress(0, 0, "Initialisiere Screener...")
        
        # Speichere initial einen Screener-Lauf in der Datenbank
        screener_run = ScreenerRun(
            screener_type=screener_type,
            watchlist_name=watchlist_name,
            parameters=parameters
        )
        db.add(screener_run)
        db.commit()
        db.refresh(screener_run)

        # Konvertiere Datums-Strings
        start_date_str = start_date.isoformat() if start_date else None
        end_date_str = end_date.isoformat() if end_date else None
        
        # Screening als asynchronen Prozess starten
        async def screening_process():
            try:
                screening_results = run_daily_screening(
                    screener_type=screener_type,
                    parameters=parameters,
                    start_date=start_date_str,
                    end_date=end_date_str,
                    watchlist_name=watchlist_name
                )
                
                if screening_results is None or screening_results.empty:
                    logger.warning("Keine Screening-Ergebnisse gefunden")
                    process_manager.status = "completed"
                    process_manager.update_progress(0, 0, "Keine Ergebnisse gefunden")
                    return
                    
                # Speichere Ergebnisse
                result_items = []
                for symbol in screening_results.index:
                    result = ScreenerResult(
                        screener_run_id=screener_run.id,
                        symbol=symbol,
                        data=screening_results.loc[symbol].to_dict()
                    )
                    db.add(result)
                    result_items.append(result)
                
                db.commit()
                
            except Exception as e:
                logger.error(f"Fehler im Screening-Prozess: {e}")
                process_manager.status = "error"
                process_manager.update_progress(
                    0, 0, "Fehler aufgetreten",
                    error_message=str(e)
                )
                db.rollback()
            finally:
                if process_manager.status not in ["error", "stopping"]:
                    process_manager.status = "completed"
        
        # Starte den Prozess asynchron
        loop = asyncio.get_running_loop()
        task = loop.create_task(screening_process())
        
        # Setze den aktuellen Prozess
        process_manager.current_process = task
        process_manager.status = "running"
        
        return ScreenerResponse(
            id=screener_run.id,
            screener_type=screener_type,
            watchlist_name=watchlist_name,
            parameters=parameters,
            status="started",
            message="Screening-Prozess gestartet",
            results=[],
            created_at=screener_run.created_at
        )
            
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Screeners: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Ausführen des Screeners: {str(e)}"
        )

def get_screener_by_id(db: Session, screener_id: int) -> Optional[ScreenerResponse]:
    """
    Holt einen Screener-Lauf und seine Ergebnisse anhand der ID.
    
    Args:
        db: Datenbankverbindung
        screener_id: ID des Screener-Laufs
        
    Returns:
        ScreenerResponse mit den Ergebnissen oder None, wenn nicht gefunden
    """
    try:
        screener_run = db.query(ScreenerRun).filter(ScreenerRun.id == screener_id).first()
        if not screener_run:
            return None
            
        results = db.query(ScreenerResult).filter(ScreenerResult.screener_run_id == screener_id).all()
        
        result_items = [
            ScreenerResultItem(
                symbol=result.symbol,
                data=result.data
            )
            for result in results
        ]
        
        return ScreenerResponse(
            status="success",
            run_id=screener_run.id,
            results=result_items
        )
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Screener-Laufs: {str(e)}", exc_info=True)
        return ScreenerResponse(
            status="error",
            message=f"Fehler beim Abrufen des Screener-Laufs: {str(e)}"
        )

def get_all_watchlists() -> List[str]:
    """
    Ruft alle verfügbaren Watchlists ab.
    
    Returns:
        Liste von Watchlist-Namen
    """
    import norgatedata
    try:
        watchlists = norgatedata.watchlists()
        return watchlists if watchlists else []
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Watchlists: {str(e)}", exc_info=True)
        return []