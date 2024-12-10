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
        try:
                max_log_size = config['max_log_size']
        except:
                max_log_size = 1048576
        try:
                max_log_backups = config["max_log_backups"]
        except:
                max_log_backups = 10
        loglevels = {
                "NOTSET": 0,
                "DEBUG": 10,
                "INFO": 20,
                "WARN": 30,
                "WARNING": 30,
                "ERROR": 40,
                "CRITICAL": 50,
                "FATAL": 50
        }
        try:
                log_level_tty = loglevels[config['terminal_logger_level']]
        except:
                log_level_tty = 20
        try:
                log_level_file = loglevels[config['file_logger_level']]
        except:
                log_level_file = 10
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
        

