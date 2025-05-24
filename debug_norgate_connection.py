import norgatedata
import logging
import sys

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_norgate_connection():
    """Testet die Verbindung zur Norgate Data Utility"""
    logger.info("Teste Verbindung zur Norgate Data Utility...")
    
    # 1. Status prüfen
    try:
        status = norgatedata.status()
        logger.info(f"Norgate Data Status: {'Aktiv' if status else 'Inaktiv'}")
    except Exception as e:
        logger.error(f"Fehler beim Prüfen des Status: {str(e)}")
        return False
        
    if not status:
        logger.error("Norgate Data Utility ist nicht aktiv")
        return False
    
    # 2. Watchlists abrufen
    try:
        watchlists = norgatedata.watchlists()
        if not watchlists:
            logger.warning("Keine Watchlists gefunden")
            return False
            
        logger.info(f"Gefundene Watchlists ({len(watchlists)}):")
        for watchlist in watchlists:
            logger.info(f"  - {watchlist}")
            
        # 3. Teste Symbole einer Watchlist
        test_watchlist = watchlists[0]  # Erste Watchlist zum Testen verwenden
        try:
            symbols = norgatedata.watchlist_symbols(test_watchlist)
            if symbols:
                logger.info(f"Erfolgreich {len(symbols)} Symbole aus {test_watchlist} geladen")
                logger.info(f"Beispiel-Symbole: {symbols[:5]}")
            else:
                logger.warning(f"Keine Symbole in {test_watchlist} gefunden")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Symbole aus {test_watchlist}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Watchlists: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_norgate_connection()
    if success:
        logger.info("Verbindungstest erfolgreich abgeschlossen")
    else:
        logger.error("Verbindungstest fehlgeschlagen")
