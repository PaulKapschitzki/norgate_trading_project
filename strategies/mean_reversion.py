import pandas as pd
import numpy as np

class MeanReversionStrategy:
    def __init__(self, gap_threshold=-0.03):
        """
        Args:
            gap_threshold: Schwellwert für Overnight-Gap (default -3%)
        """
        self.gap_threshold = gap_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generiert Trading Signale basierend auf Overnight-Gaps."""
        
        # Kopie erstellen um original nicht zu verändern
        df = df.copy()
        
        # Nach Symbol gruppieren und Gaps berechnen
        df['prev_close'] = df.groupby('Symbol')['Close'].shift(1)
        df['gap'] = (df['Open'] - df['prev_close']) / df['prev_close']
        
        # Long Signal wenn Gap kleiner als Schwellwert
        df['signal'] = df['gap'] < self.gap_threshold
        
        return df

    def backtest(self, df: pd.DataFrame) -> dict:
        """
        Führt einen einfachen Backtest durch.
        Wird nicht mehr benötigt da wir BacktestEngine nutzen.
        """
        signals = self.generate_signals(df)
        trades = signals[signals["signal"]]
        return {"total_trades": len(trades)}