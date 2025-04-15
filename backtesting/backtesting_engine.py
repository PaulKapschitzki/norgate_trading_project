def run_backtest(strategy, data):
    # Hier werden die Strategie-Funktionen aufgerufen,
    # um Signale zu generieren und Backtesting durchzuführen.
    results = strategy.backtest(data)
    return results

if __name__ == "__main__":
    # Kurzer Test, falls nötig
    from strategies.mean_reversion import MeanReversionStrategy
    import pandas as pd

    data = pd.DataFrame({
        "close": [100, 98, 97, 95, 96, 94, 93, 92, 95, 97],
        "date": pd.date_range("2025-01-01", periods=10)
    })

    strat = MeanReversionStrategy()
    results = run_backtest(strat, data)
    print("Ergebnisse:", results)
