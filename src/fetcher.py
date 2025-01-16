"""
URL fetching and handling module.
Provides functionality to fetch web content with proper error handling.
"""

import re
import socket
import requests
from pathlib import Path

# Set a timeout for DNS resolution to prevent hanging
socket.setdefaulttimeout(3.0)

def getHost(url):
    """Extract and validate URL components using regex.
    
    Args:
        url (str): URL to parse
        
    Returns:
        tuple: (scheme, host, path, query) or None if invalid URL
    """
    try:
        scheme = re.search(r"\bhttps?://", url)
        host = re.search(r"([-%@a-z0-9]+\.)+[-%@a-z0-9]+", url)
        if not (scheme and host):
            return None
            
        # Quick DNS check - if it fails, the host doesn't exist
        socket.gethostbyname(host.group())
        
        path = re.search(r"((?<=[-%@a-z0-9])/[-%@a-z0-9]+)+", url)
        query = re.search(r"(\?[-%@a-z0-9]+=[-%@a-z0-9]+(&[-%@a-z0-9]+=[-%@a-z0-9]+)*)|(\?([-%@a-z0-9]+\+)*[-%@a-z0-9]+)", url)
        return (scheme.group(), host.group(), path.group() if path else "/", query.group() if query else "")
        
    except (socket.gaierror, socket.timeout):
        return None

def fetch(url, host, verify = True):
    """Fetch HTTP response from the given URL.
    
    Args:
        url (str): URL to fetch
        host (str): Host extracted from the URL
        verify (bool): Verify SSL certificate (default: True)
        
    Returns:
        requests.Response or str: HTTP response object or "SSLERR" for SSL errors
    """
    headers = {
        "user-agent": "SPyB/24.01",
        "host": host if isinstance(host, str) else host[1] if isinstance(host, tuple) else "",
        "Cache-control": "max-age=180, public"
    }
    try:
        return requests.get(url, headers=headers, verify=verify)
    except requests.exceptions.SSLError:
        return "SSLERR"
    except requests.exceptions.RequestException:
        return None

def handleErrors(response):
    """Handle HTTP status codes and log accordingly.
    
    Args:
        response (requests.Response): HTTP response object
        
    Returns:
        tuple: (status, reason)
    """
    if response == "SSLERR":
        return (None, "SSL Error")
    elif response is None:
        return (None, "Request Failed")
        
    status = response.status_code
    reason = response.reason
    return (status, reason)

def decodeBody(response, previewLen=None):
    """Decode HTTP response body using the specified character set.
    
    Args:
        response (requests.Response): HTTP response object
        previewLen (int, optional): Length of the preview. If None, returns full content.
        
    Returns:
        str: Decoded response body
    """
    if response == "SSLERR" or response is None:
        return ""
        
    body = response.content if previewLen is None else response.content[:previewLen]
    charset = response.encoding or 'utf-8'
    
    try:
        return body.decode(charset)
    except UnicodeDecodeError:
        return body.decode('ISO-8859-1', errors='replace')

def fetcher(url, verify=True):
    """Fetch and handle HTTP response from the given URL.
    
    Args:
        url (str): URL to fetch
        verify (bool): Verify SSL certificate (default: True)
        
    Returns:
        str or tuple: Decoded response body or error tuple
    """
    host = getHost(url)
    if host is None:
        return None
        
    response = fetch(url, host, verify)
    if response == "SSLERR":
        return "SSLERR"
    elif response is None:
        return None
            
    status, reason = handleErrors(response)
    if status != 200:
        return ("ERROR", status, reason, decodeBody(response, 1000))
        
    return decodeBody(response)  # Return full content