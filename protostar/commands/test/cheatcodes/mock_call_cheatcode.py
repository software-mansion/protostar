from collections.abc import Mapping
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from starkware.starknet.public.abi import get_selector_from_name

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.starkware.types import AddressType
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.utils.data_transformer_facade import DataTransformerFacade


class MockCallCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        data_transformer: DataTransformerFacade,
    ):
        super().__init__(syscall_dependencies)
        self._data_transformer = data_transformer

    @property
    def name(self) -> str:
        return "mock_call"

    def build(self) -> Callable[..., Any]:
        return self.mock_call

    def mock_call(
        self,
        contract_address: int,
        fn_name: str,
        ret_data: Union[
            List[int],
            Dict[
                DataTransformerFacade.ArgumentName,
                DataTransformerFacade.SupportedType,
            ],
        ],
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
                self.name,
                f"'{fn_name}' in the contract with address {contract_address} has been already mocked",
            )
        self.state.mocked_calls_map[contract_address][selector] = ret_data

        def clear_mock():
            if contract_address not in self.state.mocked_calls_map:
                raise CheatcodeException(
                    self.name,
                    f"Contract {contract_address} doesn't have mocked selectors.",
                )
            if selector not in self.state.mocked_calls_map[contract_address]:
                raise CheatcodeException(
                    self.name,
                    f"Couldn't find mocked selector {selector} for an address {contract_address}.",
                )
            del self.state.mocked_calls_map[contract_address][selector]

        return clear_mock

    def _transform_ret_data_to_cairo_format(
        self,
        contract_address: int,
        fn_name: str,
        ret_data: Dict[
            DataTransformerFacade.ArgumentName,
            DataTransformerFacade.SupportedType,
        ],
    ) -> List[int]:
        contract_path = self.get_contract_path_from_contract_address(contract_address)
        if contract_path is None:
            raise CheatcodeException(
                self.name,
                (
                    "Couldn't map the `contract_address` to the `contract_path`.\n"
                    f"Is the `contract_address` ({contract_address}) valid?\n"
                ),
            )

        return self._data_transformer.build_from_python_transformer(
            contract_path, fn_name, "outputs"
        )(ret_data)

    def get_contract_path_from_contract_address(
        self, contract_address: AddressType
    ) -> Optional[Path]:
        if contract_address in self.state.contract_address_to_class_hash_map:
            class_hash = self.state.contract_address_to_class_hash_map[contract_address]
            if class_hash in self.state.class_hash_to_contract_path_map:
                return self.state.class_hash_to_contract_path_map[class_hash]

        return None
