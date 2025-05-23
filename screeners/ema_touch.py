import pandas as pd
import ta
import norgatedata
from .base_screener import BaseScreener
from typing import Dict, List
import logging

class EmaTouchScreener(BaseScreener):
    def __init__(self, 
                 ema_period: int = 20,
                 min_price: float = None,
                 min_volume: int = None,
                 touch_threshold: float = 0.02,
                 required_indices: List[str] = None):
        """
        Initialisiert den EMA Touch Screener.
        
        Args:
            ema_period: Periode für den EMA
            min_price: Minimaler Preis für das Screening (optional, Standard aus Config)
            min_volume: Minimales Volumen für das Screening (optional, Standard aus Config)
            touch_threshold: Maximale Entfernung vom EMA in Prozent
            required_indices: Liste der Indizes, in denen die Aktie sein muss
        """
        super().__init__("EMA Touch", min_price=min_price, min_volume=min_volume)
        self.ema_period = ema_period
        self.touch_threshold = touch_threshold
        self.required_indices = required_indices or ['S&P 500', 'Russell 3000']
        self.processed_symbols = 0
        
    def check_index_membership(self, symbol: str) -> Dict[str, bool]:
        """Prüft die Index-Zugehörigkeit eines Symbols."""
        memberships = {}
        for index_name in self.required_indices:
            try:
                # constituent gibt True zurück wenn das Symbol im Index ist
                is_member = bool(norgatedata.constituent(index_name, symbol))
                memberships[index_name] = is_member
            except Exception as e:
                logging.warning(f"Fehler bei Index-Prüfung für {symbol} in {index_name}: {e}")
                memberships[index_name] = False
        return memberships
    
    def screen(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Führt das Screening durch.
        
        Args:
            data: DataFrame mit OHLCV-Daten und Symbol-Spalte
        
        Returns:
            DataFrame mit gefilterten Aktien
        """
        # Reset index, um Timestamp-Probleme zu vermeiden
        if isinstance(data.index, pd.DatetimeIndex):
            data = data.reset_index()
            
        # Grundlegende Filterung
        filtered_data = self.filter_basic_criteria(data)
        
        # Berechne EMA
        filtered_data['EMA'] = ta.trend.ema_indicator(
            filtered_data['Close'], 
            window=self.ema_period
        )
        
        # Berechne relative Distanz zum EMA
        filtered_data['EMA_Distance'] = abs(filtered_data['Low'] - filtered_data['EMA']) / filtered_data['EMA']
        
        # Berechne technische Indikatoren
        filtered_data['RSI'] = ta.momentum.rsi(filtered_data['Close'])
        filtered_data['MACD'] = ta.trend.macd_diff(filtered_data['Close'])
        
        # Identifiziere EMA-Berührungen mit Threshold
        filtered_data['EMA_Touch'] = (
            (filtered_data['Low'] <= filtered_data['EMA']) &
            (filtered_data['Close'] > filtered_data['EMA']) &
            (filtered_data['EMA_Distance'] <= self.touch_threshold)
        )
        
        # Kombiniere alle Filterkriterien
        mask = (
            filtered_data['EMA_Touch'] &
            (filtered_data['RSI'] < 70) &  # Nicht überkauft
            (filtered_data['MACD'] > 0)    # Positiver MACD
        )
        
        # Finale Filterung
        result = filtered_data[mask].copy()
        
        # Aktualisiere Fortschritt für jedes Symbol
        unique_symbols = filtered_data['Symbol'].unique()
        total_symbols = len(unique_symbols)
        
        # Prüfe Index-Zugehörigkeit für die gefilterten Symbole
        if not result.empty:
            unique_filtered_symbols = result['Symbol'].unique()
            for symbol in unique_filtered_symbols:
                if self.check_stop_requested():
                    logging.info("Screening wurde gestoppt")
                    return pd.DataFrame()
                    
                self.update_progress(total_symbols, symbol)
                
                memberships = self.check_index_membership(symbol)
                # Füge Index-Zugehörigkeit als Spalten hinzu
                for index, is_member in memberships.items():
                    col_name = f'In_{index.replace(" ", "_")}'
                    result.loc[result['Symbol'] == symbol, col_name] = is_member
        
        return result.sort_values('Volume', ascending=False)