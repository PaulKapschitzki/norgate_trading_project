import unittest
import os
import sys
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Projektpfad zum Python Path hinzufügen
project_root = os.path.abspath('e:\\Eigene_Daten\\Programmierung\\Python\\Projects\\norgate_trading_project')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Test für die EnhancedMarketDataManager Klasse
class TestEnhancedMarketDataManager(unittest.TestCase):
    
    def setUp(self):
        # Mock-Dateipfad für Tests
        self.test_cache_file = os.path.join(project_root, 'tests', 'test_cache.parquet')
        # Sicherstellen, dass die Test-Datei nicht existiert
        if os.path.exists(self.test_cache_file):
            os.remove(self.test_cache_file)
    
    def tearDown(self):
        # Aufräumen nach dem Test
        if os.path.exists(self.test_cache_file):
            os.remove(self.test_cache_file)
    
    @patch('utils.data_manager.sanitize_filename')
    def test_sanitize_filename(self, mock_sanitize):
        """Test, ob die Dateinamen korrekt bereinigt werden"""
        from utils.data_manager import EnhancedMarketDataManager
        
        # Mock konfigurieren
        mock_sanitize.return_value = 's_p_500'
        
        # EnhancedMarketDataManager mit Watchlist-Namen initialisieren
        EnhancedMarketDataManager(watchlist_name="S&P 500")
        
        # Prüfen, ob sanitize_filename mit dem richtigen Argument aufgerufen wurde
        mock_sanitize.assert_called_once_with("S&P 500")
    
    @patch('utils.data_manager.Path.exists')
    @patch('utils.data_manager.Path.stat')
    def test_cache_valid(self, mock_stat, mock_exists):
        """Test, ob die Cache-Validierung korrekt funktioniert"""
        from utils.data_manager import EnhancedMarketDataManager
        
        # Mock konfigurieren
        mock_exists.return_value = True
        mock_stat_result = MagicMock()
        # Setze das Änderungsdatum auf heute
        mock_stat_result.st_mtime = datetime.now().timestamp()
        mock_stat.return_value = mock_stat_result
        
        # EnhancedMarketDataManager initialisieren und Cache-Gültigkeit prüfen
        mdm = EnhancedMarketDataManager(cache_file=self.test_cache_file)
        self.assertTrue(mdm.is_cache_valid())
        
        # Jetzt setzen wir das Änderungsdatum auf vor 2 Tagen (Cache zu alt)
        mock_stat_result.st_mtime = (datetime.now() - timedelta(days=2)).timestamp()
        mdm = EnhancedMarketDataManager(cache_file=self.test_cache_file, max_age_days=1)
        self.assertFalse(mdm.is_cache_valid())
    
    @patch('utils.data_manager.pd.read_parquet')
    @patch('utils.data_manager.EnhancedMarketDataManager.is_cache_valid')
    def test_load_market_data_from_cache(self, mock_is_valid, mock_read_parquet):
        """Test, ob Daten aus dem Cache geladen werden"""
        from utils.data_manager import EnhancedMarketDataManager
        
        # Mock konfigurieren
        mock_is_valid.return_value = True
        mock_df = pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT', 'GOOGL']*3,
            'Close': [150.0, 250.0, 2000.0]*3
        }, index=pd.date_range(start='2023-01-01', periods=9))
        mock_read_parquet.return_value = mock_df
        
        # Daten laden
        mdm = EnhancedMarketDataManager(cache_file=self.test_cache_file)
        result_df = mdm.load_market_data()
        
        # Prüfen, ob die Mock-Funktionen korrekt aufgerufen wurden
        mock_is_valid.assert_called_once()
        mock_read_parquet.assert_called_once_with(self.test_cache_file)
        
        # Prüfen, ob das Ergebnis korrekt ist
        self.assertEqual(len(result_df), 9)
        self.assertEqual(len(result_df['Symbol'].unique()), 3)

# Test für die MeanReversionStrategy Klasse
class TestMeanReversionStrategy(unittest.TestCase):
    
    def test_generate_signals(self):
        """Test, ob die Signalgenerierung korrekt funktioniert"""
        from strategies.mean_reversion import MeanReversionStrategy
        
        # Testdaten erstellen
        df = pd.DataFrame({
            'Symbol': ['AAPL', 'AAPL', 'AAPL', 'MSFT', 'MSFT', 'MSFT'],
            'Close': [100.0, 105.0, 95.0, 200.0, 210.0, 190.0],
            'Open': [101.0, 106.0, 90.0, 201.0, 211.0, 185.0]
        }, index=pd.date_range(start='2023-01-01', periods=6))
        
        # Strategie initialisieren und Signale generieren
        strategy = MeanReversionStrategy(gap_threshold=-0.03)  # 3% Gap nach unten
        result_df = strategy.generate_signals(df)
        
        # Prüfen, ob die Signale korrekt generiert wurden
        # AAPL: Tag 3 sollte ein Signal sein (Gap von ~-5% von 105 auf 90)
        # MSFT: Tag 6 sollte ein Signal sein (Gap von ~-5% von 210 auf 185)
        expected_signals = [False, False, True, False, False, True]
        self.assertListEqual(list(result_df['signal']), expected_signals)

# Test für die BacktestingEngine Klasse
class TestBacktestingEngine(unittest.TestCase):
    
    def test_execute_backtest(self):
        """Test, ob der Backtest korrekt ausgeführt wird"""
        from backtesting.backtesting_engine import BacktestingEngine
        
        # Testdaten mit Signalen erstellen
        df = pd.DataFrame({
            'Symbol': ['AAPL', 'AAPL', 'AAPL', 'AAPL'],
            'close': [100.0, 95.0, 98.0, 105.0],
            'signal': [False, True, True, False]
        }, index=pd.date_range(start='2023-01-01', periods=4))
        
        # Engine initialisieren und Backtest ausführen
        engine = BacktestingEngine()
        result = engine.execute_backtest(df)
        
        # Prüfen, ob das Ergebnis korrekt ist
        self.assertIn('total_trades', result)
        self.assertIn('avg_return', result)
        self.assertIn('win_rate', result)
        
        # Bei diesen Testdaten sollte ein Trade stattfinden
        # Einstieg bei Tag 2 (Signal True) mit Preis 95
        # Ausstieg bei Tag 4 (Signal False) mit Preis 105
        # Return sollte etwa 10.5% sein
        self.assertEqual(result['total_trades'], 1)
        self.assertGreater(result['avg_return'], 0)

# Integrationstest für die EnhancedBacktestPerformance Klasse
class TestEnhancedBacktestPerformance(unittest.TestCase):
    
    @patch('backtesting.performance.EnhancedMarketDataManager')
    def test_run_backtest(self, mock_mdm_class):
        """Test, ob der Backtest korrekt mit der Strategie ausgeführt wird"""
        from backtesting.performance import EnhancedBacktestPerformance
        from strategies.mean_reversion import MeanReversionStrategy
        
        # Mock für EnhancedMarketDataManager erstellen
        mock_mdm = MagicMock()
        mock_mdm_class.return_value = mock_mdm
        
        # Testdaten für den Mock konfigurieren
        test_df = pd.DataFrame({
            'Symbol': ['AAPL', 'AAPL', 'AAPL', 'MSFT', 'MSFT', 'MSFT'],
            'close': [100.0, 95.0, 105.0, 200.0, 190.0, 210.0],
            'open': [101.0, 90.0, 106.0, 201.0, 185.0, 211.0]
        }, index=pd.date_range(start='2023-01-01', periods=6))
        
        mock_mdm.load_market_data.return_value = test_df
        
        # Strategie und Backtest-Performance initialisieren
        strategy = MeanReversionStrategy(gap_threshold=-0.03)
        bp = EnhancedBacktestPerformance()
        
        # Backtest ausführen
        results = bp.run_backtest(
            strategy=strategy,
            symbols=['AAPL', 'MSFT'],
            start_date='2023-01-01',
            end_date='2023-01-06'
        )
        
        # Prüfen, ob die Methoden korrekt aufgerufen wurden
        mock_mdm.load_market_data.assert_called_once_with(
            start_date='2023-01-01',
            end_date='2023-01-06',
            symbols=['AAPL', 'MSFT']
        )
        
        # Prüfen, ob die Ergebnisse das richtige Format haben
        self.assertEqual(len(results), 2)  # AAPL und MSFT
        for result in results:
            self.assertIn('Symbol', result)
            self.assertIn('Results', result)
            self.assertIn('total_trades', result['Results'])

# Test für die Watchlist-Funktion
class TestWatchlistFunctions(unittest.TestCase):
    
    @patch('utils.norgate_watchlist_symbols.norgatedata.status')
    @patch('utils.norgate_watchlist_symbols.norgatedata.watchlists')
    @patch('utils.norgate_watchlist_symbols.norgatedata.watchlist_symbols')
    def test_get_watchlist_symbols(self, mock_watchlist_symbols, mock_watchlists, mock_status):
        """Test, ob die Watchlist-Funktion korrekt funktioniert"""
        from utils.norgate_watchlist_symbols import get_watchlist_symbols
        
        # Mocks konfigurieren
        mock_status.return_value = True
        mock_watchlists.return_value = [
            {'name': 'S&P 500', 'id': 1},
            {'name': 'Nasdaq 100', 'id': 2}
        ]
        mock_watchlist_symbols.return_value = ['AAPL', 'MSFT', 'GOOGL']
        
        # Funktion aufrufen
        result = get_watchlist_symbols('S&P 500', quiet=True)
        
        # Prüfen, ob die Funktion korrekt aufgerufen wurde
        mock_watchlist_symbols.assert_called_once_with('S&P 500')
        
        # Prüfen, ob das Ergebnis korrekt ist
        self.assertEqual(result, ['AAPL', 'MSFT', 'GOOGL'])
        
        # Test für nicht existierende Watchlist
        mock_watchlist_symbols.reset_mock()
        result = get_watchlist_symbols('Nicht existierend', quiet=True)
        
        # Prüfen, ob die Funktion nicht aufgerufen wurde
        mock_watchlist_symbols.assert_not_called()
        
        # Prüfen, ob das Ergebnis eine leere Liste ist
        self.assertEqual(result, [])

# Alle Tests ausführen
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)