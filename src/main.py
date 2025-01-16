"""
Simple Python Browser (SPyB) main module.
Initializes and runs the text-based browser interface.
"""

import app_confvars as confvars
import tui

def main():
    # Initialize browser with configured control style
    control_style = confvars.tui_controls
    interface = tui.init_tui(control_style) 

    try:
        url = None
        while True:
            # Get initial or new URL
            if not url:
                url = interface.get_url()
                if not url or interface.should_quit:  # No URL provided or quit requested
                    break
                    
            # Fetch and display content
            content = interface.fetch_url(url)
            if content is None or interface.should_quit:
                url = None  # Reset URL on fetch failure
                if interface.should_quit:
                    break
                continue
                
            result = interface.display_html(content)
            if result == "RETRY" or interface.should_quit:
                if interface.should_quit:
                    break
                continue
                
            # Handle user input until URL change is requested
            while interface.handle_input():
                if interface.should_quit:
                    break
            if interface.should_quit:
                break
                
            # Get new URL after input loop exits
            url = interface.current_url
    except KeyboardInterrupt:
        pass
    finally:
        tui.cleanup()

if __name__ == "__main__":
    main()