# norgate_trading_project
Backtesting, Screening + Webapp of my trading strategies 

# TODO's
## data_fetcher.py Script modularisieren
Aktuell werden alle Funktionen (def) in data_fetcher.py beim Aufruf ausgeführt, obwohl ich nur die Daten für ein Symbol via download_stock_data haben will

Aufsplitten in u. a.
- symbol_utils.py für bpsw. get_all_market_symbols und filter_stocks
- data_downloader.py für bspw. download_stock_data und download_all_stock_data
- ???
## Globale Variablen vermeiden
In deinem aktuellen data_fetcher.py-Code werden globale Variablen wie active_symbols und delisted_symbols direkt definiert. Diese sollten in Funktionen gekapselt werden, um ungewollte Seiteneffekte zu vermeiden.

Beispiel:
def get_active_and_delisted_symbols():
    active_symbols, delisted_symbols = get_all_market_symbols()
    return active_symbols, delisted_symbols

In main.py kannst du dann gezielt diese Funktion aufrufen, falls benötigt.