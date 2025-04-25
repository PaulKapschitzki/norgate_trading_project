import sys
import os
import logging

# Projektpfad zum Python Path hinzufügen
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from backtesting.performance import BacktestPerformance
from strategies.mean_reversion import MeanReversionStrategy

logging.basicConfig(level=logging.INFO)

def main():
    # Strategie und Backtester initialisieren
    strategy = MeanReversionStrategy(gap_threshold=-0.03)  # 3% Gap
    bp = BacktestPerformance()
    
    # Backtest für einige Test-Symbole durchführen
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    results = bp.run_backtest(strategy, symbols=test_symbols)
    
    # Ergebnisse ausgeben
    for result in results:
        print(f"\nErgebnisse für {result['Symbol']}:")
        print(f"Anzahl Trades: {result['Results']['total_trades']}")
        print(f"Durchschnittlicher Return: {result['Results']['avg_return']:.2f}%")
        print(f"Win Rate: {result['Results']['win_rate']:.2f}")

if __name__ == "__main__":
    main()