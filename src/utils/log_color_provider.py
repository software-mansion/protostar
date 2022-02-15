from colorama import Fore
from typing_extensions import Literal


class LogColorProvider:
    def __init__(self):
        self.is_ci_mode = False

    # pylint: disable=too-many-return-statements
    def get_color(
        self,
        color_name: Literal[
            "RED", "YELLOW", "GREEN", "CYAN", "GRAY", "MAGENTA", "RESET", "BLUE"
        ],
    ) -> str:
        if self.is_ci_mode:
            return ""

        if color_name == "RED":
            return Fore.RED
        if color_name == "YELLOW":
            return Fore.YELLOW
        if color_name == "GREEN":
            return Fore.GREEN
        if color_name == "CYAN":
            return Fore.CYAN
        if color_name == "BLUE":
            return Fore.BLUE
        if color_name == "GRAY":
            return Fore.LIGHTBLACK_EX
        if color_name == "MAGENTA":
            return Fore.LIGHTMAGENTA_EX
        if color_name == "RESET":
            return Fore.RESET
        return ""


log_color_provider = LogColorProvider()
