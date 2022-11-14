import json
import sys
from abc import ABC, abstractmethod

from .log_color_provider import LogColorProvider


class Message(ABC):
    @abstractmethod
    def format_human(self, fmt: LogColorProvider) -> str:
        ...


class StructuredMessage(Message, ABC):
    @abstractmethod
    def format_dict(self) -> dict:
        ...


class Messenger(ABC):
    @abstractmethod
    def __call__(self, message: Message):
        ...


class HumanMessenger(Messenger):
    def __init__(self, log_color_provider: LogColorProvider):
        self._log_color_provider = log_color_provider

    def __call__(self, message: Message):
        human_message = message.format_human(fmt=self._log_color_provider)
        print(human_message)


class JsonMessenger(Messenger):
    def __call__(self, message: Message):
        if not isinstance(message, StructuredMessage):
            raise NotImplementedError(
                f"JSON output is not supported for messages of type {type(message).__name__}."
            )

        dictionary = message.format_dict()
        json.dump(dictionary, sys.stdout, allow_nan=False, separators=(",", ":"))
        sys.stdout.write("\n")
        sys.stdout.flush()
