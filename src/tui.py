import curses
import logging
import json
import colorama
from colorama import Fore, Back
colorama.just_fix_windows_console()
logger = logging.getLogger(__name__)
logging.basicConfig(LOG_FILENAME = "../etc/logfile.log", level=logging.DEBUG,  format="%(asctime)s - %(levelname)s - %(message)s")

screen = curses.initscr()
num_rows, num_cols = screen.getmaxyx()

logger.debug(f"Size: {num_rows} by {num_cols}")


address_bar = curses.newwin(1, num_cols - 20, 0, 0)
side_bar_opts = curses.newwin(1, 20, 0, num_cols - 20)
main_panel = curses.newpad(10000, num_cols - 20)
side_bar = curses.newpad(10000, 20)
controls = curses.newwin(1, num_cols, num_rows - 1, 0)





def handleStdIn(section, string):
        pass

def handleStdOut(section, string):
        pass