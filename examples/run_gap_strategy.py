import logging

from config.config import Config
from strategies.mean_reversion import MeanReversionStrategy
from backtesting.performance import EnhancedBacktestPerformance

# Logging Setup über Config
Config.setup()

def main():
    # Strategie initialisieren
    strategy = MeanReversionStrategy(gap_threshold=-0.03)
    
    # Backtester initialisieren
    bp = EnhancedBacktestPerformance()

    # Backtest mit individuellen Parametern ausführen
    results = bp.run_backtest(
        strategy=strategy,
        # symbols=['AAPL', 'MSFT', 'GOOGL'],  # Optional: None für alle Symbole
        # start_date='2023-01-01',            # Optional: Individuelles Startdatum
        # end_date='2024-01-01'               # Optional: Individuelles Enddatum
        )

    # Ergebnisse ausgeben
    for result in results:
        print(f"\nErgebnisse für {result['Symbol']}:")
        print(f"Anzahl Trades: {result['Results']['total_trades']}")
        print(f"Durchschn. Return: {result['Results'].get('avg_return', 0):.2f}%")
        print(f"Win Rate: {result['Results'].get('win_rate', 0):.2f}")

if __name__ == "__main__":
    main()