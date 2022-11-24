import json
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import ContextManager, Callable, Generator

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

    @abstractmethod
    def activity(self, message_template: Message) -> ContextManager:
        ...


class HumanMessenger(Messenger):
    def __init__(
        self,
        log_color_provider: LogColorProvider,
        activity_indicator: Callable[[str], ContextManager],
    ):
        self._fmt = log_color_provider
        self._activity_indicator = activity_indicator

    def __call__(self, message: Message):
        human_message = message.format_human(fmt=self._fmt)
        print(human_message)

    @contextmanager
    def activity(self, message_template: Message) -> Generator[None, None, None]:
        message = message_template.format_human(fmt=self._fmt)
        try:
            with self._activity_indicator(self._fmt.colorize("GRAY", message)):
                yield

            print(message, self._fmt.colorize("GREEN", "OK"))
        except BaseException:
            print(message, self._fmt.colorize("RED", "FAILED"))
            raise


class JsonMessenger(Messenger):
    def __call__(self, message: Message):
        if not isinstance(message, StructuredMessage):
            raise NotImplementedError(
                f"JSON output is not supported for messages of type {type(message).__name__}."
            )

        obj = message.format_dict()
        self._print(obj)

    @contextmanager
    def activity(self, message_template: Message) -> Generator[None, None, None]:
        # Passthrough, we don't want indicators in JSON output.
        yield

    @staticmethod
    def _print(obj: dict):
        json.dump(obj, sys.stdout, allow_nan=False, separators=(",", ":"))
        sys.stdout.write("\n")
        sys.stdout.flush()
