import time
from logging import Formatter, LogRecord

from protostar.io.log_color_provider import LogColorProvider


class StandardLogFormatter(Formatter):
    def __init__(self, log_color_provider: LogColorProvider) -> None:
        super().__init__()
        self._log_color_provider = log_color_provider

    def get_level_color(self, level: str) -> str:
        mapping = {
            "DEBUG": self._log_color_provider.get_color("MAGENTA"),
            "INFO": self._log_color_provider.get_color("CYAN"),
            "WARNING": self._log_color_provider.get_color("YELLOW"),
            "ERROR": self._log_color_provider.get_color("RED"),
        }

        if level in mapping:
            return mapping[level]
        return self._log_color_provider.get_color("RESET")

    def formatMessage(self, record: LogRecord) -> str:
        color_reset = self._log_color_provider.get_color("RESET")
        message_blocks = []
        message_blocks.append(
            self._log_color_provider.get_color("GRAY")
            + time.strftime("%H:%M:%S")
            + color_reset
        )
        if record.levelname == "DEBUG" and record.name is not None:
            message_blocks.append(
                self._log_color_provider.get_color("GRAY") + record.name + color_reset
            )

        message_blocks.append(
            f"[{self.get_level_color(record.levelname)}{record.levelname}{color_reset}]"
        )
        message_blocks.append(f"{record.message}")

        return " ".join(message_blocks)
