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

logger = logconf.logger

class TUI:
    def __init__(self, control_style='vim'):
        self.init_screen()
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
        self.search_pos = -1

    def init_screen(self):
        """Initialize or reinitialize the screen state"""
        global screen, address_bar, controls, num_rows, num_cols
        
        # If we're reinitializing, clean up first
        if hasattr(self, 'screen'):
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()
        
        # Initialize screen
        screen = curses.initscr()
        num_rows, num_cols = screen.getmaxyx()
        
        # Create windows
        address_bar = curses.newwin(1, num_cols, 0, 0)
        controls = curses.newwin(1, num_cols, num_rows - 1, 0)
        self.content_win = curses.newwin(num_rows - 2, num_cols, 1, 0)
        
        # Set up screen state
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        # Set window backgrounds
        self.address_bar = address_bar
        self.controls = controls
        self.screen = screen
        
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
        from bs4 import BeautifulSoup
        
        # Parse HTML and extract links
        soup = BeautifulSoup(content, 'html.parser')
        self.links = []
        self.link_positions = {}  # Map line numbers to links
        
        # Process links and their positions
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not href.startswith(('http://', 'https://')):
                # Make relative URLs absolute
                from urllib.parse import urljoin
                href = urljoin(self.current_url, href)
            link_text = link.get_text().strip()
            if link_text:  # Only store links with visible text
                self.links.append((link_text, href))
            
        formatted_content, num_lines = parse(content)
        self.content_lines = formatted_content.split('\n')
        
        # Map links to line numbers
        for i, line in enumerate(self.content_lines):
            for link_text, href in self.links:
                if link_text in line:
                    self.link_positions[i] = (link_text, href)
        
        self.cursor_y = 0
        self.refresh_display()
        
    def follow_link(self):
        """Follow link at cursor position"""
        current_line = self.scroll_pos + self.cursor_y
        if current_line in self.link_positions:
            _, href = self.link_positions[current_line]
            self.current_url = href
            return href
        self.address_bar.clear()
        self.address_bar.addstr(0, 0, "No link at cursor position")
        self.address_bar.refresh()
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
        
        if content == "SSLERR":
            if self.handle_ssl_error():
                # Retry with SSL verification disabled
                content = fetcher.fetcher(url, verify=False)
                if content == "SSLERR":
                    self.show_error("SSL Error persists. Cannot load page.")
                    return None
                return content
            return None
        elif content is None:
            self.show_error("Failed to fetch page. Please try again.")
            return None
            
        return content

    def show_error(self, message):
        """Show an error message in the content window"""
        self.content_win.clear()
        try:
            self.content_win.addstr(1, 2, "Error:", curses.A_BOLD)
            self.content_win.addstr(1, 9, f" {message}")
        except curses.error:
            pass
        self.content_win.refresh()
    
    def search_content(self):
        """Search content in the current page"""
        search_term = self.get_user_input("Search: ")
        if not search_term:
            return
            
        self.last_search = search_term.lower()
        self.search_pos = -1
        self.find_next()
        
    def find_next(self):
        """Find next occurrence of search term"""
        if not self.last_search:
            return
            
        # Start from next position
        start_pos = self.search_pos + 1
        
        # Search in all lines
        for i in range(start_pos, len(self.content_lines)):
            if self.last_search in self.content_lines[i].lower():
                self.search_pos = i
                # Adjust scroll position to show the found text
                if i < self.scroll_pos or i >= self.scroll_pos + (num_rows - 2):
                    self.scroll_pos = max(0, min(i, len(self.content_lines) - (num_rows - 2)))
                self.cursor_y = i - self.scroll_pos
                self.refresh_display()
                return
                
        # If not found after current position, start from beginning
        if start_pos > 0:
            self.address_bar.clear()
            self.address_bar.addstr(0, 0, "Search wrapped to top")
            self.address_bar.refresh()
            for i in range(0, start_pos):
                if self.last_search in self.content_lines[i].lower():
                    self.search_pos = i
                    if i < self.scroll_pos or i >= self.scroll_pos + (num_rows - 2):
                        self.scroll_pos = max(0, min(i, len(self.content_lines) - (num_rows - 2)))
                    self.cursor_y = i - self.scroll_pos
                    self.refresh_display()
                    return
                    
        # If nothing found, show message
        self.address_bar.clear()
        self.address_bar.addstr(0, 0, f"No matches found for '{self.last_search}'")
        self.address_bar.refresh()
        self.search_pos = -1  # Reset search position
        
    def refresh_display(self):
        """Refresh the display with current content."""
        self.content_win.clear()
        
        display_lines = self.content_lines[self.scroll_pos:self.scroll_pos + (num_rows - 2)]
        for i, line in enumerate(display_lines):
            try:
                current_line = self.scroll_pos + i
                # Check if this line has a link
                if current_line in self.link_positions:
                    link_text = self.link_positions[current_line][0]
                    start_idx = line.find(link_text)
                    self.content_win.addstr(i, 0, line[:start_idx])
                    # Highlight link if cursor is on this line
                    attr = curses.A_REVERSE if i == self.cursor_y else curses.A_UNDERLINE
                    self.content_win.addstr(i, start_idx, link_text, attr)
                    self.content_win.addstr(i, start_idx + len(link_text), line[start_idx + len(link_text):])
                else:
                    # Regular line with cursor highlight if needed
                    attr = curses.A_REVERSE if i == self.cursor_y else curses.A_NORMAL
                    self.content_win.addstr(i, 0, line, attr)
            except curses.error:
                pass
                
        self.show_controls()
        self.content_win.refresh()
        
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
            # Convert control characters to readable format
            up = self._key_to_readable(self.controls_map['up'])
            down = self._key_to_readable(self.controls_map['down'])
            quit_key = self._key_to_readable(self.controls_map['quit'])
            follow = self._key_to_readable(self.controls_map['follow_link'])
            term = self._key_to_readable(self.controls_map['show_terminal'])
            find = self._key_to_readable(self.controls_map['find'])
            open_url = self._key_to_readable(self.controls_map['open_url'])
            
            controls_text = f"UP: {up} DOWN: {down} QUIT: {quit_key} FOLLOW: {follow} TERM: {term} FIND: {find} OPEN URL: {open_url}"
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
        self.init_screen()
        self.refresh_display()

    def handle_input(self):
        """Handle user input based on current control scheme."""
        key = self.screen.getch()
        if key == -1:
            return True
            
        # Handle multi-key sequences (like Ctrl-X Ctrl-C in Emacs)
        if self.controls_map['quit'] == '\x18\x03' and key == 0x18:  # Ctrl-X
            second_key = self.screen.getch()
            if second_key == 0x03:  # Ctrl-C
                cleanup()  # Ensure proper cleanup
                return False
                
        # Convert key to string representation for comparison
        key_str = chr(key) if key < 256 else curses.keyname(key).decode('utf-8')
        
        if key_str == self.controls_map['quit']:
            cleanup()  # Ensure proper cleanup
            return False
        elif key_str == self.controls_map['find']:
            self.search_content()
        elif key_str == self.controls_map['open_url']:
            new_url = self.show_url_bar()
            if new_url:
                return False  # Exit input loop to load new URL
        elif key_str == self.controls_map['follow_link']:
            url = self.follow_link()
            if url:
                return False  # Exit input loop to load new URL
        elif key_str in (self.controls_map['up'], 'KEY_UP'):
            self.cursor_y = max(0, self.cursor_y - 1)
            if self.cursor_y < 2:  # Keep cursor in view
                self.scroll_pos = max(0, self.scroll_pos - 1)
        elif key_str in (self.controls_map['down'], 'KEY_DOWN'):
            max_y = min(num_rows - 3, len(self.content_lines) - self.scroll_pos - 1)
            self.cursor_y = min(max_y, self.cursor_y + 1)
            if self.cursor_y > num_rows - 5:  # Keep cursor in view
                self.scroll_pos = min(len(self.content_lines) - (num_rows - 2), self.scroll_pos + 1)
        elif key_str == self.controls_map['scroll_up']:
            self.scroll_pos = max(0, self.scroll_pos - (num_rows - 2))
            self.cursor_y = 0  # Reset cursor position
        elif key_str == self.controls_map['scroll_down']:
            self.scroll_pos = min(len(self.content_lines) - (num_rows - 2), 
                                self.scroll_pos + (num_rows - 2))
            self.cursor_y = 0  # Reset cursor position
        elif key_str == self.controls_map['show_terminal']:
            self.show_terminal()
            
        self.refresh_display()
        return True

def init_tui(control_style='vim'):
    tui = TUI(control_style)
    return tui

def cleanup():
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()

VIM_CONTROLS = {
    'up': 'k',
    'down': 'j',
    'quit': 'q',
    'follow_link': 'f',
    'back': 'b',
    'scroll_up': 'u',
    'scroll_down': 'd',
    'show_terminal': 't',
    'find': '/',  
    'open_url': 'o'
}

NANO_CONTROLS = {
    'up': 'KEY_UP',
    'down': 'KEY_DOWN',
    'quit': '\x18',  
    'follow_link': '\x06',  
    'back': '\x02',  
    'scroll_up': 'KEY_PPAGE',
    'scroll_down': 'KEY_NPAGE',
    'show_terminal': '\x14',  
    'find': '\x17',  
    'open_url': '\x0F'
}

EMACS_CONTROLS = {
    'up': '\x10',  
    'down': '\x0E',  
    'quit': '\x18\x03',  
    'follow_link': '\x0A',  
    'back': '\x02',  
    'scroll_up': '\x1B\x76',  
    'scroll_down': '\x16',  
    'show_terminal': '\x1A',  
    'find': '\x13',
    'open_url': '\x0F'
}
