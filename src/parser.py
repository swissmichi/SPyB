"""
HTML Parser module for SPyB.
Handles HTML content parsing and formatting for terminal display.
"""

# Third-party imports
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import HtmlLexer
from pygments.formatters import TerminalFormatter

# Local imports
import logconf

logger = logconf.logger

def parse(html_body):
    """Parse and format HTML content for terminal display.
    
    Args:
        html_body (str): Raw HTML content to parse
        
    Returns:
        tuple: (formatted_text, line_count)
            - formatted_text (str): Terminal-formatted text with syntax highlighting
            - line_count (int): Number of lines in the formatted text
    """
    if not html_body:
        return ("No content available.", 1)
        
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_body, 'html.parser')
    text_with_html_tags = soup.get_text()
    
    # Apply syntax highlighting for terminal display
    terminal_formatted = highlight(text_with_html_tags, HtmlLexer(), TerminalFormatter())
    logger.debug(f"Terminal formatted Body (first 500 characters): {terminal_formatted[:500]}")
    
    # Count lines for display purposes
    nlines = terminal_formatted.count('\n') + 1
    return (terminal_formatted, nlines)
