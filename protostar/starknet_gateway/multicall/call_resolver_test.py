import pytest

from protostar.starknet import Address, Selector

from .call_resolver import CallResolver, UnknownNameException
from .multicall_structs import DeployCall, InvokeCall


async def test_resolving_deploy_and_invoke():
    resolver = CallResolver()

    resolved_calls = await resolver.resolve(
        [
            DeployCall(name="A", calldata=[1], class_hash=1),
            InvokeCall(address="A", calldata=[], selector=Selector("foo")),
            InvokeCall(address=Address(0), calldata=[], selector=Selector("bar")),
        ]
    )

    assert len(resolved_calls) == 3


async def test_resolving_calldata():
    resolver = CallResolver()

    resolved_calls = await resolver.resolve(
        [
            DeployCall(name="A", calldata=[1], class_hash=1),
            InvokeCall(address=Address(0), calldata=["A"], selector=Selector("foo")),
        ]
    )

    assert isinstance(resolved_calls[1].calldata[0], int)


async def test_raising_error_when_name_is_undefined():
    resolver = CallResolver()

    with pytest.raises(UnknownNameException):
        await resolver.resolve(
            [InvokeCall(address="A", calldata=[], selector=Selector("foo"))]
        )
