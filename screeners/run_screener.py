import logging
from datetime import datetime
from typing import Dict, Any, Optional, Type, List
import importlib
import pandas as pd

from config.config import Config
from screeners.base_screener import BaseScreener
from utils.data_downloader import download_all_stock_data
from utils.norgate_database_symbols import get_active_symbols
from utils.norgate_watchlist_symbols import get_watchlist_symbols
from webapp.backend.services.screener_process import ScreenerProcess

def get_symbols(watchlist_name: Optional[str] = None) -> List[str]:
    """
    Holt die Symbole entweder aus einer Watchlist oder aus der gesamten Datenbank.
    
    Args:
        watchlist_name: Optional, Name der Watchlist
    
    Returns:
        Liste von Symbolen
    """
    if watchlist_name:
        return get_watchlist_symbols(watchlist_name)
    return get_active_symbols()

def get_screener_class(screener_type: str) -> Type[BaseScreener]:
    """
    Lädt die Screener-Klasse dynamisch basierend auf dem Screener-Typ.
    
    Args:
        screener_type: Name des Screeners (z.B. 'ema_touch')
    
    Returns:
        Screener-Klasse
    """
    try:
        module_name = f"screeners.{screener_type}"
        module = importlib.import_module(module_name)
        class_name = ''.join(word.capitalize() for word in screener_type.split('_')) + "Screener"
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Screener-Typ '{screener_type}' nicht gefunden: {str(e)}")

def run_daily_screening(
    screener_type: str = "ema_touch",
    parameters: Dict[str, Any] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    watchlist_name: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Führt das tägliche Screening durch
    
    Args:
        screener_type: Art des Screeners (z.B. 'ema_touch')
        parameters: Parameter für den Screener
        start_date: Startdatum für die Marktdaten im Format 'YYYY-MM-DD'
        end_date: Enddatum für die Marktdaten im Format 'YYYY-MM-DD'
        watchlist_name: Optional, Name der Watchlist für das Screening
    """
    Config.setup()
    process_manager = ScreenerProcess()
    
    try:
        # Screener-Klasse dynamisch laden
        screener_class = get_screener_class(screener_type)
        
        # Screener mit übergebenen Parametern initialisieren
        screener_params = parameters or {}
        screener = screener_class(**screener_params)
        
        # Hole Symbole aus Watchlist oder Datenbank
        symbols = get_symbols(watchlist_name)
        total_symbols = len(symbols)
        logging.info(f"Gefundene Symbole: {total_symbols} {'in Watchlist ' + watchlist_name if watchlist_name else 'in Datenbank'}")
        
        if not symbols:
            logging.error("Keine Symbole gefunden")
            return None
        
        # Setze Default-Werte für Datum wenn nicht angegeben
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            # Standard: 1 Jahr zurück vom Enddatum
            start_date = (datetime.strptime(end_date, "%Y-%m-%d").replace(year=datetime.strptime(end_date, "%Y-%m-%d").year - 1)).strftime("%Y-%m-%d")
        
        # Lade aktuelle Marktdaten
        market_data = download_all_stock_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        if market_data.empty:
            logging.error("Keine Marktdaten geladen")
            return None
        
        # Aktualisiere den Fortschritt
        process_manager.update_progress(
            total_symbols=total_symbols,
            processed_symbols=0,
            current_symbol="Starte Screening..."
        )
            
        # Führe Screening durch
        results = screener.screen(market_data)
        
        # Prüfe, ob der Prozess gestoppt wurde
        if process_manager.stop_requested:
            logging.info("Screening-Prozess wurde gestoppt")
            return None
            
        # Speichere Ergebnisse
        output_path = Config.get_project_path('data', 'processed', f'screener_results_{end_date}.parquet')
        results.to_parquet(output_path)
        logging.info(f"Screening Ergebnisse gespeichert in: {output_path}")
        
        return results
        
    except Exception as e:
        logging.error(f"Fehler beim Screening-Prozess: {e}")
        return None