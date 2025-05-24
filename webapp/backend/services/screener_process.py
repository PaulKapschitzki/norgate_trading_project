"""Service zum Verwalten des Screener-Prozesses"""
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any
import logging
from webapp.backend.models.screener_status_new import ScreenerStatus

logger = logging.getLogger(__name__)

class ScreenerProcess:
    _instance = None
    _lock = threading.Lock()
    _executor = ThreadPoolExecutor(max_workers=1)

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialisiert die Singleton-Instanz"""
        self.current_process: Optional[asyncio.Task] = None
        self.stop_requested: bool = False
        self.status: str = "idle"
        self.progress: Dict[str, Any] = {
            "total_symbols": 0,
            "processed_symbols": 0,
            "current_symbol": None,
            "error_message": None
        }
        self._process_lock = threading.Lock()

    def stop_process(self) -> bool:
        """Stoppt den aktuellen Screening-Prozess"""
        with self._process_lock:
            if not self.current_process or self.current_process.done():
                return False
            
            self.stop_requested = True
            self.status = "stopping"
            return True

    def update_progress(self, total_symbols: int, processed_symbols: int, 
                       current_symbol: str, error_message: Optional[str] = None) -> None:
        """Aktualisiert den Fortschritt des Screenings"""
        with self._process_lock:
            self.progress = {
                "total_symbols": total_symbols,
                "processed_symbols": processed_symbols,
                "current_symbol": current_symbol,
                "error_message": error_message
            }
            
            if error_message:
                logger.error(f"Screening-Fehler: {error_message}")

    def get_status_response(self) -> dict:
        """Liefert den aktuellen Status im korrekten Format zurück"""
        with self._process_lock:
            is_running = bool(
                self.current_process and 
                not self.current_process.done() and 
                self.status not in ["completed", "error", "idle"]
            )
            
            return {
                "status": self.status,
                "progress": {
                    "total_symbols": self.progress["total_symbols"],
                    "processed_symbols": self.progress["processed_symbols"],
                    "current_symbol": self.progress.get("current_symbol"),
                    "error_message": self.progress.get("error_message")
                },
                "is_running": is_running
            }

    async def cleanup(self):
        """Cleanup-Methode für den Shutdown"""
        logger.info("Führe Screener Process Cleanup durch...")
        self._executor.shutdown(wait=True)
        
        if self.current_process and not self.current_process.done():
            self.stop_requested = True
            self.status = "stopping"
            try:
                await asyncio.wait_for(self.current_process, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Timeout beim Warten auf Prozess-Beendigung")
