import requests
import re
import logging
import socket
import colorama
from colorama import Fore, Back
colorama.just_fix_windows_console()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,  format="%(asctime)s - %(levelname)s - %(message)s")

def getHost(url):
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
                        logger.error(Fore.RED + f"The host {host.group()} doesn't appear to exist, or may not be connected to the internet." + Fore.RESET)
                        return None
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
                logger.error(Fore.RED + f"Invalid URL: {url}" + Fore.RESET)
                return None

def fetch(url, host, verify = True):
        headers = {"user-agent" : "SPyB/0.1", 
                   "host" : host
        }
        try:
                response = requests.get(url, headers = headers, verify=verify)
                return response
        except requests.exceptions.SSLError as ssl_err:
                logger.critical(Back.RED + f"SSL Error occured: {ssl_err}" + Back.RESET)
                return "SSLERR"
        except requests.exceptions.RequestException as req_err:
                logger.error(Fore.RED + f"Request Error occurred: {req_err}" + Fore.RESET)
                return None
        
        

def handleErrors(response):
        status = response.status_code
        reason = response.reason
        if 199 < status < 203 or 206 < status < 300:
                logger.info(f"Status: {status} {reason}")
        elif 202 < status < 207 or 299 < status < 400:
                logger.warn(Fore.YELLOW + f"Status: {status} {reason}" + Fore.RESET)
        elif 399 < status < 600:
                logger.error(Fore.RED + f"Status: {status} {reason}" + Fore.RESET)
        return status
       
def decodeBody(response, previewLen):
        contentType = response.headers['Content-Type']
        logger.debug(f'Content-Type: {contentType}')
        charsetMatch = re.search(r'charset=([\w-]+)', contentType)
        charset = charsetMatch.group(1) if charsetMatch else "utf-8"
        logger.debug(f"CharSet: {charset}")
        body = response.content

        try:
                decodeBody = body.decode(charset)
                logger.info(f"Body Decoded (First {previewLen} Characters): {decodeBody[:previewLen]}")
                return decodeBody
        except UnicodeDecodeError as e:
                logger.error(Fore.RED + f"Decoding failed: {e}" + Fore.RESET)
                return body.decode('ISO-8859-1', errors='replace')

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
                                verify = input("Do you want to load the site anyway? (y/N) " + Fore.RED + "[This is not recommended!] " + Fore.RESET)
                                if verify.lower() == "y":
                                        response = fetch(url, host, False)
                                else:
                                        return None
                        status = handleErrors(response)
                        if status > 399:
                                body = decodeBody(response, 250)
                                retry = input("Retry (y/N)? ")
                                if retry.lower() == "y":
                                        continue
                                return body
                        else:
                                body = decodeBody(response, 750)
                                return body

fetcher(input("URL: "))
