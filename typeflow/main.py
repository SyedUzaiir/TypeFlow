import sys
import os
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from services.controller import TypingController

def setup_logging() -> None:
    """Configures application-wide logging to console and home folder logs/typeflow.log."""
    log_dir = Path.home() / ".typeflow" / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "typeflow.log"
    except Exception:
        # Fallback to local logs directory if home folder cannot be accessed
        log_dir = Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "typeflow.log"

    logger = logging.getLogger("TypeFlow")
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to initialize file logger: {e}", file=sys.stderr)

    # Console Stream Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("==============================================")
    logger.info("TypeFlow Application Started")
    logger.info(f"Log file location: {log_file}")

def main() -> None:
    # 1. Initialize Logging
    setup_logging()
    
    logger = logging.getLogger("TypeFlow")

    # 2. Configure DPI Scaling Policies
    # PySide6 handles High DPI scaling automatically by default.
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # 3. Start PySide Application
    app = QApplication(sys.argv)
    app.setApplicationName("TypeFlow")
    app.setApplicationVersion("1.0.0")

    # 4. Instantiate UI and Coordinator Controller
    logger.info("Creating Main Window and Typing Controller...")
    window = MainWindow()
    controller = TypingController(window)

    # 5. Display Interface
    window.show()

    # 6. Execute Application Event Loop
    logger.info("Entering main application event loop.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
