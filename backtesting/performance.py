from utils.data_manager import EnhancedMarketDataManager
from .backtesting_engine import BacktestingEngine
import logging
from typing import List, Dict, Any, Optional

class EnhancedBacktestPerformance:
    """Erweiterte High-Level Interface für Backtesting mit individuellen Parametern"""
    
    def __init__(self):
        self.mdm = EnhancedMarketDataManager()
        self.engine = BacktestingEngine()
        
    def run_backtest(self, strategy, symbols=None, start_date=None, end_date=None) -> List[Dict[str, Any]]:
        """
        Führt Backtest für eine Strategie mit individuellen Parametern durch.
        
        Args:
            strategy: Strategie-Instanz
            symbols: Liste von Symbolen oder None für alle
            start_date: Optional, Startdatum im Format 'YYYY-MM-DD'
            end_date: Optional, Enddatum im Format 'YYYY-MM-DD'
        """
        # Lade Daten mit individuellen Parametern
        df = self.mdm.load_market_data(start_date=start_date, end_date=end_date, symbols=symbols)
        
        results = []
        total_symbols = len(df['Symbol'].unique())
        logging.info(f"Starte Backtest für {total_symbols} Symbole...")
        
        for i, symbol in enumerate(df['Symbol'].unique(), 1):
            logging.info(f"Backtest für {symbol} ({i}/{total_symbols})")
            
            # Daten für Symbol vorbereiten
            symbol_data = df[df['Symbol'] == symbol].copy()
            
            # Signale generieren
            symbol_data = strategy.generate_signals(symbol_data)
            
            # Backtest durchführen
            result = self.engine.execute_backtest(symbol_data)
            
            results.append({
                'Symbol': symbol,
                'Results': result
            })
            
        return results

# class BacktestPerformance:
#     """High-Level Interface für Backtesting und Performance-Analyse"""
    
#     def __init__(self):
#         self.mdm = MarketDataManager()
#         self.engine = BacktestingEngine()
        
#     def run_backtest(self, strategy, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
#         """
#         Führt Backtest für eine Strategie durch.
        
#         Args:
#             strategy: Strategie-Instanz
#             symbols: Liste von Symbolen oder None für alle
#         """
#         df = self.mdm.load_market_data()
        
#         if symbols:
#             df = df[df['Symbol'].isin(symbols)]
            
#         results = []
#         for symbol in df['Symbol'].unique():
#             # Daten für Symbol vorbereiten
#             symbol_data = df[df['Symbol'] == symbol].copy()
            
#             # Signale generieren
#             symbol_data = strategy.generate_signals(symbol_data)
            
#             # Backtest durchführen
#             result = self.engine.execute_backtest(symbol_data)
            
#             results.append({
#                 'Symbol': symbol,
#                 'Results': result
#             })
            
#         return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from strategies.mean_reversion import MeanReversionStrategy
    
    bp = EnhancedMarketDataManager()
    strategy = MeanReversionStrategy()
    
    # Test mit wenigen Symbolen
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    # results = bp.run_backtest(strategy, symbols=test_symbols) # Mit optionaler Symbol-Liste
    results = bp.run_backtest(strategy) # Alle Symbole
    
    for result in results:
        print(f"\nErgebnisse für {result['Symbol']}:")
        print(result['Results'])