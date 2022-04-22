from pathlib import Path
from typing import List

from src.core.application import Application
from src.core.command import Command


class ReferenceDocsGenerator:
    @staticmethod
    def save_to_markdown_file(filepath: Path, content: str):
        with open(filepath, "w", encoding="utf_8") as file:
            file.write(content)

    def __init__(self, app: Application) -> None:
        self.app = app

    def generate_cli_reference_markdown(self) -> str:
        result: List[str] = ["# CLI Reference"]

        if len(self.app.root_args) > 0:
            result += ["## Generic flags"]
            result += self._generate_args_markdown(self.app.root_args)

        if len(self.app.commands) > 0:
            result += ["## Commands"]
            for command in self.app.commands:
                result.append(f"### `{command.name}`")
                if command.example:
                    result.append(f"```shell\n{command.example}\n```")
                result.append(f"{command.description}")

                result += self._generate_args_markdown(command.arguments)

        return "\n".join(result)

    # pylint: disable=no-self-use
    def _generate_args_markdown(self, arguments: List[Command.Argument]) -> List[str]:
        result: List[str] = []

        for arg in arguments:
            name = arg.name if arg.is_required else f"--{arg.name}"
            arg_type = arg.type if arg.type != "bool" else None
            arg_type = f"{arg_type}[]" if arg.is_array else arg_type
            arg_type = f" {arg_type.upper()}" if arg_type else ""
            result.append(f"#### `{name}{arg_type or ''}`")
            if arg.example:
                result.append(f"```\n{arg.example}\n```")
            result.append(f"{arg.description}")

        return result
