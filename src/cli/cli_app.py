from typing import Any, List, Optional

from src.cli.command import Command


class CLIApp:
    """
    Defines CLI structure and is responsible for executing the proper command.
    """

    def __init__(
        self,
        commands: Optional[List[Command]] = None,
        root_args: Optional[List[Command.Argument]] = None,
    ) -> None:
        self.commands = commands or []
        self.root_args = root_args or []
        self._command_mapping = {command.name: command for command in self.commands}

    async def run(self, args: Any) -> bool:
        if not args.command:
            return False

        command = self._command_mapping[args.command]
        await command.run(args)
        return True
