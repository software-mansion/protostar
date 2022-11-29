from protostar.starknet import Address

from .multicall_protocols import ResolvedCall
from .resolved_calls_to_calldata_converter import ResolvedCallsToCalldataConverter


def test_happy_case():
    converter = ResolvedCallsToCalldataConverter()
    resolved_calls = [
        ResolvedCall(
            address=Address(1),
            selector=2,
            calldata=[3, 4],
        ),
        ResolvedCall(
            address=Address(5),
            selector=6,
            calldata=[7, 8],
        ),
    ]

    calldata = converter.convert(resolved_calls)

    assert calldata == [2, 1, 2, 0, 2, 5, 6, 2, 2, 4, 3, 4, 7, 8]
