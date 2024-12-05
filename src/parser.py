import fetcher
import json
import colorama
from colorama import Fore, Back
from html.parser import HTMLParser
colorama.just_fix_windows_console()
logger = logging.getLogger(__name__)
logging.basicConfig(LOG_FILENAME = "../etc/logfile.log", level=logging.DEBUG,  format="%(asctime)s - %(levelname)s - %(message)s")
