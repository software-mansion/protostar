import os
from typing import Optional, Callable

from starkware.starknet.public.abi import get_selector_from_name

from protostar.starknet.cheater import CheaterException
from protostar.starknet.address import Address
from protostar.starknet.data_transformer import (
    CairoOrPythonData,
    transform_calldata_to_cairo_data,
)
from protostar.starknet.types import SelectorType

from .stateful import StatefulCheater


def assert_no_expected_calls(
    expected_calls: dict[Address, list[tuple[SelectorType, CairoOrPythonData]]],
    fixed_address: Optional[Address] = None,
) -> None:
    msg = "expected calls not fulfilled:"
    any_addresses_present = False
    for address, details in expected_calls.items():
        if fixed_address is not None and address != fixed_address:
            continue
        any_addresses_present = True
        msg += f"{os.linesep}  - for address {address}:"
        for details_item in details:
            msg += f"{os.linesep}    - function name: {details_item[0]}, calldata: {details_item[1]}"
    if any_addresses_present:
        raise CheaterException(msg)


class ExpectsCheater(StatefulCheater):
    async def expect_call(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> Callable:
        cairo_calldata = await transform_calldata_to_cairo_data(
            contract_class=await self.cheatable_state.get_contract_class_by_address(
                contract_address=contract_address
            ),
            function_name=function_name,
            calldata=calldata,
        )

        self.cheatable_state.register_expected_call(
            contract_address=contract_address,
            function_selector=get_selector_from_name(function_name),
            calldata=cairo_calldata,
        )

        def stop_callback():
            assert_no_expected_calls(
                expected_calls=self.cheatable_state.expected_contract_calls,
                fixed_address=contract_address,
            )

        return stop_callback
