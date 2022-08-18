from logging import Logger
from typing import List, Optional
from pathlib import Path

from protostar.cli import Command
from protostar.protostar_exception import ProtostarExceptionSilent
from protostar.formatter.formatter import Formatter


class FormatCommand(Command):
    def __init__(self, project_root_path: Path, logger: Logger) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._logger = logger

    @property
    def example(self) -> Optional[str]:
        return "$ protostar format"

    @property
    def name(self) -> str:
        return "format"

    @property
    def description(self) -> str:
        return "Format cairo source code."

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="target",
                description=("Target to format, can be a file or a directory."),
                type="path",
                is_array=True,
                is_positional=True,
                default=["."],
            ),
            Command.Argument(
                name="check",
                description=(
                    "Run in 'check' mode. Exits with 0 if input is formatted correctly."
                    "Exits with 1 if formatting is required."
                ),
                type="bool",
                is_required=False,
                default=False,
                short_name="c",
            ),
            Command.Argument(
                name="verbose",
                description=("Log information about already formatted files as well."),
                type="bool",
                is_required=False,
                default=False,
            ),
            Command.Argument(
                name="ignore-broken",
                description=("Ignore broken files."),
                type="bool",
                is_required=False,
                default=False,
            ),
        ]

    async def run(self, args):
        try:
            any_unformatted_or_broken = self.format(
                args.target, args.check, args.verbose, args.ignore_broken
            )
        except BaseException as exc:
            self._logger.error("Command failed.")
            raise exc

        # set exit code to 1
        if any_unformatted_or_broken:
            raise ProtostarExceptionSilent(
                "Some files were unformatted, impossible to format or broken."
            )

    def format(
        self, targets: List[Path], check=False, verbose=False, ignore_broken=False
    ) -> int:

        formatter = Formatter(self._logger, self._project_root_path)
        any_unformatted_or_broken = formatter.format(
            targets, check, verbose, ignore_broken
        )

        return any_unformatted_or_broken
