import requests
import re
import logging
import json
import socket
import colorama
from colorama import Fore, Back
from pathlib import Path
# Below are files found in /src
import logconf
import parser
# import tui

colorama.just_fix_windows_console()
logger = logconf.init()

# Gets the Host using RegEx
def getHost(url):
        scheme = re.search(r"\bhttps?://", url)
        host = re.search(r"([-%@a-z0-9]+\.)+[-%@a-z0-9]+", url) # Important part
        path = re.search(r"((?<=[-%@a-z0-9])/[-%@a-z0-9]+)+", url)
        query = re.search(r"(\?[-%@a-z0-9]+=[-%@a-z0-9]+(&[-%@a-z0-9]+=[-%@a-z0-9]+)*)|(\?([-%@a-z0-9]+\+)*[-%@a-z0-9]+)", url)
        if scheme and host:
                logger.debug(f"Scheme: {scheme.group()}")
                logger.info(f"Host: {host.group()}")
                try:
                        logger.debug(f"Host IP: {socket.gethostbyname(host.group())}")
                except:
                        logger.error(f"The host {host.group()} doesn't appear to exist. Please check the address and your internet connection.")
                if path:
                        logger.debug(f"Path: {path.group()}")
                else:
                        logger.debug("Path: None")
                if query:
                        logger.debug(f"Query: {query.group()}")
                else:
                        logger.debug("Query: None")
                return host.group()
        else:
                logger.error(f"Invalid URL: {url}")

# gets an HTTP Response using request module
def fetch(url, host, verify = True):
        headers = {"user-agent" : "SPyB/0.1", 
                   "host" : host,
                   "Cache-control": "max-age=180, public}"
        }
        try:
                response = requests.get(url, headers = headers, verify=verify)
                return response
        except requests.exceptions.SSLError as ssl_err:
                logger.critical(f"SSL Error occured: {ssl_err}")
                return "SSLERR"
        except requests.exceptions.RequestException as req_err:
                logger.error(f"Request Error occurred: {req_err}")
                return None
                
        
# Outputs log entries when receiveing an http status
def handleErrors(response):
        status = response.status_code
        reason = response.reason
        if 199 < status < 203 or 206 < status < 300:
                logger.info(f"Status: {status} {reason}")
        elif 202 < status < 207 or 299 < status < 400:
                logger.warn(f"Status: {status} {reason}")
        elif 399 < status < 600:
                logger.error(f"Status: {status} {reason}")
        return status

# decodes the body (if required) using the character set given in the response or utf-8
def decodeBody(response, previewLen):
        contentType = response.headers['Content-Type']
        logger.debug(f'Content-Type: {contentType}')
        charsetMatch = re.search(r'charset=([\w-]+)', contentType)
        charset = charsetMatch.group(1) if charsetMatch else "utf-8"
        logger.debug(charset)
        body = response.content

        try:
                decodeBody = body.decode(charset)
                logger.info(f"Body Decoded (First {previewLen} Characters): {decodeBody[:previewLen]}")
                return decodeBody
        except UnicodeDecodeError as dec_err:
                logger.error(f"Decoding failed: {dec_err}")
                return body.decode('ISO-8859-1', errors='replace')

# Outputs the HTML Body given in the HTTP Response
def fetcher(url):
        while True:
                host = getHost(url)
                if host == None:
                        return None
                else:
                        response = fetch(url, host)
                        if response == None:
                                return None
                        if response == "SSLERR":
                                # verify = tui.handleStdIn(tui.main_panel, "Do you want to load the site anyway? (y/N) [This is not recommended!] ")
                                verify = input("Do you want to load the site anyway? (y/N) [This is not recommended!] ")
                                if verify.lower() == "y":
                                        response = fetch(url, host, False)
                                else:
                                        return None
                        status = handleErrors(response)
                        if status > 399:
                                body = decodeBody(response, 250)
                                # retry = tui.handleStdIn(tui.main_panel, "Retry (y/N)? ")
                                retry = input("Retry? (y/N) ")
                                if retry.lower() == "y":
                                        continue
                                return body
                        else:
                                body = decodeBody(response, 750)
                                return body
if __name__ == "__main__":
        # fetcher(tui.handleStdIn(tui.address_bar, "URL "))
        parser.parse(fetcher(input("URL: ")))

