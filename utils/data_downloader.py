import logging
import pandas as pd
import norgatedata

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
    """Lädt Daten für mehrere Symbole."""
    all_data = []
    
    for symbol in symbols:
        data = download_stock_data(symbol, start_date, end_date)
        if data is not None:
            all_data.append(data)
    
    if not all_data:
        return pd.DataFrame()
        
    return pd.concat(all_data, ignore_index=False)