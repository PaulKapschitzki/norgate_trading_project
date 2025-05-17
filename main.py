# main.py
import os
import sys

# Setup und Python-Pfad konfigurieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from config.config import Config
from utils.data_manager import EnhancedMarketDataManager
from strategies.mean_reversion import MeanReversionStrategy
from screeners.ema_touch import EmaTouchScreener
from screeners.run_screener import run_daily_screening

def main():
    # Setup
    Config.setup()
    
    # Daten laden
    try:
        # EnhancedMarketDataManager initialisieren
        mdm = EnhancedMarketDataManager()
        # Daten laden (verwendet Cache wenn vorhanden, lädt sonst neu)
        merged_data = mdm.load_market_data()
        logging.info("Daten erfolgreich geladen und verarbeitet")
    except Exception as e:
        logging.error(f"Fehler beim Laden der Daten: {e}")
        return
    
    # Führe Screening durch und wende Strategie an
    try:
        screening_results = run_daily_screening()
        logging.info(f"Screening gefunden: {len(screening_results)} Aktien")
        
        # Strategie testen
        strategy = MeanReversionStrategy()
        signals = strategy.generate_signals(screening_results)
        
        # Ergebnisse speichern
        output_path = Config.get_project_path('data', 'processed', 'screener_results.parquet')
        signals.to_parquet(output_path)
        logging.info(f"Ergebnisse gespeichert in {output_path}")
        
    except Exception as e:
        logging.error(f"Fehler beim Screening oder der Strategie-Anwendung: {e}")
        return

if __name__ == "__main__":
    main()
