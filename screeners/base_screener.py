from abc import ABC, abstractmethod
import pandas as pd
from config.config import Config

class BaseScreener(ABC):
    def __init__(self, name: str):
        self.name = name
        self.config = Config()
    
    @abstractmethod
    def screen(self, data: pd.DataFrame) -> pd.DataFrame:
        """Führt das Screening auf den Daten durch"""
        pass
    
    def filter_basic_criteria(self, data: pd.DataFrame) -> pd.DataFrame:
        """Wendet grundlegende Filterkriterien an"""
        return data[
            (data['Close'] >= self.config.MIN_PRICE) &
            (data['Volume'] >= self.config.MIN_VOLUME)
        ]