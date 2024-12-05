import logging
import logging.handlers
from pathlib import Path
import json 
def init():
        cwd = Path.cwd()
        parent_path = Path(__file__).parent
        log_path = (parent_path / "../etc/logfile.log").resolve()
        logger = logging.getLogger(__name__)
