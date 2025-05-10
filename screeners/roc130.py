import logging
from typing import List, Optional
import pandas as pd
from stock_indicators.indicators.common.quote import Quote
from stock_indicators import indicators
from utils.norgate_watchlist_symbols import get_watchlist_symbols
from utils.data_manager import EnhancedMarketDataManager

class ROC130Screener:
    def __init__(self, watchlist_name: Optional[str] = None):
        """
        ROC130 Screener zum Finden von Aktien die den ROC130 von unten nach oben durchbrechen.
        
        Args:
            watchlist_name: Optional, Name der zu scannenden Watchlist
        """
        self.mdm = EnhancedMarketDataManager(watchlist_name=watchlist_name)
        logging.basicConfig(level=logging.INFO)
        
    def create_quotes(self, df: pd.DataFrame) -> List[Quote]:
        """Konvertiert DataFrame zu Quote-Objekten für stock-indicators"""
        quotes = []
        for index, row in df.iterrows():
            quote = Quote()
            quote.date = index
            quote.open = float(row['open'])
            quote.high = float(row['high'])
            quote.low = float(row['low'])
            quote.close = float(row['close'])
            quote.volume = float(row['volume'])
            quotes.append(quote)
        return quotes
        
    def scan(self, roc_threshold: float = 40.0) -> List[str]:
        """
        Führt den ROC130 Scan durch.
        
        Args:
            roc_threshold: Schwellenwert für ROC130 Durchbruch (default: 40.0)
            
        Returns:
            Liste der Symbole, die das Kriterium erfüllen
        """
        # Daten laden (letzten 200 Tage für 130 ROC Berechnung)
        df = self.mdm.load_market_data(
            start_date="2024-01-01",  # Ausreichend Daten für 130 Perioden
            end_date="2025-01-04"
        )
        
        matches = []
        total_symbols = len(df['Symbol'].unique())
        
        for i, symbol in enumerate(df['Symbol'].unique(), 1):
            logging.info(f"Scanne {symbol} ({i}/{total_symbols})")
            
            # Daten für das Symbol extrahieren
            symbol_data = df[df['Symbol'] == symbol].copy()
            
            # Zu Quote-Objekten konvertieren
            quotes = self.create_quotes(symbol_data)
            
            # ROC130 berechnen
            roc_results = indicators.get_roc(quotes, 130)
            
            # Die letzten beiden ROC-Werte prüfen
            if len(roc_results) >= 2:
                yesterday_roc = roc_results[-1].roc
                day_before_roc = roc_results[-2].roc
                
                # Prüfen ob ROC von unter threshold auf über threshold gestiegen ist
                if day_before_roc < roc_threshold and yesterday_roc > roc_threshold:
                    matches.append({
                        'symbol': symbol,
                        'roc_yesterday': yesterday_roc,
                        'roc_day_before': day_before_roc
                    })
                    logging.info(f"Match gefunden: {symbol} (ROC: {yesterday_roc:.2f}%)")
        
        return matches

def main():
    # Screener für S&P 500 initialisieren
    screener = ROC130Screener(watchlist_name="S&P 500")
    
    # Scan durchführen
    matches = screener.scan(roc_threshold=40.0)
    
    # Ergebnisse ausgeben
    if matches:
        print("\nGefundene Matches:")
        print("Symbol\t\tROC (gestern)\tROC (vorgestern)")
        print("-" * 50)
        for match in matches:
            print(f"{match['symbol']}\t\t{match['roc_yesterday']:.2f}%\t\t{match['roc_day_before']:.2f}%")
    else:
        print("\nKeine Matches gefunden.")

if __name__ == "__main__":
    main()