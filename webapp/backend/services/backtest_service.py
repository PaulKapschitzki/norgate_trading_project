import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import importlib

from sqlalchemy.orm import Session

from backtesting.performance import EnhancedBacktestPerformance
from utils.data_manager import EnhancedMarketDataManager

# Logger konfigurieren
logger = logging.getLogger(__name__)

def run_backtest(
    watchlist_name: str,
    strategy_type: str,
    parameters: Dict[str, Any],
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Führt einen Backtest mit den angegebenen Parametern aus.
    
    Args:
        watchlist_name: Name der zu verwendenden Watchlist
        strategy_type: Art der Strategie (z.B. 'mean_reversion')
        parameters: Parameter für die Strategie
        start_date: Startdatum für den Backtest
        end_date: Enddatum für den Backtest
        
    Returns:
        Dictionary mit Backtest-Ergebnissen
    """
    try:
        # Strategie-Modul dynamisch laden
        module_path = f"strategies.{strategy_type}"
        try:
            strategy_module = importlib.import_module(module_path)
            # Get the appropriate strategy class (assuming it follows naming convention)
            strategy_class_name = ''.join(word.capitalize() for word in strategy_type.split('_')) + "Strategy"
            strategy_class = getattr(strategy_module, strategy_class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Fehler beim Laden des Strategie-Moduls: {str(e)}")
            return {
                "status": "error",
                "message": f"Strategie {strategy_type} nicht gefunden."
            }
        
        # Daten-Manager initialisieren
        data_manager = EnhancedMarketDataManager(watchlist_name=watchlist_name)
        
        # Symbole aus der Watchlist holen
        from utils.norgate_watchlist_symbols import get_watchlist_symbols
        symbols = get_watchlist_symbols(watchlist_name)
        
        # Strategie initialisieren
        strategy = strategy_class(**parameters)
        
        # Backtest-Engine initialisieren
        backtest_performance = EnhancedBacktestPerformance()
        
        # Backtest durchführen
        results = backtest_performance.run_backtest(
            strategy=strategy,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        # Gesamtperformance berechnen
        total_trades = sum(r['Results']['total_trades'] for r in results)
        total_win_trades = sum(r['Results']['win_trades'] if 'win_trades' in r['Results'] else 0 for r in results)
        avg_return = sum(r['Results']['avg_return'] * r['Results']['total_trades'] for r in results) / total_trades if total_trades > 0 else 0
        
        summary = {
            "total_symbols": len(results),
            "total_trades": total_trades,
            "win_rate": total_win_trades / total_trades if total_trades > 0 else 0,
            "avg_return": avg_return
        }
        
        return {
            "status": "success",
            "summary": summary,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Backtests: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Fehler beim Ausführen des Backtests: {str(e)}"
        }

def get_available_strategies() -> List[Dict[str, Any]]:
    """
    Gibt eine Liste der verfügbaren Backtest-Strategien zurück.
    
    Returns:
        Liste der Strategien mit Namen und Beschreibungen
    """
    try:
        # Diese Liste sollte erweitert werden, wenn neue Strategien hinzugefügt werden
        strategies = [
            {
                "id": "mean_reversion",
                "name": "Mean Reversion",
                "description": "Strategie, die Umkehrungen nach starken Kursbewegungen identifiziert",
                "parameters": [
                    {
                        "name": "gap_threshold",
                        "type": "float",
                        "default": -0.03,
                        "description": "Schwellenwert für Kurslücke nach unten (z.B. -0.03 für -3%)"
                    },
                    {
                        "name": "exit_days",
                        "type": "int",
                        "default": 5,
                        "description": "Anzahl der Tage bis zum Ausstieg"
                    }
                ]
            }
            # Hier können weitere Strategien hinzugefügt werden
        ]
        
        return strategies
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der verfügbaren Strategien: {str(e)}", exc_info=True)
        return []