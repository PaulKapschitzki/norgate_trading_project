import os
import sys

# Projektpfad zum Python Path hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
import logging
import norgatedata
from utils.norgate_database_symbols import get_database_symbols
from utils.norgate_watchlist_symbols import get_watchlist_symbols
from typing import Optional, List, Tuple

# Step 1
# Set up logging to display log messages in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Step 2
# Define the function to fetch OHLCV data for a single symbol
def fetch_ohlcv_data(symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    Lädt OHLCV Daten für ein einzelnes Symbol.
    
    Args:
        symbol: Aktien-Symbol
        start_date: Startdatum (YYYY-MM-DD)
        end_date: Enddatum (YYYY-MM-DD)
    
    Returns:
        DataFrame mit OHLCV Daten oder None bei Fehler
    """
    try:
        logging.info(f"Lade OHLCV Daten für {symbol}...")
        
        df = norgatedata.price_timeseries(
            symbol,
            start_date=start_date,
            end_date=end_date,
            stock_price_adjustment_setting=norgatedata.StockPriceAdjustmentType.TOTALRETURN,
            padding_setting=norgatedata.PaddingType.NONE,
            timeseriesformat='pandas-dataframe'
        )
        
        if df is None or df.empty:
            logging.warning(f"Keine Daten für {symbol} gefunden")
            return None
            
        # Symbol als Spalte hinzufügen
        df['Symbol'] = symbol
        
        return df
        
    except Exception as e:
        logging.error(f"Fehler beim Laden der Daten für {symbol}: {str(e)}")
        return None

# Step 3
# Define the function to fetch OHLCV data for all symbols
def fetch_all_ohlcv_data(start_date: str, end_date: str, 
                        save_path: str) -> None:
    """
    Lädt OHLCV Daten für alle Aktien (aktiv und delistet).
    
    Args:
        start_date: Startdatum (YYYY-MM-DD)
        end_date: Enddatum (YYYY-MM-DD) 
        save_path: Speicherpfad für die Parquet-Datei
    """
    # Aktive Symbole laden
    active_symbols = get_database_symbols('US Equities')
    # active_details = get_symbol_details(active_symbols)
    
    # Delistete Symbole laden  
    delisted_symbols = get_database_symbols('US Equities Delisted')
    # delisted_details = get_symbol_details(delisted_symbols)
    
    # Alle Details kombinieren
    # all_details = active_details + delisted_details
    all_symbols = active_symbols + delisted_symbols
    
    # DataFrame für alle Daten
    all_data = []
    
    # Fortschrittsanzeige
    total = len(all_symbols)
    for i, (symbol) in enumerate(all_symbols, 1):
    # for i, (symbol, name) in enumerate(all_symbols, 1):
        logging.info(f"Fortschritt: {i}/{total} ({i/total*100:.1f}%)")
        
        df = fetch_ohlcv_data(symbol, start_date, end_date)
        if df is not None:
            # Firmenname hinzufügen
            # df['Company_Name'] = name
            all_data.append(df)
    
    if not all_data:
        logging.error("Keine Daten geladen!")
        return
        
    # Alle Daten zusammenführen
    final_df = pd.concat(all_data, ignore_index=False)
    
    print(f"Inside fetch_all_ohlcv_data, save_path is: {save_path}")
    # Daten speichern
    try:
        final_df.to_parquet(save_path)
        logging.info(f"Daten erfolgreich gespeichert unter: {save_path}")
        logging.info(f"Datensatz enthält {len(final_df)} Zeilen für {len(all_symbols)} Aktien")
        # logging.info(f"Datensatz enthält {len(final_df)} Zeilen für {len(all_details)} Aktien")
    except Exception as e:
        logging.error(f"Fehler beim Speichern der Daten: {str(e)}")

# Gets all symbols from a specific watchlist
# Example: Get all symbols from the S&P 500 watchlist
def fetch_all_ohlcv_data_from_list(watchlist_name: str, start_date: str, end_date: str, save_path: str) -> None:
    """
    Lädt OHLCV Daten für alle aktiven Aktien einer Watchliste.
    
    Args:
        watchlist_name: Name der Watchliste
        start_date: Startdatum (YYYY-MM-DD)
        end_date: Enddatum (YYYY-MM-DD) 
        save_path: Speicherpfad für die Parquet-Datei
    """
    # Symbole laden
    symbols = get_watchlist_symbols(watchlist_name)
    if not symbols:
        logging.error("Keine Symbole geladen!")
        return

    # DataFrame für alle Daten
    all_data = []
    
    # Fortschrittsanzeige
    for i, symbol in enumerate(symbols, 1):
        logging.info(f"Fortschritt: {i}/{len(symbols)} ({i/len(symbols)*100:.1f}%)")
        
        df = fetch_ohlcv_data(symbol, start_date, end_date)
        if df is not None:
            all_data.append(df)
    
    if not all_data:
        logging.error("Keine Daten geladen!")
        return
        
    # Alle Daten zusammenführen
    final_df = pd.concat(all_data, ignore_index=False)
    
    # Daten speichern
    try:
        if not save_path:
            save_path = f"data/raw/{watchlist_name.replace(' ', '_').lower()}_data.parquet"
            
        final_df.to_parquet(save_path)
        logging.info(f"Daten erfolgreich gespeichert unter: {save_path}")
        logging.info(f"Datensatz enthält {len(final_df)} Zeilen für {len(symbols)} Aktien")
    except Exception as e:
        logging.error(f"Fehler beim Speichern der Daten: {str(e)}")


# Hauptfunktion zum Testen
if __name__ == "__main__":
    # Logging konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Zeitraum definieren
    start_date = "2020-05-01"  # Anpassen nach Bedarf
    end_date = "2025-05-01"    # Anpassen nach Bedarf
    
    # Daten laden
    # fetch_all_ohlcv_data(start_date, end_date) # All active and delisted symbols from database
    fetch_all_ohlcv_data_from_list(
        "S&P 500", 
        start_date, 
        end_date, 
        "data/raw/sp500_data.parquet"
    ) # All active symbols from specific watchlist