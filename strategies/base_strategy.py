from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, name):
        self.name = name
        self.positions = {}
        self.signals = pd.DataFrame()
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generiert Trading-Signale basierend auf den Eingabedaten"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, data: pd.DataFrame, signal: float) -> float:
        """Berechnet die Positionsgröße basierend auf Signal und Daten"""
        pass
    
    def update(self, data: pd.DataFrame):
        """Aktualisiert die Strategie mit neuen Daten"""
        self.signals = self.generate_signals(data)