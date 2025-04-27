import pandas as pd
import logging
from typing import Dict, Any

class BacktestingEngine:
    """Core-Engine für Backtesting-Berechnungen"""
    
    def __init__(self):
        self.positions = {}
        self.cash = 10000  # Startkapital
        self.position_size = 0.1  # 10% pro Position
        
    def calculate_position_size(self, price: float) -> int:
        """Berechnet Positionsgröße basierend auf verfügbarem Kapital"""
        position_value = self.cash * self.position_size
        return int(position_value / price)
        
    def execute_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Führt Backtest-Berechnungen für einen einzelnen Datensatz durch.
        
        Args:
            df: DataFrame mit OHLCV und Signaldaten
            
        Returns:
            Dict mit Performancemetriken
        """
        try:
            returns = []
            trades = []
            
            for idx, row in df.iterrows():
                if row['signal'] and not self.positions.get(row['Symbol']):
                    # Entry
                    size = self.calculate_position_size(row['close'])
                    self.positions[row['Symbol']] = {
                        'size': size,
                        'entry_price': row['close'],
                        'entry_date': idx
                    }
                    trades.append({
                        'type': 'entry',
                        'date': idx,
                        'price': row['close'],
                        'size': size
                    })
                    
                elif not row['signal'] and self.positions.get(row['Symbol']):
                    # Exit
                    position = self.positions[row['Symbol']]
                    returns.append(
                        (row['close'] - position['entry_price']) / 
                        position['entry_price'] * 100
                    )
                    trades.append({
                        'type': 'exit',
                        'date': idx,
                        'price': row['close'],
                        'size': position['size']
                    })
                    del self.positions[row['Symbol']]
            
            return {
                'total_trades': len(trades) // 2,
                'avg_return': sum(returns) / len(returns) if returns else 0,
                'win_rate': len([r for r in returns if r > 0]) / len(returns) if returns else 0,
                'trades': trades
            }
            
        except Exception as e:
            logging.error(f"Fehler in execute_backtest: {str(e)}")
            return {}
