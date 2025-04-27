import sys
import os
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# Projektpfad zum Python Path hinzufügen
project_root = 'e:\\Eigene_Daten\\Programmierung\\Python\\Projects\\norgate_trading_project'
sys.path.append(project_root)

class EnhancedMarketDataManager:
    def __init__(self, cache_file=None, max_age_days=1):
        """
        Initialisiert den erweiterten Market Data Manager.
        
        Args:
            cache_file: Pfad zur Parquet-Datei (absolute Pfadangabe)
            max_age_days: Maximales Alter der Cache-Datei in Tagen
        """
        if cache_file is None:
            # Korrekter Pfad zur market_data.parquet im data/raw/ Verzeichnis
            cache_file = os.path.join(project_root, 'data', 'raw', 'market_data.parquet')
        self.cache_file = Path(cache_file)
        self.max_age_days = max_age_days
        
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
            print(f"Cache file path being used for reading: {self.cache_file}")
            df = pd.read_parquet(self.cache_file)
            
            # Index zu DateTime konvertieren falls nötig
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index) 
        else:
            logging.info("Aktualisiere Cache mit neuen Daten...")
            # Importiere mit vollem Pfad
            sys.path.insert(0, os.path.join(project_root, 'data', 'raw'))
            import utils.data_fetcher as data_fetcher
            
            # Definiere Standard-Zeitraum wenn nicht angegeben
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if start_date is None:
                start_date = f"{datetime.now().year - 5}-01-01"
            
            # Hole neue Daten
            data_fetcher.fetch_all_ohlcv_data(start_date, end_date, str(self.cache_file))
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

# class MarketDataManager:
#     def __init__(self, cache_file="market_data.parquet", max_age_days=1):
#         """
#         Initialisiert den Market Data Manager.
        
#         Args:
#             cache_file: Pfad zur Parquet-Datei
#             max_age_days: Maximales Alter der Cache-Datei in Tagen
#         """
#         self.cache_file = Path(cache_file)
#         self.max_age_days = max_age_days
        
#     def is_cache_valid(self) -> bool:
#         """Prüft ob Cache-Datei existiert und aktuell ist."""
#         if not self.cache_file.exists():
#             logging.info("Cache-Datei existiert nicht.")
#             return False
            
#         # Prüfe Alter der Datei
#         file_age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
#         if file_age.days > self.max_age_days:
#             logging.info(f"Cache ist älter als {self.max_age_days} Tage.")
#             return False
            
#         return True
        
#     def load_market_data(self) -> pd.DataFrame:
#         """Lädt Marktdaten aus Cache oder via Norgate."""
#         if self.is_cache_valid():
#             logging.info("Lade Daten aus Cache...")
#             df = pd.read_parquet(self.cache_file)
            
#             # Index zu DateTime konvertieren falls nötig
#             if not isinstance(df.index, pd.DatetimeIndex):
#                 df.index = pd.to_datetime(df.index) 
                
#             return df
#         else:
#             logging.info("Aktualisiere Cache mit neuen Daten...")
#             from utils.data_fetcher import fetch_all_ohlcv_data
            
#             # Definiere Zeitraum (z.B. letzten 5 Jahre)
#             end_date = datetime.now().strftime("%Y-%m-%d")
#             start_date = (datetime.now().year - 5, "01", "01")
#             start_date = "-".join(map(str, start_date))
            
#             # Hole neue Daten
#             fetch_all_ohlcv_data(start_date, end_date, str(self.cache_file))
#             return pd.read_parquet(self.cache_file)