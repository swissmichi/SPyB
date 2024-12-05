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
import fetcher
import json
from html.parser import HTMLParser
import colorama
from colorama import Fore, Back
colorama.just_fix_windows_console()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,  format="%(asctime)s - %(levelname)s - %(message)s")

class parse(HTMLParser):
        def __init__(self):
                super().__init__()
                self.reset()
        
 
