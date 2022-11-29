from starknet_py.net.account.account_client import merge_calls
from starknet_py.net.client_models import Call
from starknet_py.utils.data_transformer.execute_transformer import (
    execute_transformer_by_version as create_transformer,
)

from .multicall_protocols import ResolvedCall


class ResolvedCallsToCalldataConverter:
    def __init__(self) -> None:
        pass

    def convert(self, resolved_calls: list[ResolvedCall]) -> list[int]:
        calls = [
            Call(
                to_addr=int(call.address),
                selector=int(call.selector),
                calldata=call.calldata,
            )
            for call in resolved_calls
        ]
        calldata = merge_calls(calls)
        transformer = create_transformer(version=1)
        result = transformer.from_python(*calldata)
        return result[0]
