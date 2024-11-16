import requests
import re
import logging
import socket
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
                logger.debug(f"Host IP: {socket.gethostbyname(host.group())}")
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

def fetch(url, host):
        headers = {"user-agent" : "StupidPythonBrowser/0.1", 
                   "host" : host
        }
        response = requests.get(url, headers = headers)
        logger.info(response)

        return response
        
def decodeBody(response):
        contentType = response.headers['Content-Type']
        contentEncoding = response.headers['Content-Encoding']
        logger.debug(f'Content-Type: {contentType}')
        logger.debug(f'Content-Encoding: {contentEncoding}')
        charsetMatch = re.search(r'charset=([\w-]+)', contentType)
        charset = charsetMatch.group(1) if charsetMatch else "utf-8"
        logger.debug(charset)
        body = response.content

        try:
                decodeBody = body.decode(charset)
                logger.info(f"Body Decoded (First 500 Characters): {decodeBody[:500]}")
                return decodeBody
        except UnicodeDecodeError as e:
                logger.error(f"Decoding failed: {e}")
                return body.decode('ISO-8859-1', errors='replace')


url = input("Url: ")
host = getHost(url)
response = fetch(url, host)
decodeBody(response)