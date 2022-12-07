from textwrap import dedent

from protostar.starknet.selector import Selector

from .multicall_file_interpreter import interpret_multicall_file_content
from .multicall_structs import DeployCall, InvokeCall, Identifier


def test_parsing():
    file_content = dedent(
        """
        [[call]]
        id = "A"
        type = "deploy"
        class-hash = 0x20
        calldata = [3]

        [[call]]
        type = "invoke"
        contract-address = "$A"
        entrypoint-name = "increase_balance"
        calldata = [42]
    """
    )

    calls = interpret_multicall_file_content(file_content)

    assert isinstance(calls[0], DeployCall)
    assert calls[0].address_alias == Identifier("A")
    assert calls[0].class_hash == 0x20
    assert calls[0].calldata == [3]

    assert isinstance(calls[1], InvokeCall)
    assert calls[1].address == Identifier("A")
    assert calls[1].calldata == [42]
    assert calls[1].selector == Selector("increase_balance")
