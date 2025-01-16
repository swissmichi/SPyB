"""
Simple Python Browser (SPyB) main module.
Initializes and runs the text-based browser interface.
"""

import app_confvars as confvars
import tui

# Initialize browser with configured control style
control_style = confvars.tui_controls
interface = tui.init_tui(control_style) 

try:
    url = None
    while True:
        # Get initial or new URL
        if not url:
            url = interface.get_url()
            if not url:  # No URL provided
                break
                
        # Fetch and display content
        content = interface.fetch_url(url)
        if content is None:
            url = None  # Reset URL on fetch failure
            continue
            
        result = interface.display_html(content)
        if result == "RETRY":
            continue
            
        # Handle user input until URL change is requested
        while interface.handle_input():
            pass
        # Get new URL after input loop exits
        url = interface.current_url
finally:
    tui.cleanup()