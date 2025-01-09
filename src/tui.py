import curses
import logging
import confvars
import logconf

logger = logconf.logger
screen = curses.initscr()
num_rows, num_cols = screen.getmaxyx()

logger.debug(f"Size: {num_rows} by {num_cols}")

side_bar_size = confvars.tui_side_bar_size
address_bar = curses.newwin(1, num_cols - side_bar_size, 0, 0)
side_bar_opts = curses.newwin(1, side_bar_size, 0, num_cols - side_bar_size)
controls = curses.newwin(1, num_cols, num_rows - 1, 0)

