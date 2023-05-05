from pathlib import Path

from protostar.configuration_file.configuration_file import ConfigurationFile


class ProjectCompiler:
    def __init__(
        self,
        project_root_path: Path,
        configuration_file: ConfigurationFile,
    ):
        self._project_root_path = project_root_path
        self.configuration_file = configuration_file

    def contract_path_from_contract_name(self, contract_name: str) -> Path:
        contract_paths = self.configuration_file.get_contract_source_paths(
            contract_name
        )

        assert len(contract_paths) == 1, (
            f"Multiple files found for contract {contract_name}, "
            f"only one file per contract is supported in cairo1!"
        )
        assert contract_paths, f"No contract paths found for {contract_name}!"

        return contract_paths[0]
