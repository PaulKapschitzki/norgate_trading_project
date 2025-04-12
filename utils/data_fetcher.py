import pandas as pd
import logging
import norgatedata

# Step 1
# Set up logging to display log messages in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Step 2
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

# aapl_data = download_stock_data('AAPL', start_date, end_date)
# tsla_data = download_stock_data('TSLA', start_date, end_date)
# goog_data = download_stock_data('GOOG', start_date, end_date)

# aapl_data.head()

# Step 3
# Define a function to add Company Names to the Downloaded Data
def add_security_name(symbol, data):
    security_name = norgatedata.security_name(symbol)
    data['Security_Name'] = security_name
    logging.info(f"Added security name for {symbol}: {security_name}")
    return data

# aapl_data = add_security_name('AAPL', aapl_data)
# tsla_data = add_security_name('TSLA', tsla_data)
# goog_data = add_security_name('GOOG', goog_data)

# aapl_data.head()

# Step 4
# Define a function to add sector information to the DataFrame
def add_sector_info(symbol, data):
    sector = norgatedata.classification_at_level(symbol, 'GICS', 'Name', level=1)
    data['Sector'] = sector
    logging.info(f"Added sector information for {symbol}: {sector}")
    return data

# aapl_data = add_sector_info('AAPL', aapl_data)
# tsla_data = add_sector_info('TSLA', tsla_data)
# goog_data = add_sector_info('GOOG', goog_data)

# aapl_data.head()

# Step 5
# Define a function to check if a symbol was part of specific indices
# def check_index_constituency(symbol, data):
#     indices_to_check = ['S&P 500', 'Russell 3000']
    
#     for indexname in indices_to_check:
#         logging.info(f"Checking if {symbol} was part of {indexname}...")

#         # Fetch the index membership timeseries directly using the data DataFrame
#         index_data = norgatedata.index_constituent_timeseries(
#             symbol,
#             indexname,
#             padding_setting=norgatedata.PaddingType.NONE,
#             pandas_dataframe=data.copy(),  # Pass in a copy of the existing DataFrame
#             timeseriesformat='pandas-dataframe'
#         )
        
        
#         column_name = f'In_{indexname.replace(" ", "_")}'
        
#         if column_name in data.columns:
#             logging.info(f"Column {column_name} already exists. Skipping...")
#             continue 

#         if 'Index Constituent' in index_data.columns:
#             # Rename the 'Index Constituent' column to reflect index membership
#             index_data.rename(columns={'Index Constituent': column_name}, inplace=True)
            
#             # Assign the renamed column back to the original data DataFrame
#             data[column_name] = index_data[column_name]
#         else:
#             logging.warning(f"'Index Constituent' column not found for {symbol} in {indexname}")
    
#     return data

# aapl_data = check_index_constituency('AAPL', aapl_data)
# tsla_data = check_index_constituency('TSLA', tsla_data)
# goog_data = check_index_constituency('GOOG', goog_data)

# aapl_data.head(5)

# Step 6
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

# Step 7
# Define a function to filter out non-stock symbols
def filter_stocks(symbols):
    stock_symbols = [symbol for symbol in symbols if norgatedata.subtype1(symbol) == 'Equity']
    logging.info(f"Filtered {len(stock_symbols)} stocks from {len(symbols)} total symbols.")
    return stock_symbols

active_stocks = filter_stocks(active_symbols)
delisted_stocks = filter_stocks(delisted_symbols)

print(f"Active stocks: {len(active_stocks)}, Delisted stocks: {len(delisted_stocks)}")

# Step 8
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

# Download all active and delisted stock data
logging.info("Downloading active stock data...")
all_active_data = download_all_stock_data(active_stocks, start_date, end_date)

logging.info("Downloading delisted stock data...")
all_delisted_data = download_all_stock_data(delisted_stocks, start_date, end_date)

# Display the number of active and delisted stocks
if not all_active_data.empty:
    print(f"Downloaded data for {len(all_active_data['Symbol'].unique())} active stocks.")
else:
    print("No active stock data downloaded.")

if not all_delisted_data.empty:
    print(f"Downloaded data for {len(all_delisted_data['Symbol'].unique())} delisted stocks.")
else:
    print("No delisted stock data downloaded.")
    
# Step 9
# Define a function to add Security Names to the Data
def add_security_name(data):
    if 'Symbol' not in data.columns:
        logging.error("The 'Symbol' column is missing in the DataFrame.")
        return data  # Gib den unveränderten DataFrame zurück
    
    unique_symbols = data['Symbol'].unique()    
    security_names = {}
    
    for symbol in unique_symbols:
        logging.info(f"Fetching security name for {symbol}...")        
        security_name = norgatedata.security_name(symbol)        
        security_names[symbol] = security_name
    
    data['Security_Name'] = data['Symbol'].map(security_names)
    
    return data

if all_active_data.empty:
    logging.warning("all_active_data is empty. Skipping add_security_name.")
else:
    print("all_active_data columns:", all_active_data.columns)
    print("all_active_data head:", all_active_data.head())
    all_active_data = add_security_name(all_active_data)
    all_delisted_data = add_security_name(all_delisted_data)

all_active_data.head()

# Step 10
# Define a function to add Sector Information to the Data
# def add_sector_info(data):
#     unique_symbols = data['Symbol'].unique() 
    
#     sectors = {}
    
#     for symbol in unique_symbols:
#         logging.info(f"Fetching sector information for {symbol}...")
        
#         sector = norgatedata.classification_at_level(symbol, 'GICS', 'Name', level=1)
        
#         sectors[symbol] = sector
    
#     data['Sector'] = data['Symbol'].map(sectors)
    
#     return data

# all_active_data = add_sector_info(all_active_data)
# all_delisted_data = add_sector_info(all_delisted_data)

# all_active_data.head()

# Step 11
# Define a function to check Index Constituency for Active and Delisted Stocks
def check_index_constituency(symbol, data):
    indices_to_check = ['S&P 500', 'Russell 3000']
    
    for indexname in indices_to_check:
        logging.info(f"Checking if {symbol} was part of {indexname}...")

        try:
            index_data = norgatedata.index_constituent_timeseries(
                symbol,
                indexname,
                pandas_dataframe=data.copy(),  # Pass in a copy of the existing DataFrame
                padding_setting=norgatedata.PaddingType.NONE,
                timeseriesformat='pandas-dataframe'
            )
        except Exception as e:
            logging.error(f"Error fetching index data for {symbol} in {indexname}: {e}")
            index_data = data.copy()
            index_data['Index Constituent'] = 0
        
        column_name = f"In_{indexname.replace(' ', '_')}"
        
        if column_name in data.columns:
            logging.info(f"Column {column_name} already exists for {symbol}. Skipping...")
            continue 

        if 'Index Constituent' in index_data.columns:
            index_data.rename(columns={'Index Constituent': column_name}, inplace=True)
            
            data[column_name] = index_data[column_name]
        else:
            logging.warning(f"'Index Constituent' column not found for {symbol} in {indexname}")
            data[column_name] = 0 
    
    return data

if all_active_data.empty:
    logging.warning("all_active_data is empty. Skipping check_index_constituency.")
else:
    active_symbols = all_active_data['Symbol'].unique()
    delisted_symbols = all_delisted_data['Symbol'].unique()

logging.info("Checking index constituency for active stocks...")
processed_active_data = []

for symbol in active_symbols:
    symbol_data = all_active_data[all_active_data['Symbol'] == symbol].copy()
    symbol_data = check_index_constituency(symbol, symbol_data)
    processed_active_data.append(symbol_data)

all_active_data = pd.concat(processed_active_data)

logging.info("Checking index constituency for delisted stocks...")
processed_delisted_data = []

for symbol in delisted_symbols:
    symbol_data = all_delisted_data[all_delisted_data['Symbol'] == symbol].copy()
    symbol_data = check_index_constituency(symbol, symbol_data)
    processed_delisted_data.append(symbol_data)

all_delisted_data = pd.concat(processed_delisted_data)

all_active_data.tail(5)

# Step 12
# Define a function to Merge Active and Delisted Stocks into One Dataset
merged_data = pd.concat([all_active_data, all_delisted_data])
merged_data.sort_index(inplace=True)

output_path = './Survivorship_bias_free_Database.parquet'
merged_data.to_parquet(output_path, engine='pyarrow')


logging.info(f"Merged data has been saved as {output_path}")