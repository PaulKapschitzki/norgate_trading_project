class MeanReversionStrategy:
    def generate_signals(self, df):
        df["ma20"] = df["close"].rolling(20).mean()
        # Signal: Einstieg, wenn Schlusskurs unter dem MA20 liegt
        df["signal"] = df["close"] < df["ma20"]
        return df

    def backtest(self, df):
        signals = self.generate_signals(df)
        trades = signals[signals["signal"]]
        # Berechne einfache Kennzahlen (hier nur Beispiel)
        return {"total_trades": len(trades)}

if __name__ == "__main__":
    # Testcode für diese Strategie
    import pandas as pd
    data = {
        "close": [100, 98, 97, 95, 96, 94, 93, 92, 95, 97],
        "date": pd.date_range("2025-01-01", periods=10)
    }
    df = pd.DataFrame(data)
    strat = MeanReversionStrategy()
    df = strat.generate_signals(df)
    print(df)