from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import importlib
import logging

from ..models.screener_models import ScreenerRun, ScreenerResult
from ..schemas.screener_schemas import ScreenerResponse, ScreenerResultItem
from utils.norgate_watchlist_symbols import get_watchlist_symbols
from utils.data_manager import EnhancedMarketDataManager

# Logger konfigurieren
logger = logging.getLogger(__name__)

def run_screener(
    db: Session,
    watchlist_name: str,
    screener_type: str,
    parameters: Dict[str, Any],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> ScreenerResponse:
    """
    Führt einen Screener mit den angegebenen Parametern aus.
    
    Args:
        db: Datenbankverbindung
        watchlist_name: Name der zu scannenden Watchlist
        screener_type: Art des Screeners (z.B. 'roc130')
        parameters: Parameter für den Screener
        start_date: Optional, Startdatum für die Daten
        end_date: Optional, Enddatum für die Daten
        
    Returns:
        ScreenerResponse-Objekt mit den Ergebnissen
    """
    try:
        # Screener-Modul dynamisch laden
        module_path = f"screeners.{screener_type}"
        try:
            screener_module = importlib.import_module(module_path)
            # Get the appropriate screener class (assuming it follows naming convention)
            screener_class_name = ''.join(word.capitalize() for word in screener_type.split('_')) + "Screener"
            screener_class = getattr(screener_module, screener_class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Fehler beim Laden des Screener-Moduls: {str(e)}")
            return ScreenerResponse(
                status="error",
                message=f"Screener {screener_type} nicht gefunden."
            )
        
        # Screener-Run in der Datenbank protokollieren
        screener_run = ScreenerRun(
            screener_type=screener_type,
            parameters=parameters,
            watchlist_name=watchlist_name,
            start_date=start_date,
            end_date=end_date,
            created_at=datetime.utcnow()
        )
        db.add(screener_run)
        db.commit()
        db.refresh(screener_run)
        
        # Screener initialisieren und ausführen
        screener = screener_class(watchlist_name=watchlist_name)
        results = screener.scan(**parameters)
        
        # Ergebnisse in der Datenbank speichern
        db_results = []
        for result in results:
            symbol = result.pop('symbol') if isinstance(result, dict) and 'symbol' in result else ''
            
            db_result = ScreenerResult(
                screener_run_id=screener_run.id,
                symbol=symbol,
                data=result,  # Rest der Daten als JSON
                created_at=datetime.utcnow()
            )
            db.add(db_result)
            db_results.append({
                'symbol': symbol,
                'data': result
            })
        
        db.commit()
        
        # Ergebnisse formatieren und zurückgeben
        result_items = [
            ScreenerResultItem(
                symbol=result['symbol'],
                data=result['data']
            )
            for result in db_results
        ]
        
        return ScreenerResponse(
            status="success",
            run_id=screener_run.id,
            results=result_items
        )
        
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Screeners: {str(e)}", exc_info=True)
        # Rollback der Transaktion bei Fehlern
        if 'screener_run' in locals() and hasattr(screener_run, 'id'):
            db.rollback()
            
        return ScreenerResponse(
            status="error",
            message=f"Fehler beim Ausführen des Screeners: {str(e)}"
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
        return [watchlist['name'] for watchlist in watchlists]
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Watchlists: {str(e)}", exc_info=True)
        return []