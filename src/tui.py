"""
Text User Interface (TUI) module for SPyB.
Provides curses-based interface for browsing web content.
"""

import curses
import logging
from pathlib import Path

# Local imports
import logconf
import fetcher
import parser
import app_confvars as confvars

logger = logconf.logger

def cleanup():
    """Clean up the terminal state."""
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def init_tui(control_style='vim'):
    """Initialize the TUI with the specified control style."""
    global screen, num_rows, num_cols
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    num_rows, num_cols = screen.getmaxyx()
    return TUI(control_style)

class TUI:
    def __init__(self, control_style='vim'):
        self.control_style = control_style
        self.controls_map = {
            'vim': VIM_CONTROLS,
            'nano': NANO_CONTROLS,
            'emacs': EMACS_CONTROLS
        }.get(control_style.lower(), VIM_CONTROLS)
        
        self.current_url = ""
        self.scroll_pos = 0
        self.cursor_y = 0
        self.content_lines = []
        self.links = []
        self.link_positions = {}
        self.last_search = ""
        self.search_matches = []  # List of line numbers containing matches
        self.current_match = -1  # Index into search_matches
        self.should_quit = False
        self.should_start_durak = False  # New flag for durak easter egg
        
        # Create windows
        self.init_windows()
        
    def init_windows(self):
        """Initialize or reinitialize the screen state"""
        global address_bar, controls, content_win
        
        # If we're reinitializing, clean up first
        if hasattr(self, 'screen'):
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()
        
        # Initialize screen
        self.screen = screen
        
        # Create windows
        address_bar = curses.newwin(1, num_cols, 0, 0)
        controls = curses.newwin(1, num_cols, num_rows - 1, 0)
        content_win = curses.newwin(num_rows - 2, num_cols, 1, 0)
        
        # Set up screen state
        curses.start_color()
        if confvars.tui_colors.lower() == "bright":
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        else:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        # Set window backgrounds
        self.address_bar = address_bar
        self.controls = controls
        self.content_win = content_win
        
        self.address_bar.bkgd(' ', curses.color_pair(1))
        self.content_win.bkgd(' ', curses.color_pair(3))
        
        # Set up input handling
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        
        # Initial refresh
        self.screen.refresh()
        self.address_bar.refresh()
        self.controls.refresh()
        self.content_win.refresh()

    def display_html(self, content):
        """Display parsed HTML content in the content window."""
        if content is None:
            self.show_error("No content to display.")
            return
        elif isinstance(content, tuple) and content[0] == "ERROR":
            _, status, reason, error_content = content
            if self.handle_http_error(status, reason, error_content):
                return "RETRY"
            return
            
        from parser import parse
        
        # Parse HTML and get formatted text
        formatted_content, num_lines = parse(content, base_url=self.current_url)
        if formatted_content is None:
            self.show_error("Failed to parse content.")
            return
            
        self.content_lines = formatted_content.split('\n')
        self.links = []
        self.link_positions = {}
        
        # Extract links from the formatted content
        import re
        link_pattern = r'\[(.*?)\]\((https?://[^\s\)]+)\)'
        for i, line in enumerate(self.content_lines):
            for match in re.finditer(link_pattern, line):
                link_text, href = match.groups()
                self.links.append((link_text, href))
                self.link_positions[i] = (link_text, href)
                
        self.cursor_y = 0
        self.scroll_pos = 0
        self.refresh_display()
        
    def follow_link(self):
        """Follow link at cursor position"""
        current_line = self.scroll_pos + self.cursor_y
        if current_line in self.link_positions:
            link_text, href = self.link_positions[current_line]
            self.current_url = href
            # Show the URL being followed
            self.address_bar.clear()
            try:
                self.address_bar.addstr(0, 0, f"Following: {href}")
                self.address_bar.refresh()
            except curses.error:
                pass
            return href
            
        # Only show "No link" message if there wasn't a link
        self.address_bar.clear()
        try:
            self.address_bar.addstr(0, 0, "No link at cursor position")
            self.address_bar.refresh()
            curses.napms(1000)  # Show message for 1 second
        except curses.error:
            pass
        return None
        
    def show_url_bar(self):
        """Show and allow editing of URL bar"""
        current_url = self.current_url if self.current_url else ""
        new_url = self.get_user_input("URL: ", current_url)
        if new_url:  # Accept any non-empty URL
            self.current_url = new_url
            return new_url
        return None

    def get_user_input(self, prompt="", prefill=""):
        """Get user input with optional prefilled text"""
        self.address_bar.clear()
        self.address_bar.addstr(0, 0, prompt + prefill)
        self.address_bar.refresh()
        
        curses.echo()
        self.address_bar.move(0, len(prompt) + len(prefill))  # Move cursor to end of prefill
        
        # Enable character reading
        self.address_bar.keypad(True)
        
        # Initialize input buffer with prefill
        input_buffer = list(prefill)
        cursor_pos = len(input_buffer)
        prompt_len = len(prompt)
        
        while True:
            try:
                c = self.address_bar.getch()
                
                if c == ord('\n'):  # Enter
                    break
                elif c == 27:  # Escape
                    input_buffer = list(prefill)  # Restore original
                    break
                elif c == curses.KEY_LEFT and cursor_pos > 0:
                    cursor_pos -= 1
                elif c == curses.KEY_RIGHT and cursor_pos < len(input_buffer):
                    cursor_pos += 1
                elif c == curses.KEY_BACKSPACE or c == 127:  # Backspace
                    if cursor_pos > 0:
                        input_buffer.pop(cursor_pos - 1)
                        cursor_pos -= 1
                elif c == curses.KEY_DC:  # Delete
                    if cursor_pos < len(input_buffer):
                        input_buffer.pop(cursor_pos)
                elif 32 <= c <= 126:  # Printable characters
                    input_buffer.insert(cursor_pos, chr(c))
                    cursor_pos += 1
                
                # Redraw input line
                self.address_bar.clear()
                self.address_bar.addstr(0, 0, prompt + ''.join(input_buffer))
                self.address_bar.move(0, prompt_len + cursor_pos)
                self.address_bar.refresh()
                
            except curses.error:
                pass
        
        curses.noecho()
        return ''.join(input_buffer)

    def get_yes_no(self, prompt):
        """Get a yes/no response from the user"""
        while True:
            response = self.get_user_input(f"{prompt} (y/N) ").lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['', 'n', 'no']:
                return False
            
    def handle_ssl_error(self):
        """Handle SSL certificate errors"""
        self.content_win.clear()
        warning = [
            "⚠️  SSL Certificate Error ⚠️",
            "",
            "The website's security certificate is not trusted.",
            "This could mean:",
            "  • The certificate has expired",
            "  • The certificate is self-signed",
            "  • The connection is being intercepted",
            "",
            "Loading this site may expose your data to attackers.",
            "",
            "Do you want to proceed anyway?",
        ]
        
        for i, line in enumerate(warning):
            try:
                if i == 0:  # Title in reverse video
                    self.content_win.addstr(i, (num_cols - len(line)) // 2, line, curses.A_REVERSE)
                else:
                    self.content_win.addstr(i, 2, line)
            except curses.error:
                pass
                
        self.content_win.refresh()
        return self.get_yes_no("Load unsafe site?")
        
    def handle_http_error(self, status, reason, error_content):
        """Handle HTTP error responses"""
        self.content_win.clear()
        
        # Get error description
        error_desc = {
            400: "Bad Request - The server cannot process the request due to client error",
            401: "Unauthorized - Authentication is required",
            403: "Forbidden - You don't have permission to access this resource",
            404: "Not Found - The requested resource could not be found",
            418: "I'm a teapot - The requested entity body is short and stout",
            500: "Internal Server Error - Something went wrong on the server",
            502: "Bad Gateway - The server received an invalid response",
            503: "Service Unavailable - The server is temporarily unable to handle the request",
            504: "Gateway Timeout - The server timed out waiting for another server"
        }.get(status, "Unknown Error")
        
        warning = [
            f"⚠️  HTTP Error {status} - {reason} ⚠️",
            "",
            error_desc,
            "",
            "Server Response:",
            "─" * (num_cols - 4),  # Horizontal line
        ]
        
        # Add error content (first few lines)
        if error_content:
            content_lines = error_content.split('\n')[:5]  # Show first 5 lines
            warning.extend(content_lines)
            if len(content_lines) == 5 and len(content_lines) < error_content.count('\n'):
                warning.append("...")
        
        warning.extend([
            "",
            "Do you want to retry?"
        ])
        
        for i, line in enumerate(warning):
            try:
                if i == 0:  # Title in reverse video
                    self.content_win.addstr(i, (num_cols - len(line)) // 2, line, curses.A_REVERSE)
                elif i == 5:  # Horizontal line
                    self.content_win.addstr(i, 2, line, curses.A_DIM)
                elif i > 5 and i < len(warning) - 2:  # Error content
                    self.content_win.addstr(i, 4, line, curses.A_DIM)
                else:
                    self.content_win.addstr(i, 2, line)
            except curses.error:
                pass
                
        self.content_win.refresh()
        return self.get_yes_no("Retry?")

    def get_url(self):
        """Get URL from user input"""
        if not self.current_url:
            return self.show_url_bar()
        return self.current_url

    def fetch_url(self, url):
        """Fetch content from URL with error handling"""
        import fetcher
        
        content = fetcher.fetcher(url)
        
        if content is None:
            self.show_error("Failed to fetch page. The host may not exist or your internet connection may be down.")
            self.current_url = ""  # Reset URL so user can enter a new one
            return None
        elif content == "SSLERR":
            if not self.handle_ssl_error():
                return None
            # Retry with SSL verification disabled
            content = fetcher.fetcher(url, verify=False)
            if content == "SSLERR":
                self.show_error("SSL Error persists. Cannot load page.")
                self.current_url = ""  # Reset URL so user can enter a new one
                return None
        elif isinstance(content, tuple) and content[0] == "ERROR":
            _, status, reason, error_content = content
            if not self.handle_http_error(status, reason, error_content):
                self.current_url = ""  # Reset URL so user can enter a new one
                return None
            # User wants to retry
            return self.fetch_url(url)
            
        return content

    def show_error(self, message):
        """Show an error message in the content window"""
        self.content_win.clear()
        try:
            self.content_win.addstr(1, 2, "Error:", curses.A_BOLD)
            self.content_win.addstr(1, 9, f" {message}")
            self.content_win.addstr(3, 2, "Press Enter to continue...")
        except curses.error:
            pass
        self.content_win.refresh()
        
        # Wait for Enter key specifically
        while True:
            try:
                key = self.content_win.getch()
                if key in (ord('\n'), ord('\r')):
                    break
            except curses.error:
                pass
        
        self.content_win.clear()
        self.content_win.refresh()

    def search_content(self):
        """Search content in the current page"""
        search_term = self.get_user_input("Search: ")
        if not search_term:
            return
        if search_term == "":
            return
        self.last_search = search_term.lower()
        self.search_matches = []
        self.current_match = -1
        
        # Find all matches
        for i, line in enumerate(self.content_lines):
            if self.last_search in line.lower():
                self.search_matches.append(i)
                
        if self.search_matches:
            self.jump_to_match(0)
        else:
            self.address_bar.clear()
            self.address_bar.addstr(0, 0, "No matches found")
            self.address_bar.refresh()
            
    def jump_to_match(self, match_index):
        """Jump to a specific match by index"""
        if not self.search_matches:
            return
            
        # Handle wrapping
        self.current_match = match_index % len(self.search_matches)
        line_num = self.search_matches[self.current_match]
        
        # Update display
        self.scroll_pos = max(0, min(line_num, len(self.content_lines) - (num_rows - 2)))
        self.cursor_y = line_num - self.scroll_pos
        
        # Show match position
        self.address_bar.clear()
        self.address_bar.addstr(0, 0, f"Match {self.current_match + 1} of {len(self.search_matches)}")
        self.address_bar.refresh()
        
        self.refresh_display()
        
    def find_next(self):
        """Find next occurrence of search term"""
        if self.search_matches:
            self.jump_to_match(self.current_match + 1)
            
    def find_previous(self):
        """Find previous occurrence of search term"""
        if self.search_matches:
            self.jump_to_match(self.current_match - 1)
        
    def refresh_display(self):
        """Refresh the display with current content."""
        try:
            self.content_win.clear()
            
            # Calculate visible range
            start = self.scroll_pos
            end = min(start + num_rows - 2, len(self.content_lines))
            
            # Display each line
            for i in range(start, end):
                y = i - start
                line = self.content_lines[i]
                
                # Handle links and search matches
                if i in self.link_positions:
                    link_text, _ = self.link_positions[i]
                    # Split line into parts: before link, link, after link
                    link_start = line.find(link_text)
                    if link_start != -1:
                        # Show parts before link
                        if link_start > 0:
                            self.content_win.addstr(y, 0, line[:link_start])
                            
                        # Show link with highlighting
                        attr = curses.A_REVERSE if y == self.cursor_y else curses.A_UNDERLINE
                        self.content_win.addstr(y, link_start, link_text, attr)
                        
                        # Show parts after link
                        after_link = link_start + len(link_text)
                        if after_link < len(line):
                            self.content_win.addstr(y, after_link, line[after_link:])
                    else:
                        # Fallback if link text not found
                        self.content_win.addstr(y, 0, line)
                        
                # Handle search highlights
                elif self.last_search and self.last_search in line.lower():
                    # Split line into segments based on matches
                    segments = []
                    last_end = 0
                    search_lower = self.last_search.lower()
                    line_lower = line.lower()
                    
                    while True:
                        pos = line_lower.find(search_lower, last_end)
                        if pos == -1:
                            segments.append((line[last_end:], False))
                            break
                        if pos > last_end:
                            segments.append((line[last_end:pos], False))
                        segments.append((line[pos:pos+len(search_lower)], True))
                        last_end = pos + len(search_lower)
                    
                    # Display segments with appropriate highlighting
                    x = 0
                    for text, is_match in segments:
                        attr = curses.A_REVERSE if is_match else curses.A_NORMAL
                        try:
                            self.content_win.addstr(y, x, text, attr)
                            x += len(text)
                        except curses.error:
                            pass
                else:
                    # Regular line
                    try:
                        attr = curses.A_REVERSE if y == self.cursor_y else curses.A_NORMAL
                        self.content_win.addstr(y, 0, line, attr)
                    except curses.error:
                        pass
                        
            # Show controls
            self.show_controls()
            
            # Refresh windows
            self.content_win.refresh()
            
        except curses.error:
            pass
            
    def _key_to_readable(self, key):
        """Convert control characters to readable format"""
        if len(key) == 1:
            if key == '\x1B':
                return 'M-'
            if ord(key) < 32:
                return f'^{chr(ord(key) + 64)}'
            return key
        elif key.startswith('\x1B'):
            return f'M-{key[1:]}'
        elif key == 'KEY_UP':
            return '↑'
        elif key == 'KEY_DOWN':
            return '↓'
        elif key == 'KEY_PPAGE':
            return 'PgUp'
        elif key == 'KEY_NPAGE':
            return 'PgDn'
        return key

    def show_controls(self):
        """Display current control scheme at the bottom."""
        try:
            up = self._key_to_readable(self.controls_map['up'])
            down = self._key_to_readable(self.controls_map['down'])
            quit_key = self._key_to_readable(self.controls_map['quit'])
            follow = self._key_to_readable(self.controls_map['follow_link'])
            term = self._key_to_readable(self.controls_map['show_terminal'])
            find = self._key_to_readable(self.controls_map['find'])
            open_url = self._key_to_readable(self.controls_map['open_url'])
            
            controls = [
                f"UP: {up}",
                f"DOWN: {down}",
                f"QUIT: {quit_key}",
                f"FOLLOW: {follow}",
                f"TERM: {term}",
                f"FIND: {find}",
                f"OPEN: {open_url}",
                "n: Next match",
                "N: Prev match"
            ]
            
            controls_text = " | ".join(controls)
            self.controls.clear()
            # Leave one character space at the end to prevent cursor wrapping
            max_length = num_cols - 1
            if len(controls_text) > max_length:
                controls_text = controls_text[:max_length - 3] + "..."
            self.controls.addstr(0, 0, controls_text)
            self.controls.refresh()
        except curses.error:
            pass

    def show_terminal(self):
        """Temporarily show the terminal by suspending curses"""
        curses.endwin()
        import os
        # Save current screen content
        os.system('tput smcup')
        input("\nPress Enter to return to the browser...")
        # Restore previous screen content
        os.system('tput rmcup')
        # Reinitialize the screen
        self.init_windows()
        self.refresh_display()

    def handle_input(self):
        """Handle user input based on current control scheme."""
        try:
            key = self.screen.getch()
            if key == -1:
                return True
                    
            # Convert key to string representation for comparison
            key_str = chr(key) if key < 256 else curses.keyname(key).decode('utf-8')
            
            # Secret durak keybind (Ctrl+D)
            if key == 4:  # Ctrl+D
                self.should_quit = True
                self.should_start_durak = True
                return False
            
            if key_str == self.controls_map['quit']:
                self.should_quit = True
                return False
            elif key_str == self.controls_map['find']:
                self.search_content()
            elif key_str == 'n':  # Next match
                self.find_next()
            elif key_str == 'N':  # Previous match
                self.find_previous()
            elif key_str == '\x1b':  # Escape key
                # Clear search highlights
                self.last_search = ""
                self.search_matches = []
                self.current_match = -1
                self.refresh_display()
            elif key_str == self.controls_map['open_url']:
                new_url = self.show_url_bar()
                if new_url:
                    self.current_url = new_url
                    return False  # Exit input loop to load new URL
            elif key_str == self.controls_map['follow_link']:
                url = self.follow_link()
                if url:
                    return False  # Exit input loop to load new URL
            elif key_str in (self.controls_map['up'], 'KEY_UP'):
                if self.search_matches and key_str == self.controls_map['up']:
                    self.find_previous()  # Use up key for previous match in vim mode
                else:
                    self.cursor_y = max(0, self.cursor_y - 1)
                    if self.cursor_y < 2:  # Keep cursor in view
                        self.scroll_pos = max(0, self.scroll_pos - 1)
            elif key_str in (self.controls_map['down'], 'KEY_DOWN'):
                if self.search_matches and key_str == self.controls_map['down']:
                    self.find_next()  # Use down key for next match in vim mode
                else:
                    max_y = min(num_rows - 3, len(self.content_lines) - 1)
                    self.cursor_y = min(max_y, self.cursor_y + 1)
                    if self.cursor_y > max_y - 2:  # Keep cursor in view
                        if self.scroll_pos + num_rows - 2 < len(self.content_lines):
                            self.scroll_pos += 1
            elif key_str == self.controls_map['show_terminal']:
                self.show_terminal()
                
            self.refresh_display()
            return not self.should_quit
            
        except curses.error:
            return True


VIM_CONTROLS = {
    'up': 'k',
    'down': 'j',
    'quit': 'q',
    'follow_link': 'f',
    'show_terminal': 't',
    'find': '/',  
    'open_url': 'o'
}

NANO_CONTROLS = {
    'up': 'KEY_UP',
    'down': 'KEY_DOWN',
    'quit': '\x18',  
    'follow_link': '\x06',  
    'show_terminal': '\x14',  
    'find': '\x17',  
    'open_url': '\x0F'
}

EMACS_CONTROLS = {
    'up': '\x10',  
    'down': '\x0E',  
    'quit': '\x18',  
    'follow_link': '\x0A',  
    'show_terminal': '\x1A',  
    'find': '\x13',
    'open_url': '\x0F'
}