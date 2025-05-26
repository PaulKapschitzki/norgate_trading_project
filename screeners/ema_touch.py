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
        self.required_indices = required_indices if required_indices else []
        self.processed_symbols = 0

    def check_index_membership(self, symbol: str, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prüft die Index-Zugehörigkeit eines Symbols und fügt die Information dem DataFrame hinzu.
        
        Args:
            symbol: Das zu prüfende Symbol
            data: DataFrame mit den Marktdaten für das Symbol
            
        Returns:
            DataFrame mit zusätzlichen Index-Zugehörigkeitsspalten
        """
        for index_name in self.required_indices:
            try:
                logging.info(f"Prüfe ob {symbol} Teil von {index_name} ist...")
                
                # Hole die Index-Mitgliedschaft als Zeitreihe
                index_data = norgatedata.index_constituent_timeseries(
                    symbol,
                    index_name,
                    padding_setting=norgatedata.PaddingType.NONE,
                    pandas_dataframe=data.copy(),  # Übergebe eine Kopie des existierenden DataFrames
                    timeseriesformat='pandas-dataframe'
                )
                
                column_name = f'In_{index_name.replace(" ", "_")}'
                
                if column_name in data.columns:
                    logging.info(f"Spalte {column_name} existiert bereits. Überspringe...")
                    continue
                
                if 'Index Constituent' in index_data.columns:
                    # Benenne die 'Index Constituent' Spalte um
                    index_data.rename(columns={'Index Constituent': column_name}, inplace=True)
                    
                    # Füge die umbenannte Spalte dem originalen DataFrame hinzu
                    data[column_name] = index_data[column_name]
                else:
                    logging.warning(f"'Index Constituent' Spalte nicht gefunden für {symbol} in {index_name}")
                    # Setze die Spalte auf False wenn keine Daten verfügbar sind
                    data[column_name] = False
                    
            except Exception as e:
                logging.warning(f"Fehler bei Index-Prüfung für {symbol} in {index_name}: {e}")
                column_name = f'In_{index_name.replace(" ", "_")}'
                data[column_name] = False
                
        return data

    def screen(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Führt das Screening durch.
        
        Args:
            data: DataFrame mit OHLCV-Daten und Symbol-Spalte
        
        Returns:
            DataFrame mit gefilterten Aktien
        """
        # Erstelle eine Kopie der Daten zu Beginn
        working_data = data.copy()
        
        # Reset index, um Timestamp-Probleme zu vermeiden
        if isinstance(working_data.index, pd.DatetimeIndex):
            working_data = working_data.reset_index()
            
        # Grundlegende Filterung
        working_data = self.filter_basic_criteria(working_data)
        
        # Berechne technische Indikatoren
        working_data.loc[:, 'EMA'] = ta.trend.ema_indicator(
            working_data['Close'], 
            window=self.ema_period
        )
        
        # Berechne relative Distanz zum EMA
        working_data.loc[:, 'EMA_Distance'] = abs(working_data['Low'] - working_data['EMA']) / working_data['EMA']
        
        working_data.loc[:, 'RSI'] = ta.momentum.rsi(working_data['Close'])
        working_data.loc[:, 'MACD'] = ta.trend.macd_diff(working_data['Close'])
        
        # Identifiziere EMA-Berührungen mit Threshold
        working_data.loc[:, 'EMA_Touch'] = (
            (working_data['Low'] <= working_data['EMA']) &
            (working_data['Close'] > working_data['EMA']) &
            (working_data['EMA_Distance'] <= self.touch_threshold)
        )
        
        # Kombiniere alle Filterkriterien
        mask = (
            working_data['EMA_Touch'] &
            (working_data['RSI'] < 70) &  # Nicht überkauft
            (working_data['MACD'] > 0)    # Positiver MACD
        )
        
        # Finale Filterung
        result = working_data[mask]
        
        # Aktualisiere Fortschritt für jedes Symbol
        unique_symbols = result['Symbol'].unique()
        total_symbols = len(unique_symbols)
        
        # Prüfe Index-Zugehörigkeit für die gefilterten Symbole
        if not result.empty:
            # Temporärer DataFrame für die Endergebnisse
            final_result = pd.DataFrame()
            
            for symbol in unique_symbols:
                if self.check_stop_requested():
                    logging.info("Screening wurde gestoppt")
                    return pd.DataFrame()
                    
                self.update_progress(total_symbols, symbol)
                
                # Hole die Symbol-spezifischen Daten
                symbol_data = result[result['Symbol'] == symbol]
                
                # Prüfe Index-Zugehörigkeit und aktualisiere die Daten
                symbol_data = self.check_index_membership(symbol, symbol_data)
                
                # Füge die Daten zum Endergebnis hinzu
                final_result = pd.concat([final_result, symbol_data])
            
            # Ersetze das ursprüngliche result mit dem aktualisierten DataFrame
            result = final_result
        
        return result.sort_values('Volume', ascending=False)