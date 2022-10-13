from pathlib import Path
from typing import List

from protostar.cli.argument import Argument
from protostar.cli.cli_app import CLIApp


class ReferenceDocsGenerator:
    @staticmethod
    def save_to_markdown_file(filepath: Path, content: str):
        with open(filepath, "w", encoding="utf_8") as file:
            file.write(content)

    def __init__(self, cli_app: CLIApp) -> None:
        self.cli_app = cli_app

    def generate_cli_reference_markdown(self) -> str:
        result: List[str] = ["# CLI Reference"]

        if len(self.cli_app.root_args) > 0:
            result += ["## Common flags"]
            result += self._generate_args_markdown(self.cli_app.root_args)

        if len(self.cli_app.commands) > 0:
            # pyright: reportUnknownLambdaType=false
            sorted_commands = sorted(self.cli_app.commands, key=(lambda c: c.name))
            result += ["## Commands"]
            for command in sorted_commands:
                result.append(f"### `{command.name}`")
                if command.example:
                    result.append(f"```shell\n{command.example}\n```")
                result.append(f"{command.description}")

                result += self._generate_args_markdown(command.arguments)

        return "\n".join(result)

    # pylint: disable=no-self-use
    def _generate_args_markdown(self, arguments: List[Argument]) -> List[str]:
        result: List[str] = []

        sorted_arguments = sorted(
            arguments, key=(lambda a: (not a.is_positional, a.name))
        )

        for arg in sorted_arguments:
            name = arg.name if arg.is_positional else f"--{arg.name}"
            arg_type = arg.type if arg.type != "bool" else None
            arg_type = "string" if arg.type == "str" else arg_type
            arg_type = f"{arg_type}[]" if arg.is_array else arg_type
            arg_type = f" {arg_type.upper()}" if arg_type else ""
            arg_type = f"{arg_type}={arg.default}" if arg.default else arg_type
            short_name = f"`-{arg.short_name}` " if arg.short_name else ""
            result.append(f"#### {short_name}`{name}{arg_type or ''}`")
            if arg.example:
                result.append(f"```\n{arg.example}\n```")
            if arg.is_required:
                result.append("Required.\n")
            result.append(f"{arg.description}")

        return result
