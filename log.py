"""
EarnApp-Earnings-Watcher - A program to monitor your EarnApp Earnings and send data to a discord webhook
Copyright (C) 2022  SWM Tech Industries

This file is part of EarnApp-Earnings-Watcher.

EarnApp-Earnings-Watcher is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

EarnApp-Earnings-Watcher is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EarnApp-Earnings-Watcher. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
from colorama import Fore, Back, Style

def info(text: str) -> None:
    print(Back.GREEN + "[INFO]" + Style.RESET_ALL + " " + text)

def warning(text: str) -> None:
    print(Back.YELLOW + "[WARN]" + Style.RESET_ALL + " " + text)

def error(text: str) -> None:
    print(Back.RED + "[ERR]" + Style.RESET_ALL + " " + text)
    sys.exit(1)