from typing import Callable, TYPE_CHECKING

from starkware.starknet.public.abi import get_selector_from_name

from protostar.starknet.address import Address
from protostar.starknet.data_transformer import (
    CairoOrPythonData,
    transform_calldata_to_cairo_data,
)
from protostar.protostar_exception import ProtostarException


if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatable_cached_state import CheatableCachedState


class MocksCairoCheater:
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.cheatable_state = cheatable_state

    async def mock_call(
        self,
        contract_address: Address,
        function_name: str,
        ret_data: CairoOrPythonData,
    ) -> Callable:
        ret_data_cairo = await transform_calldata_to_cairo_data(
            contract_class=await self.cheatable_state.get_contract_class_by_address(
                contract_address=contract_address
            ),
            function_name=function_name,
            calldata=ret_data,
        )

        function_selector = get_selector_from_name(func_name=function_name)
        if self.cheatable_state.mocked_calls_map.get(contract_address) is None:
            self.cheatable_state.mocked_calls_map[contract_address] = {}
        elif (
            function_selector in self.cheatable_state.mocked_calls_map[contract_address]
        ):
            raise ProtostarException(
                f"'{function_name}' in the contract with address {contract_address} has been already mocked",
            )
        self.cheatable_state.mocked_calls_map[contract_address][
            function_selector
        ] = ret_data_cairo

        def stop_mock():
            if contract_address not in self.cheatable_state.mocked_calls_map:
                raise ProtostarException(
                    f"Contract {contract_address} doesn't have mocked selectors.",
                )
            if (
                function_selector
                not in self.cheatable_state.mocked_calls_map[contract_address]
            ):
                raise ProtostarException(
                    f"Couldn't find mocked selector {function_selector} for an address {contract_address}.",
                )
            del self.cheatable_state.mocked_calls_map[contract_address][
                function_selector
            ]

        return stop_mock
