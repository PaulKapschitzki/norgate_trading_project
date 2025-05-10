import os
import re
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from config.config import Config
from utils.norgate_watchlist_symbols import get_watchlist_symbols

def sanitize_filename(name: str) -> str:
    """
    Wandelt einen Watchlist-Namen in einen gültigen Dateinamen um.
    
    Args:
        name: Der ursprüngliche Watchlist-Name
        
    Returns:
        Bereinigter Dateiname ohne ungültige Zeichen
    """
    # Ersetze Leerzeichen und Sonderzeichen
    sanitized = re.sub(r'[\s&]+', '_', name)
    # Entferne ungültige Zeichen
    sanitized = re.sub(r'[^\w\-_]', '', sanitized)
    return sanitized.lower()

class EnhancedMarketDataManager:
    def __init__(self, watchlist_name: Optional[str] = None, cache_file=None, max_age_days=1):
        """
        Initialisiert den erweiterten Market Data Manager.
        
        Args:
            watchlist_name: Optional, Name der Norgate Watchlist
            cache_file: Optional, Pfad zur Parquet-Datei
            max_age_days: Maximales Alter der Cache-Datei in Tagen
        """
        if cache_file is None:
            if watchlist_name is not None:
                # Erstelle einen sprechenden Dateinamen für die Watchlist
                filename = f"{sanitize_filename(watchlist_name)}_data.parquet"
                cache_file = Config.get_project_path('data', 'raw', filename)
            else:
                # Standard-Datei für allgemeine Marktdaten
                cache_file = Config.get_project_path('data', 'raw', 'database_market_data.parquet')
                
        self.cache_file = Path(cache_file)
        self.max_age_days = max_age_days
        self.watchlist_name = watchlist_name
        
    def is_cache_valid(self) -> bool:
        """Prüft ob Cache-Datei existiert und aktuell ist."""
        if not self.cache_file.exists():
            logging.info(f"Cache-Datei existiert nicht: {self.cache_file}")
            return False
            
        # Prüfe Alter der Datei
        file_age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        if file_age.days > self.max_age_days:
            logging.info(f"Cache ist älter als {self.max_age_days} Tage.")
            return False
            
        return True
        
    def load_market_data(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None,
                         symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Lädt Marktdaten aus Cache oder via Norgate.
        
        Args:
            start_date: Optional, Startdatum im Format 'YYYY-MM-DD'
            end_date: Optional, Enddatum im Format 'YYYY-MM-DD'
            symbols: Optional, Liste der zu ladenden Symbole
            
        Returns:
            DataFrame mit Marktdaten
        """
        # Lade alle Daten aus dem Cache
        if self.is_cache_valid():
            logging.info(f"Lade Daten aus Cache: {self.cache_file}")
            df = pd.read_parquet(self.cache_file)
            
            # Index zu DateTime konvertieren falls nötig
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index) 
        else:
            logging.info("Aktualisiere Cache mit neuen Daten...")
            # Importiere mit vollem Pfad
            from utils.data_fetcher import fetch_all_ohlcv_data, fetch_all_ohlcv_data_from_list
            
            # Definiere Standard-Zeitraum wenn nicht angegeben
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if start_date is None:
                start_date = f"{datetime.now().year - 5}-01-01"
            
            # Hole neue Daten (abhängig davon ob eine Watchlist spezifiziert wurde)
            if self.watchlist_name:
                fetch_all_ohlcv_data_from_list(self.watchlist_name, start_date, end_date, str(self.cache_file))
            else:
                fetch_all_ohlcv_data(start_date, end_date, str(self.cache_file))
                
            df = pd.read_parquet(self.cache_file)
            
        # Filtere nach Datum wenn angegeben
        if start_date:
            df = df[df.index >= pd.Timestamp(start_date)]
        if end_date:
            df = df[df.index <= pd.Timestamp(end_date)]
            
        # Filtere nach Symbolen wenn angegeben
        if symbols:
            df = df[df['Symbol'].isin(symbols)]
            
        # Normalisiere Spaltennamen für Konsistenz mit backtesting_engine.py
        column_mapping = {
            'Close': 'close',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume'
        }
        
        for original, normalized in column_mapping.items():
            if original in df.columns and normalized not in df.columns:
                df[normalized] = df[original]
            
        return df

# Beispiel für die Verwendung
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Zeitraum definieren
    start_date = "2015-04-01"
    end_date = "2025-04-01"
    
    # Beispiel 1: Laden von Daten aus einer bestimmten Watchlist
    watchlist_name = "S&P 500"
    mdm = EnhancedMarketDataManager(watchlist_name=watchlist_name)
    df = mdm.load_market_data(start_date=start_date, end_date=end_date)
    print(f"Geladen: {len(df)} Zeilen für Watchlist {watchlist_name}")
    
    # Beispiel 2: Laden allgemeiner Marktdaten
    general_mdm = EnhancedMarketDataManager()
    general_df = general_mdm.load_market_data(start_date=start_date, end_date=end_date)
    print(f"Geladen: {len(general_df)} Zeilen für allgemeine Marktdaten")