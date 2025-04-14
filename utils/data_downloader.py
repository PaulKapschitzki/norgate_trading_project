import logging
import pandas as pd
import norgatedata

# Define a function to download stock data for a given symbol and date range
def download_stock_data(symbol, start_date, end_date):
    logging.info(f"Downloading data for {symbol} from {start_date} to {end_date}...")
    priceadjust = norgatedata.StockPriceAdjustmentType.TOTALRETURN
    padding_setting = norgatedata.PaddingType.NONE
    timeseriesformat = 'pandas-dataframe'
    
    try:
        # Versuche, die Preisdaten abzurufen
        pricedata = norgatedata.price_timeseries(
            symbol,
            stock_price_adjustment_setting=priceadjust,
            padding_setting=padding_setting,
            start_date=start_date,
            end_date=end_date,
            timeseriesformat=timeseriesformat
        )
        
        # Überprüfe, ob die Rückgabe None oder leer ist
        if pricedata is None or len(pricedata) == 0:
            logging.warning(f"No data returned for {symbol}.")
            return None
        
        return pricedata
    except Exception as e:
        # Protokolliere den Fehler und gib None zurück
        logging.error(f"Error downloading data for {symbol}: {e}")
        return None

# Define a function to download stock data for multiple symbols
def download_all_stock_data(symbols, start_date, end_date):

    all_data = []
    
    for symbol in symbols:
        logging.info(f"Downloading data for {symbol}...")
        data = download_stock_data(symbol, start_date, end_date)
        
        if data is not None:
            data['Symbol'] = symbol  # Add the symbol as a column
            all_data.append(data)
    
    # Combine all data into a single DataFrame (keeping Date as index by default)
    return pd.concat(all_data, ignore_index=False) if all_data else pd.DataFrame()