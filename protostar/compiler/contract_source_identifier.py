from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from protostar.protostar_exception import ProtostarException
from protostar.self import ContractName


@dataclass(eq=True, frozen=True, unsafe_hash=True)
class ContractSourceIdentifier:
    @classmethod
    def from_contract_path(cls, path: Path):
        check_contract_path_existence(path)

        return cls(
            name=path.stem,
            paths=[path],
        )

    @classmethod
    def create(cls, name: ContractName, paths: list[Path]):
        for contract_path in paths:
            check_contract_path_existence(contract_path)

        return cls(
            name=name,
            paths=paths,
        )

    name: ContractName
    paths: list[Path]


class ContractNamesProviderProtocol(Protocol):
    def get_contract_names(self) -> list[ContractName]:
        ...

    def get_contract_source_paths(self, contract_name: ContractName) -> list[Path]:
        ...


def create_contract_source_identifier_factory(
    contract_names_provider: ContractNamesProviderProtocol,
):
    def create_contract_source_identifier(input_data: str):
        if input_data.endswith(".cairo"):
            return ContractSourceIdentifier.from_contract_path(Path(input_data))
        contract_name = input_data
        contract_names = contract_names_provider.get_contract_names()
        if contract_name not in contract_names:
            raise InvalidContractSourceIdentifierException(
                f"Unknown contract: {contract_name}"
            )

        return ContractSourceIdentifier.create(
            name=contract_name,
            paths=contract_names_provider.get_contract_source_paths(contract_name),
        )

    return create_contract_source_identifier


def check_contract_path_existence(contract_path: Path):
    if not contract_path.exists():
        raise InvalidContractSourceIdentifierException(
            f"The following contract doesn't exist: {contract_path}"
        )


class InvalidContractSourceIdentifierException(ProtostarException):
    pass
