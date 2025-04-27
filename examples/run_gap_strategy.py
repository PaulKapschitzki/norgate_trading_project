import sys
import os
import logging

# Projektpfad zum Python Path hinzufügen
project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from strategies.mean_reversion import MeanReversionStrategy
from backtesting.performance import EnhancedBacktestPerformance

logging.basicConfig(level=logging.INFO)

def main():
    # Strategie initialisieren
    strategy = MeanReversionStrategy(gap_threshold=-0.03)
    
    # Backtester initialisieren
    bp = EnhancedBacktestPerformance()

    # Backtest mit individuellen Parametern ausführen
    results = bp.run_backtest(
        strategy=strategy,
        symbols=['AAPL', 'MSFT', 'GOOGL'],  # Optional: None für alle Symbole
        start_date='2023-01-01',            # Optional: Individuelles Startdatum
        end_date='2024-01-01'               # Optional: Individuelles Enddatum
        )

    # Ergebnisse ausgeben
    for result in results:
        print(f"\nErgebnisse für {result['Symbol']}:")
        print(f"Anzahl Trades: {result['Results']['total_trades']}")
        print(f"Durchschn. Return: {result['Results'].get('avg_return', 0):.2f}%")
        print(f"Win Rate: {result['Results'].get('win_rate', 0):.2f}")

if __name__ == "__main__":
    main()