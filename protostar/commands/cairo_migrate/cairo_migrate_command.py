from logging import Logger
from pathlib import Path
from typing import Any, List, Optional

from protostar.cairo_migrator import CairoMigrator
from protostar.cli import Command
from protostar.cli.misc import resolve_cairo_targets


class CairoMigrateCommand(Command):
    def __init__(self, script_root: Path, logger: Logger):
        super().__init__()
        self._script_root = script_root
        self._logger = logger

    @property
    def name(self) -> str:
        return "cairo-migrate"

    @property
    def description(self) -> str:
        return "Migrates the project sources to be compatible with cairo 0.10"

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="targets",
                description="Targets to migrate (a target can be a file or directory)",
                type="str",
                is_array=True,
                is_positional=True,
                default=resolve_cairo_targets([Path()]),
            )
        ]

    async def run(self, args: Any):
        migrator = CairoMigrator(
            logger=self._logger,
            single_return_functions=True
        )
        migrator.run(file_paths=resolve_cairo_targets(args.targets))
        migrator.save()
