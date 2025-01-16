"""
Logging configuration module for SPyB.
Sets up colored logging with both file and terminal output.
"""

# Standard library imports
import logging
import logging.handlers
from pathlib import Path

# Third-party imports
from colorama import Fore, Style

# Local imports
import app_confvars as confvars

def init():
    """Initialize logging configuration with color support.
    
    Sets up two handlers:
    - StreamHandler for terminal output with color formatting
    - RotatingFileHandler for file output
    
    Returns:
        logging.Logger: Configured logger instance
    """
    class ColoredFormatter(logging.Formatter):
        """Custom formatter that adds color to terminal output based on log level."""
        
        format = "%(asctime)s - %(levelname)s - %(message)s"
        
        FORMATS = {
            logging.DEBUG: format,
            logging.INFO: format,
            logging.WARNING: Fore.YELLOW + format + Fore.RESET,
            logging.ERROR: Fore.RED + format + Fore.RESET,
            logging.CRITICAL: Fore.RED + Style.BRIGHT + format + Fore.RESET + Style.RESET_ALL
        }
        
        def format(self, record):
            """Format log record with appropriate color."""
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
            
    # Setup paths and configuration
    parent_path = Path(__file__).parent
    log_path = (parent_path / "../etc/logfile.log").resolve()
    log_level_tty = confvars.log_level_tty
    log_level_file = confvars.log_level_file
    max_log_size = confvars.max_log_size
    max_log_backups = confvars.max_log_backups
    
    # Initialize logger
    logger = logging.getLogger('spyb')
    if not logger.handlers:  # Only add handlers if they don't exist
        logger.setLevel(min(log_level_tty, log_level_file))
        
        # Terminal handler with color support
        tty_handler = logging.StreamHandler()
        tty_handler.setLevel(log_level_tty)
        tty_handler.setFormatter(ColoredFormatter())
        logger.addHandler(tty_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_log_size,
            backupCount=max_log_backups
        )
        file_handler.setLevel(log_level_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
    
    return logger

# Get or create logger instance
logger = init()
