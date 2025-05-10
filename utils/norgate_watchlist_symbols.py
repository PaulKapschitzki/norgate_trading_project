import norgatedata
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
    
# Gets all symbols from a specific watchlist
# Example: Get all symbols from the S&P 500 watchlist
def get_watchlist_symbols(watchlist_name: str) -> list:
    """
    Holt Symbole aus verschiedenen Norgate Watchlisten mit Fehlerbehandlung.
    
    Args:
        watchlist_name: Name der jeweiligen Norgate Watchliste
        
    Returns:
        Liste der Symbole oder leere Liste bei Fehler
    """
    try:
        # Prüfen ob Norgate Data Utility läuft
        if not norgatedata.status():
            raise ConnectionError("Norgate Data Utility ist nicht aktiv")
          # Get all active watchlists from norgatedata
        all_watchlists = norgatedata.watchlists()
        
        # Suche nach der gewünschten Watchlist
        if watchlist_name not in all_watchlists:
            logging.error(f"Watchlist: {watchlist_name} nicht gefunden!")
            return []
            
        logging.info(f"Gefundene Watchlist: {watchlist_name}")
  
        
        # Symbole abrufen
        symbols = norgatedata.watchlist_symbols(watchlist_name)
        if not symbols:
            logging.error(f"Keine Symbole in der Watchlist {watchlist_name} gefunden")
            return []
            
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
    
def main():
    # Beispielaufruf der Funktion
    watchlist_name = "S&P 500"
    symbols = get_watchlist_symbols(watchlist_name)
    
    if symbols:
        print(f"Symbole in {watchlist_name}: {symbols}")
    else:
        print(f"Keine Symbole gefunden oder Fehler aufgetreten.")

if __name__ == "__main__":
    main()