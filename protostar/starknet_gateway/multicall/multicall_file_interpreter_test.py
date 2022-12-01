from textwrap import dedent

from .multicall_file_interpreter import interpret_multicall_file_content
from .multicall_structs import DeployCall, InvokeCall


def test_foo():
    file_content = dedent(
        """
        [[call]]
        id = "A"
        type = "deploy"
        class-hash = 0x123
        calldata = [1]

        [[call]]
        type = "invoke"
        contract-address = "$A"
        entrypoint-name = "increase_balance"
        calldata = [42]
    """
    )

    calls = interpret_multicall_file_content(file_content)

    assert isinstance(calls[0], DeployCall)
    assert calls[0].name == "A"
    assert calls[0].class_hash == 0x123
    assert calls[0].calldata == 1

    assert isinstance(calls[1], InvokeCall)
