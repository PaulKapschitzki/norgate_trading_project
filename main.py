import norgatedata
import pandas as pd

# Verbindung zu NorgateData herstellen
norgatedata.connect()

# Beispiel: Daten für ein Symbol laden und in einem DataFrame speichern
data = norgatedata.price_timeseries('AAPL', fields=['date', 'open', 'high', 'low', 'close', 'volume'], frequency='daily')
df = pd.DataFrame(data)
print(df.head())

class BaseStrategy:
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Berechnet und fügt dem DataFrame Handelssignale hinzu."""
        raise NotImplementedError

    def backtest(self, df: pd.DataFrame) -> dict:
        """Führt den Backtest durch und gibt Metriken zurück."""
        raise NotImplementedError
