"""
Configuration variables module for SPyB.
Handles loading and managing configuration from JSON files.
"""

# Standard library imports
import json
from pathlib import Path

# Define log levels mapping
LOGLEVELS = {
    "NOTSET": 0,
    "DEBUG": 10,
    "INFO": 20,
    "WARN": 30,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
    "FATAL": 50
}

# Setup paths
cwd = Path.cwd()
parent_path = Path(__file__).parent
log_path = (parent_path / "../etc/logfile.log").resolve()
conf_path = (parent_path / "../etc/config.conf").resolve()
defaults_path = (parent_path / "../etc/config.def.conf").resolve()

# Load configuration
try:
    with open(conf_path) as json_data:
        config = json.load(json_data)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

# Load defaults
with open(defaults_path) as json_data:
    defaults = json.load(json_data)

# Initialize configuration variables with fallbacks to defaults
max_log_size = config.get('max_log_size', defaults['max_log_size'])
max_log_backups = config.get('max_log_backups', defaults['max_log_backups'])

# Get log levels with fallbacks
try:
    log_level_tty = LOGLEVELS[config['terminal_logger_level']]
except (KeyError, TypeError):
    log_level_tty = LOGLEVELS[defaults['terminal_logger_level']]

try:
    log_level_file = LOGLEVELS[config['file_logger_level']]
except (KeyError, TypeError):
    log_level_file = LOGLEVELS[defaults['file_logger_level']]

# Get control style with fallback
try:
    tui_controls = config["controls"]
except (KeyError, TypeError):
    tui_controls = defaults["controls"]
