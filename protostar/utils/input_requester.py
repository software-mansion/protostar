from protostar.utils.log_color_provider import LogColorProvider


class InputRequester:
    def __init__(self, log_color_provider: LogColorProvider) -> None:
        self._log_color_provider = log_color_provider

    def request_input(self, message: str):
        return input(self._log_color_provider.colorize("CYAN", f"{message}: "))

    def request_input_again(self, message: str):
        return input(self._log_color_provider.colorize("RED", f"{message}: "))

    def confirm(self, message: str) -> bool:
        res = self.request_input(message + " [y/n]")
        while res not in ("y", "n"):
            res = self.request_input("Please provide one of the [y/n]")
        return res == "y"
