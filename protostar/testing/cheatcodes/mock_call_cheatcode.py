from collections.abc import Mapping
from typing import Any, Callable, List, Optional

from starkware.starknet.public.abi import AbiType, get_selector_from_name

from protostar.starknet import RawAddress, Address, Cheatcode, CheatcodeException
from protostar.starknet.data_transformer import (
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
        contract_address: RawAddress,
        fn_name: str,
        ret_data: CairoOrPythonData,
    ):
        address = Address.from_user_input(contract_address)
        selector = get_selector_from_name(fn_name)
        if isinstance(ret_data, Mapping):
            ret_data = self._transform_ret_data_to_cairo_format(
                Address.from_user_input(contract_address), fn_name, ret_data
            )

        if contract_address not in self.cheatable_state.mocked_calls_map:
            self.cheatable_state.mocked_calls_map[address] = {}

        if selector in self.cheatable_state.mocked_calls_map[address]:
            raise CheatcodeException(
                self,
                f"'{fn_name}' in the contract with address {contract_address} has been already mocked",
            )
        self.cheatable_state.mocked_calls_map[address][selector] = ret_data

        def clear_mock():
            if contract_address not in self.cheatable_state.mocked_calls_map:
                raise CheatcodeException(
                    self,
                    f"Contract {contract_address} doesn't have mocked selectors.",
                )
            if selector not in self.cheatable_state.mocked_calls_map[contract_address]:
                raise CheatcodeException(
                    self,
                    f"Couldn't find mocked selector {selector} for an address {contract_address}.",
                )
            del self.cheatable_state.mocked_calls_map[contract_address][selector]

        return clear_mock

    def _transform_ret_data_to_cairo_format(
        self,
        contract_address: Address,
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
        self, contract_address: Address
    ) -> Optional[AbiType]:
        if contract_address in self.cheatable_state.contract_address_to_class_hash_map:
            class_hash = self.cheatable_state.contract_address_to_class_hash_map[
                contract_address
            ]
            if class_hash in self.cheatable_state.class_hash_to_contract_abi_map:
                return self.cheatable_state.class_hash_to_contract_abi_map[class_hash]

        return None
