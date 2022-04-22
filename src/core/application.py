from typing import List

from src.core.command import AbstractCommand


class Application:
    def __init__(
        self, commands: List[AbstractCommand], root_args: List[AbstractCommand.Argument]
    ) -> None:
        self.commands = commands
        self.root_args = root_args
