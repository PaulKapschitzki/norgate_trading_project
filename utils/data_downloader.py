import logging
import pandas as pd
import norgatedata
from webapp.backend.services.screener_process import ScreenerProcess

def download_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Lädt Daten für ein einzelnes Symbol."""
    logging.info(f"Downloading data for {symbol} from {start_date} to {end_date}...")
    
    try:
        pricedata = norgatedata.price_timeseries(
            symbol,
            stock_price_adjustment_setting=norgatedata.StockPriceAdjustmentType.TOTALRETURN,
            padding_setting=norgatedata.PaddingType.NONE,
            start_date=start_date,
            end_date=end_date,
            timeseriesformat='pandas-dataframe'
        )
        
        if pricedata is None or len(pricedata) == 0:
            logging.warning(f"No data returned for {symbol}.")
            return None
            
        # Füge Symbol als Spalte hinzu
        pricedata['Symbol'] = symbol
        return pricedata
        
    except Exception as e:
        logging.error(f"Error downloading data for {symbol}: {e}")
        return None

def download_all_stock_data(symbols: list, start_date: str, end_date: str) -> pd.DataFrame:
    """Lädt Daten für mehrere Symbole.
    
    Args:
        symbols: Liste der zu ladenden Symbole
        start_date: Startdatum im Format 'YYYY-MM-DD'
        end_date: Enddatum im Format 'YYYY-MM-DD'
    
    Returns:
        DataFrame mit den kombinierten Daten aller Symbole
    
    Raises:
        ValueError: Wenn keine Symbole angegeben sind
        RuntimeError: Wenn der Download komplett fehlschlägt
    """
    if not symbols:
        raise ValueError("Keine Symbole zum Download angegeben")

    all_data = []
    total_symbols = len(symbols)
    process_manager = ScreenerProcess()
    successful_downloads = 0
    failed_downloads = 0

    # Setze initialen Status
    process_manager.status = "downloading"
    process_manager.update_progress(total_symbols, 0, None)
    
    try:
        for i, symbol in enumerate(symbols, 1):
            if process_manager.stop_requested:
                logging.info("Download-Prozess wurde gestoppt")
                break

            # Update progress
            process_manager.update_progress(total_symbols, i - 1, symbol)
            
            try:
                data = download_stock_data(symbol, start_date, end_date)
                if data is not None and not data.empty:
                    all_data.append(data)
                    successful_downloads += 1
                else:
                    failed_downloads += 1
            except Exception as e:
                logging.error(f"Fehler beim Download von {symbol}: {e}")
                failed_downloads += 1
                continue
                
            # Log progress
            if i % 10 == 0 or i == total_symbols:  # Log alle 10 Symbole oder am Ende
                logging.info(f"Fortschritt: {i}/{total_symbols} ({i/total_symbols*100:.1f}%)")
                logging.info(f"Erfolgreich: {successful_downloads}, Fehlgeschlagen: {failed_downloads}")
        
        if not all_data:
            raise RuntimeError("Keine Daten heruntergeladen")
            
        combined_data = pd.concat(all_data, ignore_index=False)
        logging.info(f"Download abgeschlossen. {len(combined_data)} Zeilen für {successful_downloads} Symbole")
        process_manager.status = "completed"
        return combined_data
        
    except Exception as e:
        process_manager.status = "error"
        raise RuntimeError(f"Fehler beim Download der Daten: {e}")
    
    finally:
        # Log final statistics
        total_processed = successful_downloads + failed_downloads
        if total_processed > 0:
            success_rate = (successful_downloads / total_processed) * 100
            logging.info(f"Download-Statistik: {success_rate:.1f}% erfolgreich " 
                        f"({successful_downloads} von {total_processed} Symbolen)")