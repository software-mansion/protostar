import asyncio
from dataclasses import dataclass
from typing import Any, Callable, List

from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.business_logic.execution.objects import CallType
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import CONSTRUCTOR_ENTRY_POINT_SELECTOR
from starkware.starknet.services.api.contract_class import EntryPointType

from protostar.starknet import CheatcodeException
from protostar.starknet.data_transformer import (
    DataTransformerException,
    to_python_transformer,
)
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode

from protostar.testing.cairo_cheatcodes.prepare_cairo_cheatcode import (
    PreparedContract,
)


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


class DeployCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "deploy"

    def build(self) -> Callable[[Any], Any]:
        return self.deploy_prepared

    def deploy_prepared(
        self,
        prepared: PreparedContract,
    ):
        asyncio.run(
            self.cheatable_state.deploy_contract(
                contract_address=int(prepared.contract_address),
                class_hash=to_bytes(prepared.class_hash),
            )
        )

        contract_class = asyncio.run(
            self.cheatable_state.get_contract_class(
                class_hash=to_bytes(prepared.class_hash)
            )
        )

        has_constructor = len(
            contract_class.entry_points_by_type[EntryPointType.CONSTRUCTOR]
        )
        if has_constructor:
            asyncio.run(self.invoke_constructor(prepared))
        elif not has_constructor and prepared.constructor_calldata:
            raise CheatcodeException(
                self,
                "Tried to deploy a contract with constructor calldata, but no constructor was found.",
            )

        return DeployedContract(contract_address=prepared.contract_address)

    async def invoke_constructor(self, prepared: PreparedContract):
        await self.validate_constructor_args(prepared)
        await self.execute_constructor_entry_point(
            class_hash_bytes=to_bytes(prepared.class_hash),
            constructor_calldata=prepared.constructor_calldata,
            contract_address=int(prepared.contract_address),
        )

    async def validate_constructor_args(self, prepared: PreparedContract):
        contract_class = await self.cheatable_state.get_contract_class(
            to_bytes(prepared.class_hash)
        )

        if not contract_class.abi:
            raise CheatcodeException(
                self,
                f"Contract ABI (class_hash: {hex(prepared.class_hash)}) was not found. "
                "Unable to verify constructor arguments.",
            )

        transformer = to_python_transformer(contract_class.abi, "constructor", "inputs")
        try:
            transformer(prepared.constructor_calldata)
        except DataTransformerException as dt_exc:
            # starknet.py interprets this call as a cairo -> python transformation, so message has to be modified
            dt_exc.message = dt_exc.message.replace("Output", "Input")
            raise CheatcodeException(
                self,
                f"There was an error while parsing constructor arguments:\n{dt_exc.message}",
            ) from dt_exc

    async def execute_constructor_entry_point(
        self,
        class_hash_bytes: bytes,
        constructor_calldata: List[int],
        contract_address: int,
    ):
        await ExecuteEntryPoint.create(
            contract_address=contract_address,
            calldata=constructor_calldata,
            entry_point_selector=CONSTRUCTOR_ENTRY_POINT_SELECTOR,
            caller_address=0,
            entry_point_type=EntryPointType.CONSTRUCTOR,
            call_type=CallType.DELEGATE,
            class_hash=class_hash_bytes,
        ).execute_for_testing(
            state=self.cheatable_state,
            general_config=StarknetGeneralConfig(),
        )
