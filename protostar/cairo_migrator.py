from logging import Logger
from pathlib import Path
from typing import List

from starkware.cairo.lang.compiler.ast.formatting_utils import FormattingError
from starkware.cairo.lang.migrators.migrator import parse_and_migrate, MIGRATE_FUNCTIONS

from protostar.protostar_exception import ProtostarException


class CairoMigrator:
    def __init__(self, logger: Logger, single_return_functions: bool = True):
        self._single_return_functions = single_return_functions
        self._logger = logger
        self._formatted_files = []

    def format_file(self, filepath: Path) -> str:
        file_contents = filepath.read_text("utf-8")
        if not file_contents.endswith('\n'):
            file_contents += '\n'
        ast = parse_and_migrate(
            code=file_contents,
            filename=str(filepath),
            migrate_syntax=True,
            single_return_functions=MIGRATE_FUNCTIONS
            if self._single_return_functions
            else None,
        )
        new_content = ast.format()
        return new_content

    def save(self):
        for filepath, new_content in self._formatted_files:
            with open(filepath, "w", encoding="utf-8") as file:
                self._logger.info(f"Writing {filepath}")
                file.write(new_content)

    def run(self, file_paths: List[Path]):
        try:
            self._formatted_files = [
                (filepath, self.format_file(filepath))
                for filepath in file_paths
            ]
        except FormattingError as f_err:
            raise ProtostarException(f"Migrate exception:\n{f_err}") from f_err
