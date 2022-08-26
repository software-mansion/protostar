from collections.abc import Mapping
from typing import Any, Callable, List, Optional

from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi import get_selector_from_name

from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.types import AddressType
from protostar.utils.data_transformer import (
    CairoOrPythonData,
    PythonData,
    from_python_transformer,
)


class MockCallCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "mock_call"

    def build(self) -> Callable[..., Any]:
        return self.mock_call

    def mock_call(
        self,
        contract_address: int,
        fn_name: str,
        ret_data: CairoOrPythonData,
    ):
        selector = get_selector_from_name(fn_name)
        if isinstance(ret_data, Mapping):
            ret_data = self._transform_ret_data_to_cairo_format(
                contract_address, fn_name, ret_data
            )

        if contract_address not in self.state.mocked_calls_map:
            self.state.mocked_calls_map[contract_address] = {}

        if selector in self.state.mocked_calls_map[contract_address]:
            raise CheatcodeException(
                self,
                f"'{fn_name}' in the contract with address {contract_address} has been already mocked",
            )
        self.state.mocked_calls_map[contract_address][selector] = ret_data

        def clear_mock():
            if contract_address not in self.state.mocked_calls_map:
                raise CheatcodeException(
                    self,
                    f"Contract {contract_address} doesn't have mocked selectors.",
                )
            if selector not in self.state.mocked_calls_map[contract_address]:
                raise CheatcodeException(
                    self,
                    f"Couldn't find mocked selector {selector} for an address {contract_address}.",
                )
            del self.state.mocked_calls_map[contract_address][selector]

        return clear_mock

    def _transform_ret_data_to_cairo_format(
        self,
        contract_address: int,
        fn_name: str,
        ret_data: PythonData,
    ) -> List[int]:
        contract_abi = self.get_contract_abi_from_contract_address(contract_address)
        if contract_abi is None:
            raise CheatcodeException(
                self,
                (
                    "Couldn't map the `contract_address` to the `contract_abi`.\n"
                    f"Is the `contract_address` ({contract_address}) valid?\n"
                ),
            )

        transformer = from_python_transformer(contract_abi, fn_name, "outputs")
        return transformer(ret_data)

    def get_contract_abi_from_contract_address(
        self, contract_address: AddressType
    ) -> Optional[AbiType]:
        if contract_address in self.state.contract_address_to_class_hash_map:
            class_hash = self.state.contract_address_to_class_hash_map[contract_address]
            if class_hash in self.state.class_hash_to_contract_abi_map:
                return self.state.class_hash_to_contract_abi_map[class_hash]

        return None
