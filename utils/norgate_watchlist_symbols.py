import norgatedata
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
    
# Gets all symbols from a specific watchlist
# Example: Get all symbols from the S&P 500 watchlist
def get_watchlist_symbols(watchlist_name: str, quiet: bool = False) -> list:
    """
    Holt Symbole aus verschiedenen Norgate Watchlisten mit Fehlerbehandlung.
    
    Args:
        watchlist_name: Name der jeweiligen Norgate Watchliste
        quiet: Wenn True, werden keine print-Ausgaben gemacht (default: False)
        
    Returns:
        Liste der Symbole oder leere Liste bei Fehler
    """
    try:
        # Prüfen ob Norgate Data Utility läuft
        if not norgatedata.status():
            raise ConnectionError("Norgate Data Utility ist nicht aktiv")
        
        # Get all active watchlists from norgatedata
        all_watchlists = norgatedata.watchlists()
        watchlist = None
        for w in all_watchlists:
            if w['name'] == watchlist_name:
                watchlist = w
                if not quiet:
                    print(f"Found watchlist: {watchlist['name']}")
                break
        if watchlist is None:
            logging.error(f"Watchlist: {watchlist_name} not found!")
            return []  # Statt exit() eine leere Liste zurückgeben
        
        # Symbole abrufen
        symbols = norgatedata.watchlist_symbols(watchlist_name)
        logging.info(f"Erfolgreich {len(symbols)} Symbole aus {watchlist_name} geladen")
        return symbols
        
    except ConnectionError as e:
        # Verbindungsfehler zur Norgate Data Utility
        logging.error(f"Verbindungsfehler: {str(e)}")
        return []
        
    except Exception as e:
        # Unerwartete Fehler
        logging.error(f"Unerwarteter Fehler: {str(e)}")
        return []