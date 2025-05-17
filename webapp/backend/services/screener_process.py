"""Service zum Verwalten des Screener-Prozesses"""
import threading
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ScreenerProcess:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialisiert die Singleton-Instanz"""
        self.current_process: Optional[threading.Thread] = None
        self.stop_requested: bool = False
        self.status: str = "idle"
        self.progress: Dict[str, Any] = {
            "total_symbols": 0,
            "processed_symbols": 0,
            "current_symbol": None
        }
        self._process_lock = threading.Lock()

    def start_process(self, process_func, *args, **kwargs):
        """Startet einen neuen Screening-Prozess"""
        with self._process_lock:
            if self.current_process and self.current_process.is_alive():
                raise RuntimeError("Ein Screening-Prozess läuft bereits")
            
            self.stop_requested = False
            self.status = "running"
            self.progress = {
                "total_symbols": 0,
                "processed_symbols": 0,
                "current_symbol": None
            }
            
            def wrapper():
                try:
                    process_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Fehler im Screening-Prozess: {e}")
                finally:
                    if not self.stop_requested:
                        self.status = "completed"
                    self.current_process = None

            self.current_process = threading.Thread(target=wrapper)
            self.current_process.start()

    def stop_process(self):
        """Stoppt den aktuellen Screening-Prozess"""
        with self._process_lock:
            if not self.current_process or not self.current_process.is_alive():
                return False
            
            self.stop_requested = True
            self.status = "stopping"
            return True

    def update_progress(self, total_symbols: int, processed_symbols: int, current_symbol: str):
        """Aktualisiert den Fortschritt des Screenings"""
        self.progress = {
            "total_symbols": total_symbols,
            "processed_symbols": processed_symbols,
            "current_symbol": current_symbol
        }

    def get_status(self) -> Dict[str, Any]:
        """Gibt den aktuellen Status des Screening-Prozesses zurück"""
        return {
            "status": self.status,
            "progress": self.progress,
            "is_running": bool(self.current_process and self.current_process.is_alive())
        }
