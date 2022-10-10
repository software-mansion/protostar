from typing import Any, Optional

import pytest
from starkware.starknet.public.abi import AbiType
from starkware.starknet.services.api.contract_class import ContractClass


@pytest.fixture(name="abi")
def abi_fixture() -> Optional[AbiType]:
    return None


@pytest.fixture(name="compiled_contract")
def compiled_contract_fixture(abi: Optional[AbiType]):
    _abi = abi

    class CompiledContract:
        abi = _abi

        class Schema:
            def dump(self, _contract: Any):
                return ""

    return CompiledContract()
