import logging
import logging.handlers
from pathlib import Path
import confvars
from colorama import Fore, Style
import sys
def init():
        class ColoredFormatter(logging.Formatter):

                format = "%(asctime)s - %(levelname)s - %(message)s"

                FORMATS = {
                        logging.DEBUG: format,
                        logging.INFO: format,
                        logging.WARNING: Fore.YELLOW + format + Fore.RESET,
                        logging.ERROR: Fore.RED + format + Fore.RESET,
                        logging.CRITICAL: Fore.RED + Style.BRIGHT + format + Fore.RESET + Style.RESET_ALL
        }

                def format(self, record):
                        log_fmt = self.FORMATS.get(record.levelno)
                        formatter = logging.Formatter(log_fmt)
                        return formatter.format(self, record)
        cwd = Path.cwd()
        parent_path = Path(__file__).parent
        log_path = (parent_path / "../etc/logfile.log").resolve()
        log_level_tty = confvars.log_level_tty
        log_level_file = confvars.log_level_file
        max_log_size = confvars.max_log_size
        max_log_backups = confvars.max_log_backups

        logger = logging.getLogger(__name__)
        logger.propagate = False
        logger.setLevel(min(log_level_tty, log_level_file))
        file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=max_log_size, backupCount=max_log_backups)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s"))
        file_handler.setLevel(log_level_file)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter)
        console_handler.setLevel(log_level_tty)
        logger.addHandler(console_handler)
        logger.debug(logger.handlers)
        return logger
        
logger = init()
