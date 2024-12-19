import curses
import logging
import json
import colorama
from colorama import Fore, Back
import logconf
colorama.just_fix_windows_console()
logger = logconf.init()
with open(conf_path) as json_data:
                config = json.load(json_data)
try:
        side_bar_size = config['side_bar_size']
except:
        side_bar_size = 30
screen = curses.initscr()
num_rows, num_cols = screen.getmaxyx()

logger.debug(f"Size: {num_rows} by {num_cols}")


address_bar = curses.newwin(1, num_cols - side_bar_size, 0, 0)
side_bar_opts = curses.newwin(1, side_bar_size, 0, num_cols - side_bar_size)
main_panel = curses.newpad(999999, num_cols - side_bar_size)
side_bar = curses.newpad(9999999, side_bar_size)
controls = curses.newwin(1, num_cols, num_rows - 1, 0)