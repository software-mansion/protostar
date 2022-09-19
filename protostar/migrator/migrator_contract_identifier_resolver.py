from pathlib import Path

from protostar.compiler import CompiledContractWriter, ProjectCompiler
from protostar.migrator.migrator_datetime_state import MigratorDateTimeState


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
            return Path(contract_identifier)
        return self._compile_contract_by_contract_name(contract_identifier)

    def _compile_contract_by_contract_name(self, contract_name: str) -> Path:
        contract_class = self._project_compiler.compile_contract_from_contract_name(
            contract_name
        )
        output_file_path = (
            CompiledContractWriter(contract=contract_class, contract_name=contract_name)
            .save(
                output_dir=self._migrator_datetime_state.get_compilation_output_path()
            )
            .compiled_contract_path
        )
        return output_file_path
