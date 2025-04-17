import pandas as pd
import ta
import norgatedata
from .base_screener import BaseScreener
from typing import Dict, List
import logging

class EmaTouchScreener(BaseScreener):
    def __init__(self, 
                 ema_period: int = 20,
                 min_price: float = 5.0,
                 min_volume: int = 100000,
                 required_indices: List[str] = None):
        """
        Initialisiert den EMA Touch Screener.
        
        Args:
            ema_period: Periode für den EMA
            min_price: Minimaler Preis für das Screening
            min_volume: Minimales Volumen für das Screening
            required_indices: Liste der Indizes, in denen die Aktie sein muss
        """
        super().__init__("EMA Touch")
        self.ema_period = ema_period
        self.min_price = min_price
        self.min_volume = min_volume
        self.required_indices = required_indices or ['S&P 500', 'Russell 3000']
        
    def check_index_membership(self, symbol: str) -> Dict[str, bool]:
        """Prüft die Index-Zugehörigkeit eines Symbols."""
        memberships = {}
        for index in self.required_indices:
            try:
                # Prüfe aktuelle Index-Zugehörigkeit
                is_member = norgatedata.index_constituent_timeseries(
                    symbol,
                    index,
                    timeseriesformat='pandas-dataframe'
                ).iloc[-1]['Index Constituent']
                memberships[index] = bool(is_member)
            except Exception as e:
                logging.warning(f"Fehler bei Index-Check für {symbol} in {index}: {e}")
                memberships[index] = False
        return memberships
    
    def screen(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Führt das Screening durch.
        
        Args:
            data: DataFrame mit OHLCV-Daten und Symbol-Spalte
        
        Returns:
            DataFrame mit gefilterten Aktien
        """
        # Grundlegende Filterung
        filtered_data = self.filter_basic_criteria(data)
        
        # Berechne EMA
        filtered_data['EMA'] = ta.trend.ema_indicator(
            filtered_data['Close'], 
            window=self.ema_period
        )
        
        # Identifiziere EMA-Berührungen
        filtered_data['EMA_Touch'] = (
            (filtered_data['Low'] <= filtered_data['EMA']) &
            (filtered_data['Close'] > filtered_data['EMA'])
        )
        
        # Zusätzliche Kriterien
        filtered_data['Price_Filter'] = filtered_data['Close'] >= self.min_price
        filtered_data['Volume_Filter'] = filtered_data['Volume'] >= self.min_volume
        
        # Berechne zusätzliche technische Indikatoren
        filtered_data['RSI'] = ta.momentum.rsi(filtered_data['Close'])
        filtered_data['MACD'] = ta.trend.macd_diff(filtered_data['Close'])
        
        # Kombiniere alle Filterkriterien
        mask = (
            filtered_data['EMA_Touch'] &
            filtered_data['Price_Filter'] &
            filtered_data['Volume_Filter'] &
            (filtered_data['RSI'] < 70) &  # Nicht überkauft
            (filtered_data['MACD'] > 0)    # Positiver MACD
        )
        
        # Finale Filterung
        result = filtered_data[mask].copy()
        
        # Prüfe Index-Zugehörigkeit für die gefilterten Symbole
        if not result.empty:
            unique_symbols = result['Symbol'].unique()
            for symbol in unique_symbols:
                memberships = self.check_index_membership(symbol)
                # Füge Index-Zugehörigkeit als Spalten hinzu
                for index, is_member in memberships.items():
                    col_name = f'In_{index.replace(" ", "_")}'
                    result.loc[result['Symbol'] == symbol, col_name] = is_member
        
        return result.sort_values('Volume', ascending=False)