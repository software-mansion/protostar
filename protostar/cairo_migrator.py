from pathlib import Path
from typing import List, Tuple

from starkware.cairo.lang.compiler.ast.formatting_utils import FormattingError
from starkware.cairo.lang.migrators.migrator import parse_and_migrate, MIGRATE_FUNCTIONS

from protostar.protostar_exception import ProtostarException


class Cairo010Migrator:
    @staticmethod
    def _format_file(filepath: Path) -> str:
        file_contents = filepath.read_text("utf-8")
        if not file_contents.endswith('\n'):
            file_contents += '\n'
        ast = parse_and_migrate(
            code=file_contents,
            filename=str(filepath),
            migrate_syntax=True,
            single_return_functions=MIGRATE_FUNCTIONS,
        )
        new_content = ast.format()
        return new_content

    @staticmethod
    def run(file_paths: List[Path]) -> List[Tuple[Path, str]]:
        try:
            return [
                (filepath, Cairo010Migrator._format_file(filepath))
                for filepath in file_paths
            ]
        except FormattingError as f_err:
            raise ProtostarException(f"Migrate exception:\n{f_err}") from f_err
