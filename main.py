# main.py
import os
import sys
import logging
from config.config import Config
from utils.data_fetcher import fetch_and_process_data
from strategies.mean_reversion import MeanReversionStrategy
from screeners.ema_touch import EmaTouchScreener

# Arbeitsverzeichnis auf das Projekt-Stammverzeichnis setzen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

def setup_logging():
    logging.basicConfig(
        level=Config.LOG_LEVEL,
        format=Config.LOG_FORMAT
    )

def main():
    # Setup
    setup_logging()
    Config.setup()
    
    # Daten laden
    try:
        merged_data = fetch_and_process_data()
        logging.info("Daten erfolgreich geladen und verarbeitet")
    except Exception as e:
        logging.error(f"Fehler beim Laden der Daten: {e}")
        return
    
    # Führe Screening durch
    try:
        screening_results = run_daily_screening()
        logging.info(f"Screening gefunden: {len(screening_results)} Aktien")
        
        # Hier kannst du weitere Verarbeitung hinzufügen
        # z.B. Strategie-Tests oder WebApp-Updates
        
    except Exception as e:
        logging.error(f"Fehler beim Screening: {e}")
    
    # Strategie testen
    strategy = MeanReversionStrategy()
    signals = strategy.generate_signals(screening_results)
    
    # Ergebnisse speichern
    output_path = Config.get_output_path('screener_results.parquet')
    signals.to_parquet(output_path)
    logging.info(f"Ergebnisse gespeichert in {output_path}")

if __name__ == "__main__":
    main()
