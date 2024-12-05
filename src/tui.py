'''
    This Script is part of SPyB.
    Copyright (C) 2024  Stepan Khristolyubov

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import curses
import logging
import json
import colorama
from colorama import Fore, Back
colorama.just_fix_windows_console()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,  format="%(asctime)s - %(levelname)s - %(message)s")

screen = curses.initscr()
num_rows, num_cols = screen.getmaxyx()

logger.debug(f"Size: {num_rows} by {num_cols}")


address_bar = curses.newwin(1, num_cols - 20, 0, 0)
side_bar_opts = curses.newwin(1, 20, 0, num_cols - 20)

controls = curses.newwin(1, num_cols, num_rows - 1, 0)




def handleStdIn(section, string):
        section.addstr(0,0,string)
        curses.echo()
        return screen.getstr().decode()

def handleStdOut(section, string):
        section.addstr(0,0,string)