from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import HtmlLexer
from pygments.formatters import TerminalFormatter
import logconf
logger = logconf.init()

# Converts an HTML Body to Test with ANSI escape codes
def parse(html_body):
        soup = BeautifulSoup(html_body, 'html.parser')
        text_with_html_tags = soup.get_text()
        terminal_formatted = highlight(text_with_html_tags, HtmlLexer(), TerminalFormatter())
        logger.debug(f"Terminal formatted Body (first 500 characters): {terminal_formatted[:500]}")
        return terminal_formatted
