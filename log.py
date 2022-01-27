import sys
from colorama import Fore, Back, Style

def info(text: str) -> None:
    print(Back.GREEN + "[INFO]" + Style.RESET_ALL + " " + text)

def warning(text: str) -> None:
    print(Back.YELLOW + "[WARN]" + Style.RESET_ALL + " " + text)

def error(text: str) -> None:
    print(Back.RED + "[ERR]" + Style.RESET_ALL + " " + text)
    sys.exit(1)