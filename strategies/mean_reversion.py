# strategies/mean_reversion.py
class MeanReversionStrategy:
    def generate_signals(self, df):
        # Berechnung der Signale
        return df

    def backtest(self, df):
        # Logik des Backtests
        return {"total_trades": len(df)}

# Beispiel in strategies/mean_reversion.py
# Zum Testen der einzelnen Datei muss if __name__ == "__main__": vorhanden sein
if __name__ == "__main__":
    import pandas as pd
    # Erstelle ein Dummy-DataFrame
    df = pd.DataFrame({
        "close": [10, 12, 11, 13, 12],
        "date": pd.date_range("2025-01-01", periods=5)
    })
    strategy = MeanReversionStrategy()
    df = strategy.generate_signals(df)
    print(df)