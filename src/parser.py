from markdownify import markdownify as md 
import logconf
logger = logconf.init()

# Converts an HTML Body to human-readable markdown.
def parse(html_body):
        markdown = md(html_body)
        logger.info(f"Markdown Body (First 750 Characters): {markdown[:750]}")
        return markdown