import time
from logging import Formatter, LogRecord

from colorama import Fore, Style


def get_level_color(level: str) -> str:
    if level == "DEBUG":
        return Fore.LIGHTMAGENTA_EX
    if level == "INFO":
        return Fore.BLUE
    if level == "WARNING":
        return Fore.YELLOW
    if level == "ERROR":
        return Fore.RED
    return ""


class StandardLogFormatter(Formatter):
    def formatMessage(self, record: LogRecord) -> str:
        message_blocks = []
        message_blocks.append(
            f"{Fore.LIGHTBLACK_EX}{time.strftime('%H:%M:%S')}{Style.RESET_ALL}"
        )
        if record.levelname == "DEBUG" and record.name is not None:
            message_blocks.append(f"{Fore.LIGHTBLACK_EX}{record.name}{Style.RESET_ALL}")

        message_blocks.append(
            f"[{get_level_color(record.levelname)}{record.levelname}{Style.RESET_ALL}]"
        )
        message_blocks.append(f"{record.message}")

        return " ".join(message_blocks)
