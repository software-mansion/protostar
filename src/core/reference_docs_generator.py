from typing import List

from src.core.application import Application
from src.core.command import AbstractCommand


class ReferenceDocsGenerator:
    def __init__(self, app: Application) -> None:
        self.app = app

    def generate_cli_reference_markdown(self) -> str:
        result: List[str] = []

        result += self._generate_args_markdown(self.app.root_args)

        for command in self.app.commands:
            result.append(f"## `{command.name}`")
            if command.example:
                result.append(f"```shell\n{command.example}\n```")
            result.append(f"{command.description}")

            result += self._generate_args_markdown(command.arguments)

        return "\n".join(result)

    # pylint: disable=no-self-use
    def _generate_args_markdown(
        self, arguments: List[AbstractCommand.Argument]
    ) -> List[str]:
        result: List[str] = []

        for arg in arguments:
            result.append(f"### `{arg.name}`")
            if arg.example:
                result.append(f"```\n{arg.example}\n```")
            result.append(f"{arg.description}")

        return result
