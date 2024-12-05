'''
    This Script is part of SPyB.
    Copyright (C) 2024  Stepan Khristolyubov

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


import requests
import re
import logging
import json
import socket
import colorama
from colorama import Fore, Back
import tui
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

def fetch(url, host, verify = True):
        headers = {"user-agent" : "SPyB/0.1", 
                   "host" : host,
                   "Cache-control": "max-age=180, public}"
        }
        response = requests.get(url, headers = headers)
        logger.info(response)

        return response

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
        contentEncoding = response.headers['Content-Encoding']
        logger.debug(f'Content-Type: {contentType}')
        logger.debug(f'Content-Encoding: {contentEncoding}')
        charsetMatch = re.search(r'charset=([\w-]+)', contentType)
        charset = charsetMatch.group(1) if charsetMatch else "utf-8"
        logger.debug(charset)
        body = response.content

        try:
                decodeBody = body.decode(charset)
                logger.info(f"Body Decoded (First  Characters): {decodeBody[:previewLen]}")
                return decodeBody
        except UnicodeDecodeError as dec_err:
                logger.error(Fore.RED + f"Decoding failed: {dec_err}" + Fore.RESET)
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
                                verify = tui.handleStdIn(tui.address_bar, "Do you want to load the site anyway? (y/N) " + Fore.RED + "[This is not recommended!] " + Fore.RESET)
                                if verify.lower() == "y":
                                        response = fetch(url, host, False)
                                else:
                                        return None
                        status = handleErrors(response)
                        if status > 399:
                                body = decodeBody(response, 250)
                                retry = tui.handleStdIn(tui.address_bar, "Retry (y/N)? ")
                                if retry.lower() == "y":
                                        continue
                                return body
                        else:
                                body = decodeBody(response, 750)
                                return body
if __name__ == "__main__":
        fetcher(tui.handleStdIn(tui.address_bar, "URL "))

