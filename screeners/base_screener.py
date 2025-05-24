from abc import ABC, abstractmethod
import pandas as pd
from config.config import Config
from webapp.backend.services.screener_process import ScreenerProcess
from typing import Optional

class BaseScreener(ABC):
    def __init__(self, name: str, min_price: Optional[float] = None, min_volume: Optional[int] = None):
        self.name = name
        self.config = Config()
        self.process_manager = ScreenerProcess()
        
        # Verwende die übergebenen Werte oder die Standardwerte aus der Config
        self.min_price = min_price if min_price is not None else self.config.DEFAULT_MIN_PRICE
        self.min_volume = min_volume if min_volume is not None else self.config.DEFAULT_MIN_VOLUME
        
    def update_progress(self, total_symbols: int, current_symbol: str) -> None:
        """Aktualisiert den Screener-Fortschritt"""
        if hasattr(self, 'processed_symbols'):
            self.processed_symbols += 1
        else:
            self.processed_symbols = 1
            
        self.process_manager.update_progress(
            total_symbols=total_symbols,
            processed_symbols=self.processed_symbols,
            current_symbol=current_symbol
        )
            
    def check_stop_requested(self) -> bool:
        """Prüft ob der Stopp-Button gedrückt wurde"""
        return self.process_manager.stop_requested
    
    @abstractmethod
    def screen(self, data: pd.DataFrame) -> pd.DataFrame:
        """Führt das Screening auf den Daten durch"""
        pass
    
    def filter_basic_criteria(self, data: pd.DataFrame) -> pd.DataFrame:
        """Wendet grundlegende Filterkriterien an"""
        filtered = data[
            (data['Close'] >= self.min_price) &
            (data['Volume'] >= self.min_volume)
        ]
        return filtered