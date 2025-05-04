from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging
import pandas as pd
from datetime import datetime

from ..models import screener_models
from ..schemas import screener_schemas
from ...screeners.roc130 import ROC130Screener

logger = logging.getLogger(__name__)

async def run_screener(
    db: Session,
    watchlist_name: str,
    screener_type: str,
    parameters: Optional[Dict] = None
) -> screener_schemas.ScreenerResult:
    """
    Führt einen Screener auf einer bestimmten Watchlist aus
    """
    try:
        # Screener-Run in der Datenbank erstellen
        db_screener_run = screener_models.ScreenerRun(
            screener_type=screener_type,
            watchlist_name=watchlist_name,
            parameters=parameters
        )
        db.add(db_screener_run)
        db.commit()
        db.refresh(db_screener_run)

        # Screener basierend auf Typ auswählen und ausführen
        if screener_type.upper() == "ROC130":
            screener = ROC130Screener(watchlist_name=watchlist_name)
            results = screener.scan(
                roc_threshold=parameters.get('roc_threshold', 40.0) if parameters else 40.0
            )
        else:
            raise ValueError(f"Unbekannter Screener-Typ: {screener_type}")

        # Ergebnisse in der Datenbank speichern
        for result in results:
            db_result = screener_models.ScreenerResult(
                screener_run_id=db_screener_run.id,
                symbol=result['symbol'],
                data={
                    'roc_yesterday': result['roc_yesterday'],
                    'roc_day_before': result['roc_day_before']
                }
            )
            db.add(db_result)
        
        db.commit()
        return await get_screener_results(db, db_screener_run.id)

    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Screeners: {str(e)}")
        db.rollback()
        raise

async def get_screener_results(db: Session, screener_id: int) -> screener_schemas.ScreenerResult:
    """
    Ruft die Ergebnisse eines spezifischen Screener-Laufs ab
    """
    try:
        screener_run = db.query(screener_models.ScreenerRun).filter(
            screener_models.ScreenerRun.id == screener_id
        ).first()

        if not screener_run:
            raise ValueError(f"Screener-Lauf mit ID {screener_id} nicht gefunden")

        return screener_schemas.ScreenerResult(
            id=screener_run.id,
            screener_type=screener_run.screener_type,
            watchlist_name=screener_run.watchlist_name,
            parameters=screener_run.parameters,
            created_at=screener_run.created_at,
            results=[
                screener_schemas.ScreenerResultBase(
                    symbol=result.symbol,
                    data=result.data
                )
                for result in screener_run.results
            ]
        )

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Screener-Ergebnisse: {str(e)}")
        raise