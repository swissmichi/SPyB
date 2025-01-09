import logconf
import json
from pathlib import Path


cwd = Path.cwd()
parent_path = Path(__file__).parent
log_path = (parent_path / "../etc/logfile.log").resolve()
conf_path = (parent_path / "../etc/config.conf").resolve()
defaults_path = (parent_path / "../etc/config.def.conf").resolve()
with open(conf_path) as json_data:
                config = json.load(json_data)
with open(defaults_path) as json_data:
                defaults = json.load(json_data)


try:
        max_log_size = config['max_log_size']
except:
        max_log_size = defaults['max_log_size']
try:
        max_log_backups = config["max_log_backups"]
except:
        max_log_backups = defaults['max_log_backups']
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
        log_level_tty = loglevels[defaults['terminal_logger_level']]
try:
        log_level_file = loglevels[config['file_logger_level']]
except:
        log_level_file = loglevels[defaults['file_logger_level']]

try:
        tui_side_bar_size = config['side_bar_size']
except:
        tui_side_bar_size = defaults['side_bar_size']