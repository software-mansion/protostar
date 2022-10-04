from pathlib import Path

from protostar.commands.build import BuildCommand
from protostar.compiler import ProjectCompiler
from protostar.migrator.migrator_datetime_state import MigratorDateTimeState
from protostar.protostar_exception import ProtostarException


class ContractIdentificationException(ProtostarException):
    pass


def checked_contract_path(contract_path: Path) -> Path:
    if contract_path.is_file():
        return contract_path

    raise ContractIdentificationException(
        f"Couldn't find `{contract_path}` in the build directory."
    )


class MigratorContractIdentifierResolver:
    def __init__(
        self,
        project_compiler: ProjectCompiler,
        migrator_datetime_state: MigratorDateTimeState,
    ) -> None:
        self._project_compiler = project_compiler
        self._migrator_datetime_state = migrator_datetime_state

    def resolve(self, contract_identifier: str) -> Path:
        if "." in contract_identifier:
            contract_path = Path(contract_identifier)
            return checked_contract_path(contract_path)

        return self._get_built_contract_by_name(contract_identifier)

    def _get_built_contract_by_name(self, contract_name: str) -> Path:
        compilation_output_dir = self._project_compiler.get_compilation_output_dir(
            Path(BuildCommand.COMPILATION_OUTPUT_ARG.default)
        )
        compiled_contract_path = compilation_output_dir / f"{contract_name}.json"

        return checked_contract_path(compiled_contract_path)
