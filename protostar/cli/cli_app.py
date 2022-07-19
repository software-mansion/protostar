from typing import Any, List, Optional

from protostar.cli.command import Command


class CLIApp:
    """
    Defines CLI structure and is responsible for executing the proper command.
    """

    class CommandNotFoundError(Exception):
        pass

    def __init__(
        self,
        commands: Optional[List[Command]] = None,
        root_args: Optional[List[Command.Argument]] = None,
    ) -> None:
        self.commands = commands or []
        self.root_args = root_args or []
        self._command_mapping = {command.name: command for command in self.commands}

    async def run(self, args: Any) -> None:
        if not args or not args.command or args.command not in self._command_mapping:
            raise CLIApp.CommandNotFoundError()

        command = self._command_mapping[args.command]
        await command.run(args)
