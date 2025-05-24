import os
import datetime
import logging

class Config:
    # Projektpfade
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    
    # Standard-Screening-Konfiguration
    DEFAULT_MIN_PRICE = 1.0  # Standard minimaler Preis für das Screening
    DEFAULT_MIN_VOLUME = 100000  # Standard minimales Volumen für das Screening
    
    # Daten-Konfiguration
    # START_DATE = "2023-01-01"
    # END_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
    # ACTIVE_SYMBOLS = norgatedata.symbols(norgatedata.SymbolType.ACTIVE)
    # DELISTED_SYMBOLS = norgatedata.symbols(norgatedata.SymbolType.DELISTED)
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def setup(cls):
        """Erstellt notwendige Verzeichnisse und konfiguriert Logging"""
        # Verzeichnisse erstellen
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(cls.PROCESSED_DATA_DIR, exist_ok=True)
        
        # Logging konfigurieren
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT
        )
    
    @classmethod
    def get_project_path(cls, *paths):
        """Generiert absolute Pfade relativ zum Projekt-Root"""
        return os.path.join(cls.PROJECT_ROOT, *paths)