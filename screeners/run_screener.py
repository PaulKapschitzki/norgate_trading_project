import logging
from datetime import datetime
from config.config import Config
from screeners.ema_touch import EmaTouchScreener
from utils.data_downloader import download_stock_data

def run_daily_screening():
    """Führt das tägliche Screening durch"""
    Config.setup()
    
    screener = EmaTouchScreener(
        ema_period=20,
        min_price=5.0,
        min_volume=100000
    )
    
    # Lade aktuelle Marktdaten
    today = datetime.now().strftime("%Y-%m-%d")
    market_data = download_stock_data(
        start_date="2023-01-01",  # Diese Daten sollten vom Frontend kommen
        end_date=today
    )
    
    # Führe Screening durch
    results = screener.screen(market_data)
    
    # Speichere Ergebnisse
    output_path = Config.get_project_path('data', 'processed', f'screener_results_{today}.parquet')
    results.to_parquet(output_path)
    logging.info(f"Screening Ergebnisse gespeichert in: {output_path}")
    
    return results