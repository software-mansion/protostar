from pathlib import Path

import pytest
from starkware.starknet.services.api.contract_class import ContractClass

from .compiled_contract_writer import CompiledContractWriter


@pytest.mark.parametrize("abi", [None])
def test_saving_abi_file_when_contract_does_not_have_entry_points(
    tmp_path: Path,
    compiled_contract: ContractClass,
):
    writer = CompiledContractWriter(contract=compiled_contract, contract_name="foo")

    result = writer.save(tmp_path)

    assert (tmp_path / result.compiled_contract_path_abi).exists()
