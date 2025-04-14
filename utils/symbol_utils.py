import pandas as pd
import logging
import norgatedata

# Define a function to retrieve all symbols from the US Equities and US Equities Delisted databases
def get_all_market_symbols():
    logging.info("Retrieving all symbols from US Equities and US Equities Delisted...")
    
    try:
        us_equities = norgatedata.database_symbols('US Equities')
        us_delisted = norgatedata.database_symbols('US Equities Delisted')

        logging.info(f"Retrieved {len(us_equities)} active symbols and {len (us_delisted)} delisted symbols.")
        return us_equities, us_delisted
    except Exception as e:
        logging.error(f"Error retrieving symbols: {e}")
        return [], []

active_symbols, delisted_symbols = get_all_market_symbols()

print("Active symbols:", active_symbols[:5])
print("Delisted symbols:", delisted_symbols[:5])

# Define a function to add Company Names to the Downloaded Data
def add_security_name(symbol, data):
    security_name = norgatedata.security_name(symbol)
    data['Security_Name'] = security_name
    logging.info(f"Added security name for {symbol}: {security_name}")
    return data

# Define a function to add sector information to the DataFrame
def add_sector_info(symbol, data):
    sector = norgatedata.classification_at_level(symbol, 'GICS', 'Name', level=1)
    data['Sector'] = sector
    logging.info(f"Added sector information for {symbol}: {sector}")
    return data