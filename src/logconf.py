import logging
import logging.handlers
from pathlib import Path
import json
import sys
def init():
        cwd = Path.cwd()
        parent_path = Path(__file__).parent
        log_path = (parent_path / "../etc/logfile.log").resolve()
        conf_path = (parent_path / "../etc/config.json").resolve()
        logger = logging.getLogger(__name__)
       
        with open(conf_path) as json_data:
                config = json.load(json_data)
        max_log_size = config['max_log_size']
        max_log_backups = config["max_log_backups"]
        loglevels = {
                "NOTSET": 0,
                "DEBUG": 10,
                "INFO": 20,
                "WARN": 30,
                "ERROR": 40,
                "CRITICAL": 50
        }
        log_level_tty = loglevels[config['terminal_logger_level']]
        log_level_file = loglevels[config['file_logger_level']]
        logger.setLevel(min(log_level_tty, log_level_file))
        logger = logging.getLogger(__name__)
        file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=max_log_size, backupCount=max_log_backups)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s"))
        file_handler.setLevel(log_level_file)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        console_handler.setLevel(log_level_tty)
        logger.addHandler(console_handler)
        return logger
        

