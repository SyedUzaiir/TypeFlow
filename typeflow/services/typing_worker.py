import time
import random
import logging
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from core.models import TypingSettings, TypingProgress
from services.typing_backend import TypingBackend

logger = logging.getLogger("TypeFlow")

class TypingWorker(QThread):
    # Signals
    progress = Signal(object)      # Emits TypingProgress
    paused = Signal()
    resumed = Signal()
    completed = Signal()
    cancelled = Signal()
    error = Signal(str)

    def __init__(self, text: str, start_index: int, settings: TypingSettings, elapsed_seconds: int = 0):
        super().__init__()
        self.text = text
        self.current_index = start_index
        self.settings = settings
        self.elapsed_seconds = float(elapsed_seconds)
        
        # Thread safety control
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self._is_paused = False
        self._is_cancelled = False
        
        # Initialize backend
        self.backend = TypingBackend()

    def pause(self) -> None:
        """Pauses the typing worker thread."""
        self.mutex.lock()
        self._is_paused = True
        self.mutex.unlock()
        self.paused.emit()
        logger.info("Typing worker paused.")

    def resume(self) -> None:
        """Resumes the typing worker thread."""
        self.mutex.lock()
        self._is_paused = False
        self.condition.wakeAll()
        self.mutex.unlock()
        self.resumed.emit()
        logger.info("Typing worker resumed.")

    def cancel(self) -> None:
        """Stops the typing worker immediately."""
        self.mutex.lock()
        self._is_cancelled = True
        # Wake up if it was paused to let it exit
        self._is_paused = False
        self.condition.wakeAll()
        self.mutex.unlock()
        logger.info("Typing worker cancellation requested.")

    def run(self) -> None:
        try:
            logger.info(f"Typing worker started from index {self.current_index} of {len(self.text)} characters.")
            self.backend.initialize()
            
            total_chars = len(self.text)
            
            # Prepare punctuation filter set if punctuation should be skipped
            punctuation_set = set(".,?!:;p'\"()[]{}-_+=*&^%$#@~`\\|/<>")
            
            last_tick_time = time.time()
            chars_typed_this_session = 0

            while self.current_index < total_chars:
                # 1. Thread-safe Pause handling
                self.mutex.lock()
                while self._is_paused:
                    # When pausing, reset last tick time so pause duration is not counted in typing stats
                    self.condition.wait(self.mutex)
                    last_tick_time = time.time()
                
                # Check cancellation immediately after waking
                if self._is_cancelled:
                    self.mutex.unlock()
                    self.cancelled.emit()
                    logger.info("Typing worker cancelled.")
                    return
                self.mutex.unlock()

                # Get current character
                char = self.text[self.current_index]

                # Apply option filters
                skip_char = False
                
                # Check if punctuation should be skipped
                if not self.settings.type_punctuation and char in punctuation_set:
                    skip_char = True
                
                # Check if line breaks should be skipped / flattened
                if char == "\n" and not self.settings.preserve_breaks:
                    # Instead of newline, replace with space
                    char = " "

                # Type character if not skipped
                if not skip_char:
                    # Calculate delay
                    base_delay = self.settings.get_char_delay()
                    if self.settings.randomize_delay and base_delay > 0:
                        # Add +/- 25% deviation
                        delay = base_delay * (1.0 + random.uniform(-0.25, 0.25))
                        delay = max(0.001, delay) # Keep positive
                    else:
                        delay = base_delay

                    # Simulate keypress
                    self.backend.type_character(char)
                    chars_typed_this_session += 1
                    
                    # Sleep for character delay
                    if delay > 0:
                        # Check cancellation in smaller chunks during sleep for maximum responsiveness
                        sleep_steps = int(delay / 0.005)
                        if sleep_steps > 0:
                            for _ in range(sleep_steps):
                                if self._is_cancelled:
                                    self.cancelled.emit()
                                    return
                                self.msleep(5)
                        else:
                            self.msleep(int(delay * 1000))

                # Update stats
                now = time.time()
                self.elapsed_seconds += (now - last_tick_time)
                last_tick_time = now

                # Calculate CPM (Chars Per Minute)
                if self.elapsed_seconds > 0.1:
                    cpm = int((chars_typed_this_session / self.elapsed_seconds) * 60)
                else:
                    cpm = 0

                # Calculate remaining chars and ETA
                remaining_chars_count = total_chars - (self.current_index + 1)
                if chars_typed_this_session > 0:
                    avg_time_per_char = self.elapsed_seconds / chars_typed_this_session
                else:
                    avg_time_per_char = self.settings.get_char_delay()
                
                eta_seconds = int(remaining_chars_count * avg_time_per_char)

                # Prepare character preview slices
                prev_slice = self.text[max(0, self.current_index - 15):self.current_index]
                curr_char = self.text[self.current_index]
                next_slice = self.text[self.current_index + 1:self.current_index + 16]

                # Emit progress
                progress_obj = TypingProgress(
                    index=self.current_index + 1,
                    total=total_chars,
                    elapsed_seconds=int(self.elapsed_seconds),
                    eta_seconds=eta_seconds,
                    cpm=cpm,
                    previous_chars=prev_slice,
                    current_char=curr_char,
                    remaining_chars=next_slice
                )
                self.progress.emit(progress_obj)

                # Move index forward
                self.current_index += 1

            # Complete hook: press enter after typing if configured
            if self.settings.press_enter:
                self.backend.press_enter()

            self.completed.emit()
            logger.info("Typing worker completed successfully.")
        except Exception as e:
            logger.exception("Exception in typing worker thread")
            self.error.emit(str(e))
        finally:
            self.backend.cleanup()
