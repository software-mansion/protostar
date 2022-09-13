from pathlib import Path
from typing import Any

import pytest
from starkware.starknet.public.abi import AbiType
from starkware.starknet.services.api.contract_class import ContractClass

from .compiled_contract_reader import CompiledContractReader
from .compiled_contract_writer import CompiledContractWriter


@pytest.fixture(name="abi")
def abi_fixture() -> AbiType:
    return [{"foo": "bar"}]


@pytest.fixture(name="compiled_contract")
def compiled_contract_fixture(abi: AbiType):
    _abi = abi

    class CompiledContract:
        abi = _abi

        class Schema:
            def dump(self, _contract: Any):
                return ""

    return CompiledContract()


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(
    compiled_contract: ContractClass, tmp_path: Path
) -> Path:
    paths_data = CompiledContractWriter(
        contract=compiled_contract, contract_name="CONTRACT_NAME"
    ).save(output_dir=tmp_path / "out")
    assert paths_data.compiled_contract_path_abi is not None
    return paths_data.compiled_contract_path


def test_loading_abi_from_compiled_contract_path(
    compiled_contract_path: Path, abi: AbiType
):
    ccr = CompiledContractReader()

    result = ccr.load_abi_from_contract_path(compiled_contract_path)

    assert result == abi
