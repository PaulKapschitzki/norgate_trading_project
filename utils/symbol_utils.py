import logging
import norgatedata
import pandas as pd

def filter_stocks(symbols: list) -> list:
    """Filtert Aktien aus der Symbol-Liste."""
    stock_symbols = [symbol for symbol in symbols if norgatedata.subtype1(symbol) == 'Equity']
    logging.info(f"Filtered {len(stock_symbols)} stocks from {len(symbols)} total symbols.")
    return stock_symbols

def add_security_name(data: pd.DataFrame) -> pd.DataFrame:
    """Fügt Sicherheitsnamen zum DataFrame hinzu."""
    if 'Symbol' not in data.columns:
        logging.error("The 'Symbol' column is missing in the DataFrame.")
        return data
        
    security_names = {}
    for symbol in data['Symbol'].unique():
        try:
            security_names[symbol] = norgatedata.security_name(symbol)
        except Exception as e:
            logging.error(f"Error getting security name for {symbol}: {e}")
            security_names[symbol] = None
            
    data['Security_Name'] = data['Symbol'].map(security_names)
    return data

def add_sector_info(data: pd.DataFrame) -> pd.DataFrame:
    """Fügt Sektor-Informationen zum DataFrame hinzu."""
    if 'Symbol' not in data.columns:
        logging.error("The 'Symbol' column is missing in the DataFrame.")
        return data
        
    sectors = {}
    for symbol in data['Symbol'].unique():
        try:
            sectors[symbol] = norgatedata.classification_at_level(symbol, 'GICS', 'Name', level=1)
        except Exception as e:
            logging.error(f"Error getting sector for {symbol}: {e}")
            sectors[symbol] = None
            
    data['Sector'] = data['Symbol'].map(sectors)
    return data