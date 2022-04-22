from typing import Any, List, Mapping

from src.core.command import Command


class Application:
    def __init__(
        self, commands: List[Command], root_args: List[Command.Argument]
    ) -> None:
        self.commands = commands
        self.root_args = root_args

        self._command_mapping: Mapping[str, Command] = {}
        for command in commands:
            self._command_mapping[command.name] = command

    async def run(self, args: Any):
        command = self._command_mapping[args.command]
        await command.run(args)
