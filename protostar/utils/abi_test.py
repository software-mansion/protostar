import pytest
from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt
from starkware.starknet.compiler.compile import compile_starknet_codes
from starkware.starknet.public.abi import AbiType

from protostar.utils.abi import (
    get_function_parameters,
    has_function_parameters,
    AbiItemNotFoundException,
)


@pytest.fixture(name="abi", scope="module")
def abi_fixture() -> AbiType:
    code = """
%lang starknet

struct Point:
    member x : felt
    member y : felt
end

@external
func test_no_args():
    return ()
end

@external
func test_fuzz{syscall_ptr : felt*, range_check_ptr}(a, b : felt):
    return ()
end
"""
    abi = compile_starknet_codes([(code, "")]).abi
    assert abi is not None
    return abi


def test_has_function_parameters(abi: AbiType):
    assert not has_function_parameters(abi, "test_no_args")
    assert has_function_parameters(abi, "test_fuzz")


def test_has_function_parameters_raises_when_function_not_found(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        has_function_parameters(abi, "foobar")


def test_has_function_parameters_raises_when_asked_for_struct(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        has_function_parameters(abi, "Point")


def test_get_function_parameters(abi: AbiType):
    assert not get_function_parameters(abi, "test_no_args")

    # Order is important here.
    parameters = get_function_parameters(abi, "test_fuzz")
    assert list(parameters.items()) == [
        ("a", TypeFelt()),
        ("b", TypeFelt()),
    ]


def test_get_function_parameters_raises_when_function_not_found(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        get_function_parameters(abi, "foobar")


def test_get_function_parameters_raises_when_asked_for_struct(abi: AbiType):
    with pytest.raises(AbiItemNotFoundException):
        get_function_parameters(abi, "Point")
