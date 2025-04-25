import os
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

class MarketDataManager:
    def __init__(self, cache_file="market_data.parquet", max_age_days=1):
        """
        Initialisiert den Market Data Manager.
        
        Args:
            cache_file: Pfad zur Parquet-Datei
            max_age_days: Maximales Alter der Cache-Datei in Tagen
        """
        self.cache_file = Path(cache_file)
        self.max_age_days = max_age_days
        
    def is_cache_valid(self) -> bool:
        """Prüft ob Cache-Datei existiert und aktuell ist."""
        if not self.cache_file.exists():
            logging.info("Cache-Datei existiert nicht.")
            return False
            
        # Prüfe Alter der Datei
        file_age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        if file_age.days > self.max_age_days:
            logging.info(f"Cache ist älter als {self.max_age_days} Tage.")
            return False
            
        return True
        
    def load_market_data(self) -> pd.DataFrame:
        """Lädt Marktdaten aus Cache oder via Norgate."""
        if self.is_cache_valid():
            logging.info("Lade Daten aus Cache...")
            return pd.read_parquet(self.cache_file)
        else:
            logging.info("Aktualisiere Cache mit neuen Daten...")
            from utils.data_fetcher import fetch_all_ohlcv_data
            
            # Definiere Zeitraum (z.B. letzten 5 Jahre)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now().year - 5, "01", "01")
            start_date = "-".join(map(str, start_date))
            
            # Hole neue Daten
            fetch_all_ohlcv_data(start_date, end_date, str(self.cache_file))
            return pd.read_parquet(self.cache_file)