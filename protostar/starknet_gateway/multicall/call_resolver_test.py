import pytest

from protostar.starknet import Address, Selector

from .call_resolver import CallResolver, UnknownNameException
from .multicall_input import DeployCall, InvokeCall


async def test_resolving_deploy_and_invoke():
    resolver = CallResolver()

    result = await resolver.resolve(
        [
            DeployCall(name="A", calldata=[1], class_hash=1),
            InvokeCall(address="A", calldata=[], selector=Selector("foo")),
            InvokeCall(address=Address(0), calldata=[], selector=Selector("bar")),
        ]
    )

    assert len(result) == 3


async def test_raising_error_when_name_is_undefined():
    resolver = CallResolver()

    with pytest.raises(UnknownNameException):
        await resolver.resolve(
            [InvokeCall(address="A", calldata=[], selector=Selector("foo"))]
        )
