"""
HTML Parser module for SPyB.
Handles HTML content parsing and formatting for terminal display.
"""

# Third-party imports
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def format_link(text, href, base_url=None):
    """Format a link in markdown style."""
    if base_url and not href.startswith(('http://', 'https://')):
        href = urljoin(base_url, href)
    return f"[{text}]({href})"

def parse(html_body, base_url=None):
    """Parse and format HTML content for terminal display.
    
    Args:
        html_body (str): Raw HTML content to parse
        base_url (str, optional): Base URL for resolving relative links
        
    Returns:
        tuple: (formatted_text, line_count)
            - formatted_text (str): Plain text extracted from HTML
            - line_count (int): Number of lines in the formatted text
    """
    if not html_body:
        return ("No content available.", 1)
        
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_body, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Process links first
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text().strip()
        if text:  # Only process links with visible text
            link.replace_with(format_link(text, href, base_url))
    
    # Get text and handle spacing
    lines = []
    for element in soup.stripped_strings:
        lines.extend(element.split('\n'))
    
    # Join lines with proper spacing
    formatted_text = '\n'.join(line.strip() for line in lines if line.strip())
    nlines = formatted_text.count('\n') + 1
    
    return (formatted_text, nlines)
