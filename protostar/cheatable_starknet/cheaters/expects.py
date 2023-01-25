import os
from typing import Optional, Callable, TYPE_CHECKING

from starkware.starknet.public.abi import get_selector_from_name

from protostar.starknet import CheatcodeException
from protostar.starknet.cheater import CheaterException
from protostar.starknet.address import Address
from protostar.starknet.data_transformer import (
    CairoOrPythonData,
    transform_calldata_to_cairo_data,
    CairoData,
    DataTransformerException,
)
from protostar.starknet.types import SelectorType


if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatable_cached_state import CheatableCachedState


class ExpectsCheaterException(CheaterException):
    pass


class ExpectsCairoCheater:
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.cheatable_state = cheatable_state

    async def expect_call(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> Callable:
        contract_address_int = int(contract_address)
        try:
            cairo_calldata = await transform_calldata_to_cairo_data(
                contract_class=await self.cheatable_state.get_contract_class(
                    await self.cheatable_state.get_class_hash_at(
                        contract_address=contract_address_int
                    )
                ),
                function_name=function_name,
                calldata=calldata,
            )
        except DataTransformerException as e:
            raise ExpectsCheaterException(e.message) from e

        self.register_expected_call(
            contract_address=contract_address,
            function_selector=get_selector_from_name(function_name),
            calldata=cairo_calldata,
        )

        def stop_callback():
            try:
                ExpectsCairoCheater.assert_no_expected_calls(
                    expected_calls=self.cheatable_state.expected_contract_calls,
                    fixed_address=contract_address,
                )
            except ExpectsCheaterException as e:
                raise CheatcodeException("expect_call", e.message) from e

        return stop_callback

    def register_expected_call(
        self,
        contract_address: Address,
        function_selector: SelectorType,
        calldata: CairoData,
    ):
        if self.cheatable_state.expected_contract_calls.get(contract_address):
            self.cheatable_state.expected_contract_calls[contract_address].append(
                (function_selector, calldata)
            )
        else:
            self.cheatable_state.expected_contract_calls[contract_address] = [
                (function_selector, calldata)
            ]

    def unregister_expected_call(
        self,
        contract_address: Address,
        function_selector: SelectorType,
        calldata: CairoData,
    ):
        if contract_address not in self.cheatable_state.expected_contract_calls:
            return
        self.cheatable_state.expected_contract_calls[contract_address] = [
            (stored_function_name, stored_calldata)
            for (
                stored_function_name,
                stored_calldata,
            ) in self.cheatable_state.expected_contract_calls[contract_address]
            if stored_function_name != function_selector or stored_calldata != calldata
        ]
        if not self.cheatable_state.expected_contract_calls[contract_address]:
            del self.cheatable_state.expected_contract_calls[contract_address]

    @staticmethod
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
            raise ExpectsCheaterException(msg)
