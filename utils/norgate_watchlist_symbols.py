import norgatedata
import pandas as pd
import logging

norgatedata.status() #shows whether NDU is running (returns True if running, or False if not)

if norgatedata.status() == False: #check if NDU is running
    # print("Norgate Data Utility is not running. Please start it before running this script.")
    # Set up logging
    logging.basicConfig(level=logging.ERROR)  # Configure logging level
    logging.error("Norgate Data Utility is not running. Please start it before running this script.")  # Log the status
    exit()
else:
    # Set up logging
    logging.basicConfig(level=logging.INFO)  # Configure logging level
    logging.info("Norgate Data Utility is running.")  # Log the status

# Get all active watchlists from norgatedata
all_watchlists = norgatedata.watchlists()
print("All available watchlists:")
for watchlist in all_watchlists:
    if watchlist == 'S&P 500':
        print("Found S&P 500 watchlist")
    if watchlist == 'Russell 3000':
        print("Found Russell 3000 watchlist")
    if watchlist == 'NASDAQ 100':
        print("Found NASDAQ 100 watchlist")
    if watchlist == '@FullPrimaryListingEquityWL':
        print("Found @FullPrimaryListingEquityWL watchlist")

watchlistname = '@FullPrimaryListingEquityWL'
symbols = norgatedata.watchlist_symbols(watchlistname)

counter = 0
for symbol in symbols:
    if norgatedata.subtype1(symbol) == 'Equity':
        counter += 1
print(f"Number of active stocks in watchlist {watchlistname}: {counter}")

# for symbol in symbols:
#     print("Active symbol in watchlist: %s" % symbol)
    # Hier können Sie weitere Informationen zu den Symbolen abrufen, z.B.: