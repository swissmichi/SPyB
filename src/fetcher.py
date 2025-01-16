"""
URL fetching and handling module.
Provides functionality to fetch web content with proper error handling and logging.
"""

import re
import socket
import logging
import requests
from pathlib import Path

import logconf

logger = logconf.logger

def getHost(url):
    """Extract and validate URL components using regex.
    
    Args:
        url (str): URL to parse
        
    Returns:
        tuple: (scheme, host, path, query) or None if invalid URL
    """
    scheme = re.search(r"\bhttps?://", url)
    host = re.search(r"([-%@a-z0-9]+\.)+[-%@a-z0-9]+", url)
    path = re.search(r"((?<=[-%@a-z0-9])/[-%@a-z0-9]+)+", url)
    query = re.search(r"(\?[-%@a-z0-9]+=[-%@a-z0-9]+(&[-%@a-z0-9]+=[-%@a-z0-9]+)*)|(\?([-%@a-z0-9]+\+)*[-%@a-z0-9]+)", url)
    
    if scheme and host:
        logger.debug(f"Scheme: {scheme.group()}")
        logger.info(f"Host: {host.group()}")
        try:
            logger.debug(f"Host IP: {socket.gethostbyname(host.group())}")
        except:
            logger.error(f"The host {host.group()} doesn't appear to exist. Please check the address and your internet connection.")
            return None
            
        if path:
            logger.debug(f"Path: {path.group()}")
        else:
            logger.debug("Path: None")
            
        if query:
            logger.debug(f"Query: {query.group()}")
            
        return (scheme.group(), host.group(), path.group() if path else "/", query.group() if query else "")
    return None

def fetch(url, host, verify = True):
    """Fetch HTTP response from the given URL.
    
    Args:
        url (str): URL to fetch
        host (str): Host extracted from the URL
        verify (bool): Verify SSL certificate (default: True)
        
    Returns:
        requests.Response: HTTP response object
    """
    headers = {"user-agent" : "SPyB/0.1", 
               "host" : host,
               "Cache-control": "max-age=180, public"}
    try:
        response = requests.get(url, headers = headers, verify=verify)
        return response
    except requests.exceptions.SSLError as ssl_err:
        logger.critical(f"SSL Error occured: {ssl_err}")
        return "SSLERR"
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request Error occurred: {req_err}")
        return None

def handleErrors(response):
    """Handle HTTP status codes and log accordingly.
    
    Args:
        response (requests.Response): HTTP response object
        
    Returns:
        tuple: (status, reason)
    """
    status = response.status_code
    reason = response.reason
    if 199 < status < 203 or 206 < status < 300:
        logger.info(f"Status: {status} {reason}")
    elif 202 < status < 207 or 299 < status < 400:
        logger.warn(f"Status: {status} {reason}")
    elif 399 < status < 600:
        logger.error(f"Status: {status} {reason}")
    return (status, reason)

def decodeBody(response, previewLen):
    """Decode HTTP response body using the specified character set.
    
    Args:
        response (requests.Response): HTTP response object
        previewLen (int): Length of the preview
        
    Returns:
        str: Decoded response body
    """
    contentType = response.headers['Content-Type']
    logger.debug(f'Content-Type: {contentType}')
    charsetMatch = re.search(r'charset=([\w-]+)', contentType)
    charset = charsetMatch.group(1) if charsetMatch else "utf-8"
    logger.debug(charset)
    body = response.content

    try:
        decodeBody = body.decode(charset)
        logger.debug(f"Body Decoded (First {previewLen} Characters): {decodeBody[:previewLen]}")
        return decodeBody
    except UnicodeDecodeError as dec_err:
        logger.error(f"Decoding failed: {dec_err}")
        return body.decode('ISO-8859-1', errors='replace')

def fetcher(url, verify=True):
    """Fetch and handle HTTP response from the given URL.
    
    Args:
        url (str): URL to fetch
        verify (bool): Verify SSL certificate (default: True)
        
    Returns:
        str: Decoded response body or error message
    """
    host = getHost(url)
    if host == None:
        return None
    else:
        response = fetch(url, host, verify)
        if response == "SSLERR" or response is None:
            return response
                    
        status, reason = handleErrors(response)
        if status > 399:
            return ("ERROR", status, reason, decodeBody(response, 500))
                
        return decodeBody(response, 500)