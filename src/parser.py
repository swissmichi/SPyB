from markdownify import markdownify as md 
import logconf
logger = logconf.init()

def parse(html_body):
        markdown = md(html_body)
        logger.info(f"Markdown Body (First 750 Characters): {markdown[:750]}")
        return markdown