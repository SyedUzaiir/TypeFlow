import time
import logging
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger("TypeFlow")

class CountdownWorker(QThread):
    tick = Signal(int)
    countdown_completed = Signal()
    cancelled = Signal()
    error = Signal(str)

    def __init__(self, seconds: int):
        super().__init__()
        self.seconds = seconds
        self._is_cancelled = False

    def cancel(self) -> None:
        """Flags the worker to stop countdown immediately."""
        self._is_cancelled = True
        logger.info("Countdown cancellation requested.")

    def run(self) -> None:
        try:
            logger.info(f"Countdown started for {self.seconds} seconds.")
            current_seconds = self.seconds
            
            while current_seconds > 0:
                if self._is_cancelled:
                    self.cancelled.emit()
                    logger.info("Countdown worker cancelled successfully.")
                    return
                
                self.tick.emit(current_seconds)
                
                # Sleep in 100ms steps to check cancellation responsively
                for _ in range(10):
                    if self._is_cancelled:
                        self.cancelled.emit()
                        logger.info("Countdown worker cancelled during sleep step.")
                        return
                    self.msleep(100)
                
                current_seconds -= 1

            if self._is_cancelled:
                self.cancelled.emit()
                return

            self.countdown_completed.emit()
            logger.info("Countdown completed.")
        except Exception as e:
            logger.exception("Exception in countdown worker thread")
            self.error.emit(str(e))
