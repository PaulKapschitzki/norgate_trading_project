import norgatedata
import pandas as pd
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_database_symbols(database_name: str) -> list:
    """
    Holt Symbole aus der Norgate Datenbank mit Fehlerbehandlung.
    
    Args:
        database_name: Name der Norgate Datenbank
        
    Returns:
        Liste der Symbole oder leere Liste bei Fehler
    """
    try:
        # Prüfen ob Norgate Data Utility läuft
        if not norgatedata.status():
            raise ConnectionError("Norgate Data Utility ist nicht aktiv")
            
        # Symbole abrufen
        symbols = norgatedata.database_symbols(database_name)
        logging.info(f"Erfolgreich {len(symbols)} Symbole aus {database_name} geladen")
        return symbols
        
    except ConnectionError as e:
        # Verbindungsfehler zur Norgate Data Utility
        logging.error(f"Verbindungsfehler: {str(e)}")
        return []
        
    except Exception as e:
        # Unerwartete Fehler
        logging.error(f"Unerwarteter Fehler: {str(e)}")
        return []

def count_equity_symbols(symbols: list) -> int:
    """
    Zählt Aktien-Symbole mit Fehlerbehandlung.
    """
    counter = 0
    for symbol in symbols:
        try:
            if norgatedata.subtype1(symbol) == 'Equity':
                counter += 1
        except Exception as e:
            logging.warning(f"Fehler beim Prüfen von Symbol {symbol}: {str(e)}")
            continue
            
    return counter

def get_active_symbols() -> list:
    """
    Holt alle aktiven Aktien-Symbole aus der Norgate Datenbank.
    
    Returns:
        Liste der aktiven Aktien-Symbole
    """
    try:
        # Prüfen ob Norgate Data Utility läuft
        if not norgatedata.status():
            raise ConnectionError("Norgate Data Utility ist nicht aktiv")
        
        # Aktive Symbole abrufen
        symbols = norgatedata.symbols(norgatedata.SymbolType.ACTIVE)
        
        # Filtere auf Aktien
        equity_symbols = [
            symbol for symbol in symbols 
            if norgatedata.subtype1(symbol) == 'Equity'
        ]
        
        logging.info(f"Erfolgreich {len(equity_symbols)} aktive Aktien-Symbole geladen")
        return equity_symbols
        
    except Exception as e:
        logging.error(f"Fehler beim Laden der aktiven Symbole: {str(e)}")
        return []

# def get_symbol_details(symbols: list) -> list:
#     """
#     Holt Details (Symbol, Firmenname) für jedes Aktien-Symbol.
    
#     Args:
#         symbols: Liste der zu prüfenden Symbole
        
#     Returns:
#         Liste von Tupeln (Symbol, Firmenname, ist_aktie)
#     """
#     details = []
#     for symbol in symbols:
#         try:
#             if norgatedata.subtype1(symbol) == 'Equity':
#                 security_name = norgatedata.security_name(symbol)
#                 details.append((symbol, security_name))
#                 # logging.info(f"Symbol: {symbol:<6} | Firma: {security_name}")
#         except Exception as e:
#             logging.warning(f"Fehler beim Abrufen der Details für {symbol}: {str(e)}")
#             continue
#     return details

if __name__ == '__main__':
    # Aktive Aktien
    print("\n=== Aktive Aktien ===")
    active_database = 'US Equities'
    active_symbols = get_database_symbols(active_database)
    # active_details = get_symbol_details(active_symbols)
    # print(f"\nAnzahl aktiver Aktien in {active_database}: {len(active_details)}")
    
    # Delistete Aktien
    print("\n=== Delistete Aktien ===")
    delisted_database = 'US Equities Delisted'
    delisted_symbols = get_database_symbols(delisted_database)
    # delisted_details = get_symbol_details(delisted_symbols)
    # print(f"\nAnzahl delisteter Aktien in {delisted_database}: {len(delisted_details)}")
    
    # Gesamtstatistik
    # total_count = len(active_details) + len(delisted_details)
    total_count = len(active_symbols) + len(delisted_symbols)
    print(f"\n=== Zusammenfassung ===")
    print(f"Gesamtanzahl aller Aktien: {total_count}")
    print(f"- Davon aktiv: {len(active_symbols)}")
    print(f"- Davon delistet: {len(delisted_symbols)}")