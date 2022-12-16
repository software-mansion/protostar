from typing import Optional, Protocol

from protostar.starknet import (
    HumanDataRepresentation,
    Address,
    Calldata,
    Selector,
    AbiType,
    CairoDataRepresentation,
)

from .structs import PayloadToAccountExecuteInvokeTx, TransactionSentResponse


class DataTransformerProtocol(Protocol):
    async def transform_entrypoint_input_to_cairo(
        self,
        calldata: Optional[Calldata],
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> CairoDataRepresentation:
        ...

    async def try_transforming_entrypoint_output_to_human(
        self,
        data: CairoDataRepresentation,
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> Optional[HumanDataRepresentation]:
        ...


class AccountManagerProtocol(Protocol):
    async def execute(
        self, payload: PayloadToAccountExecuteInvokeTx
    ) -> TransactionSentResponse:
        ...
